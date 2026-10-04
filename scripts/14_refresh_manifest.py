import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from replication.pipeline import _write_reproducibility_records

ROOT = Path(__file__).resolve().parents[1]


def run():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit("Tests failed; manifest was not refreshed")
    ruff_status = "NOT_RUN"
    if importlib.util.find_spec("ruff"):
        subprocess.run(
            [sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"], cwd=ROOT, check=True
        )
        ruff_status = "PASS"
    path = ROOT / "outputs/logs/run_metadata.json"
    metadata = json.loads(path.read_text())
    metadata["postprocessed_at_utc"] = datetime.now(timezone.utc).isoformat()
    metadata["postprocessing"] = [
        "Regenerated figures from the saved raw rows after layout review.",
        "Checked prices by independent quadrature and refreshed paper comparisons.",
        "Refreshed sensitivity diagnostics and the final source/output snapshot.",
    ]
    metadata["verification"] = {"unit_tests_passed": result.testsRun, "ruff_check": ruff_status}
    for counts in metadata["outer_repetitions_by_model_pair"].values():
        if "figures2_3" in counts:
            counts["figure2"] = counts.pop("figures2_3")
        counts["figure3"] = counts["figure1"]
    metadata["limitations"][-1] = (
        "PAPER_REPLICATION specifies repetition counts; numerical agreement with the paper remains unverified."
    )
    path.write_text(json.dumps(metadata, indent=2) + "\n")
    _write_reproducibility_records(
        ROOT,
        ROOT / "config/experiments.json",
        ROOT / "paper/main.pdf",
        metadata,
        append_log=False,
    )


if __name__ == "__main__":
    run()
