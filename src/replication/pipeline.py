from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import load_config
from .experiments import run_figure1, run_figure2
from .plotting import write_figures
from .tables import (
    write_analytical_validation,
    write_paper_design_comparison,
    write_parameter_tables,
    write_results,
)
from .validation import run_jump_count_diagnostics, validate_model_config


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _package_versions() -> dict[str, str | None]:
    versions = {}
    for package in ("numpy", "pandas", "scipy", "matplotlib"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def _write_reproducibility_records(
    root: Path,
    config_path: Path,
    paper_path: Path,
    run_record: dict,
    append_log: bool = True,
) -> None:
    """Persist input/output hashes and append one concise run-log row."""
    reproduction_dir = root / "reproduction"
    reproduction_dir.mkdir(parents=True, exist_ok=True)
    source_files = sorted((root / "src" / "replication").glob("*.py"))
    test_files = sorted((root / "tests").glob("*.py"))
    script_files = sorted((root / "scripts").glob("*.py")) if (root / "scripts").exists() else []
    generated_roots = [root / "outputs" / "tables", root / "outputs" / "diagnostics"]
    if run_record["mode"] == "PAPER_REPLICATION":
        generated_roots.extend(
            [
                root / "data" / "processed",
                root / "outputs" / "figures",
                root / "outputs" / "validation",
            ]
        )
    elif run_record["mode"] == "DEBUG":
        generated_roots = [root / "outputs" / "debug"]
    generated_paths = [
        path
        for folder in generated_roots
        if folder.exists()
        for path in folder.rglob("*")
        if path.is_file()
    ]
    if run_record["mode"] == "PAPER_REPLICATION":
        generated_paths.extend(
            path
            for path in (root / "outputs").iterdir()
            if path.is_file() and path.suffix in {".md", ".tex"}
        )
    input_paths = [
        root / "pyproject.toml",
        root / "requirements.lock",
        root / "paper/reviewed_source.pdf",
    ]
    input_paths.extend(path for path in (root / "paper/specification").iterdir() if path.is_file())
    manifest = {
        "schema_version": 1,
        "run_id": run_record["started_at_utc"],
        "mode": run_record["mode"],
        "execution_date_local": datetime.now().astimezone().isoformat(),
        "python": sys.version,
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "packages": _package_versions(),
        "git_commit": _git_commit(root),
        "seed": run_record["seed"],
        "configuration_sha256": _sha256(config_path),
        "paper_sha256": _sha256(paper_path),
        "additional_input_sha256": {
            str(path.relative_to(root)): _sha256(path) for path in input_paths if path.exists()
        },
        "source_sha256": {
            str(path.relative_to(root)): _sha256(path)
            for path in [*source_files, *test_files, *script_files]
        },
        "generated_output_sha256": {
            str(path.relative_to(root)): _sha256(path) for path in sorted(generated_paths)
        },
        "outer_repetitions_by_model_pair": run_record["outer_repetitions_by_model_pair"],
        "result_rows": run_record.get("rows", 0),
        "runtime_seconds": run_record["runtime_seconds"],
        "limitations": run_record["limitations"],
    }
    manifest_name = {
        "VALIDATION": "validation_manifest.json",
        "DEBUG": "debug_manifest.json",
        "PAPER_REPLICATION": "reproducibility_manifest.json",
    }[run_record["mode"]]
    (reproduction_dir / manifest_name).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if not append_log:
        return
    log_path = reproduction_dir / "experiment_log.csv"
    fields = [
        "run_id",
        "mode",
        "started_at_utc",
        "finished_at_utc",
        "runtime_seconds",
        "seed",
        "rows",
        "git_commit",
        "notes",
    ]
    write_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "run_id": run_record["started_at_utc"],
                "mode": run_record["mode"],
                "started_at_utc": run_record["started_at_utc"],
                "finished_at_utc": run_record["finished_at_utc"],
                "runtime_seconds": run_record["runtime_seconds"],
                "seed": run_record["seed"],
                "rows": run_record.get("rows", 0),
                "git_commit": manifest["git_commit"] or "unavailable",
                "notes": f"Source/config/output hashes are in {manifest_name}",
            }
        )


def run(
    config_path: Path,
    root: Path,
    full: bool = False,
    mode: str | None = None,
) -> None:
    """Execute validation, debug, or explicitly approved paper-scale runs."""
    root = root.resolve()
    config_path = config_path if config_path.is_absolute() else root / config_path
    config = load_config(config_path)
    sim = config["simulation"]
    started_at = datetime.now(timezone.utc)
    validate_model_config(config)
    mode = mode or ("PAPER_REPLICATION" if full else "DEBUG")
    mode = mode.upper()
    if mode not in {"DEBUG", "VALIDATION", "PAPER_REPLICATION"}:
        raise ValueError("mode must be DEBUG, VALIDATION, or PAPER_REPLICATION")
    if full and mode != "PAPER_REPLICATION":
        raise ValueError("--full cannot be combined with a non-paper mode")
    sim["full_paper_counts"] = mode == "PAPER_REPLICATION"

    output_root = root / "outputs" / "debug" if mode == "DEBUG" else root / "outputs"
    data_dir = output_root / "data" if mode == "DEBUG" else root / "data" / "processed"
    table_dir = output_root / "tables"
    figure_dir = output_root / "figures"
    log_dir = output_root / "logs"
    diagnostics_dir = output_root / "diagnostics"
    validation_dir = output_root / "validation"
    for directory in (data_dir, table_dir, figure_dir, log_dir, diagnostics_dir, validation_dir):
        directory.mkdir(parents=True, exist_ok=True)

    write_parameter_tables(config, table_dir)
    write_paper_design_comparison(config, table_dir)
    validation_rows = write_analytical_validation(config, sim["seed"] + 2, table_dir)
    jump_diagnostics = run_jump_count_diagnostics(
        sim["seed"] + 3,
        sim["jump_rates"],
        config["models"]["mrjd"]["maturity"],
    )
    import pandas as pd

    pd.DataFrame(jump_diagnostics).to_csv(diagnostics_dir / "jump_count_strata.csv", index=False)
    if mode == "VALIDATION":
        run_record = _make_run_record(started_at, mode, sim, config, validation_rows, 0, root)
        (log_dir / "validation_metadata.json").write_text(
            json.dumps(run_record, indent=2), encoding="utf-8"
        )
        _write_reproducibility_records(root, config_path, root / "paper" / "main.pdf", run_record)
        print("Validation-only mode finished; no experiment figures were generated.", flush=True)
        return

    print("Running Figure 1 ratio sweeps...", flush=True)
    rows = run_figure1(config)
    print("Running Figure 2 path-count sweeps...", flush=True)
    rows.extend(run_figure2(config))
    write_results(rows, data_dir)
    write_figures(rows, figure_dir)
    run_record = _make_run_record(started_at, mode, sim, config, validation_rows, len(rows), root)
    (log_dir / "run_metadata.json").write_text(json.dumps(run_record, indent=2), encoding="utf-8")
    _write_reproducibility_records(root, config_path, root / "paper" / "main.pdf", run_record)
    print(
        f"Finished. Wrote {len(rows):,} replicate-method rows to {data_dir}; figures to {figure_dir}.",
        flush=True,
    )


def _make_run_record(started_at, mode, sim, config, validation_rows, row_count, root) -> dict:
    """Create a truthful run record shared by all execution modes."""
    finished_at = datetime.now(timezone.utc)
    return {
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "runtime_seconds": (finished_at - started_at).total_seconds(),
        "mode": mode,
        "python": platform.python_version(),
        "operating_system": platform.platform(),
        "cpu": {"processor": platform.processor(), "count": os.cpu_count()},
        "packages": _package_versions(),
        "git_commit": _git_commit(root),
        "seed": sim["seed"],
        "configured_debug_repetitions": {
            "ratio_sweep": sim["repetitions_fig1"],
            "path_sweep": sim["repetitions_fig23"],
        },
        "outer_repetitions_by_model_pair": {
            "pair1_merton": {
                "figure1": sim["paper_repetitions_pair1"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig1"],
                "figure2": sim["paper_repetitions_pair1"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig23"],
                "figure3": sim["paper_repetitions_pair1"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig1"],
            },
            "pair2_mrjd": {
                "figure1": sim["paper_repetitions_pair2"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig1"],
                "figure2": sim["paper_repetitions_pair2"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig23"],
                "figure3": sim["paper_repetitions_pair2"]
                if mode == "PAPER_REPLICATION"
                else sim["repetitions_fig1"],
            },
        },
        "full_paper_outer_repetition_counts": mode == "PAPER_REPLICATION",
        "rows": row_count,
        "simulation_settings": sim,
        "model_parameters": config["models"],
        "analytical_validation": validation_rows,
        "method": f"Jump-time partition; {sim.get('gradient_estimator', 'exhaustive')} MVD sums; Student-t critical values; plug-in noncentral-t power.",
        "replication_verified": False,
        "limitations": [
            "The paper does not provide the authors' random seed, executable source, or numeric curve series.",
            "Table 1 mu_J is overloaded; code currently maps it to mean log jump.",
            "The MRJD baseline follows plotted E[abs(J)]/sigma and preserves E[J]; the incompatible Section 4 signed-gap ratio is excluded. Authors' actual mapping remains unverified.",
            "Equation (8) supplies no numeric lambda^M; zero is used for the baseline.",
            "The twelve-observation payoff is a put in Example 4/panel heading but a call in the subfigure caption.",
            "The article does not specify exact MVD randomization details or t inference corrections for antithetic/stratified dependence.",
            "PAPER_REPLICATION specifies repetition counts; it does not establish numerical agreement with the paper.",
        ],
    }
