from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .models import mrjd_scaled_means


def load_config(path: Path) -> dict[str, Any]:
    """Read a configuration file and catch the most common setup mistakes."""
    with path.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    if not 0 < config["simulation"]["alpha"] < 1:
        raise ValueError("simulation.alpha must be strictly between zero and one")
    if not config.get("cases"):
        raise ValueError("At least one experiment case is required")
    sim = config["simulation"]
    for key in (
        "paths_primary",
        "paths_vanilla_call_fig1",
        "repetitions_fig1",
        "repetitions_fig23",
        "paper_repetitions_pair1",
        "paper_repetitions_pair2",
    ):
        value = sim[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"simulation.{key} must be a positive integer")
    if sim["paths_primary"] < 2 or sim["paths_vanilla_call_fig1"] < 2:
        raise ValueError("Student-t estimates require at least two paths")
    if any(not isinstance(n, int) or isinstance(n, bool) or n < 2 for n in sim["path_counts"]):
        raise ValueError("path_counts must contain integers of at least two")
    for key in ("jump_rates", "merton_ratio_grid", "mrjd_ratio_grid"):
        if not sim[key] or any(not math.isfinite(x) or x <= 0 for x in sim[key]):
            raise ValueError(f"simulation.{key} must contain finite positive values")
    if sim.get("gradient_estimator", "exhaustive") not in {"exhaustive", "randomized"}:
        raise ValueError("gradient_estimator must be exhaustive or randomized")
    mrjd = config["models"]["mrjd"]
    if mrjd.get("beta_definition") != "mean_magnitude":
        raise ValueError("models.mrjd.beta_definition must be mean_magnitude")
    if "ratio_interpretation" not in mrjd:
        raise ValueError("models.mrjd.ratio_interpretation must be explicit")
    if not 0 < mrjd["positive_jump_probability"] < 1:
        raise ValueError("MRJD sign probability must lie strictly between zero and one")
    ratios = set(sim["mrjd_ratio_grid"]) | {sim["fixed_ratios"]["mrjd"]}
    for ratio in ratios:
        for rate in sim["jump_rates"]:
            mrjd_scaled_means(mrjd, ratio, rate)
    case_ids = [case["id"] for case in config["cases"]]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Case IDs must be unique")
    for case in config["cases"]:
        if case["pair"] not in {"merton", "mrjd"} or case["option"] not in {"call", "put"}:
            raise ValueError(f"Unsupported model/option in {case['id']}")
        if case["style"] not in {"vanilla", "asian"}:
            raise ValueError(f"Unsupported style in {case['id']}")
        if not isinstance(case["observations"], int) or case["observations"] < 1:
            raise ValueError("observations must be a positive integer")
    return config
