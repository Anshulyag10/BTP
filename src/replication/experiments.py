from __future__ import annotations

import numpy as np

from .estimators import estimate_once


def _repetitions(simulation: dict, case: dict, figure_key: str) -> int:
    """Use published outer counts by model pair in full mode."""
    if simulation.get("full_paper_counts", False):
        key = "paper_repetitions_pair1" if case["pair"] == "merton" else "paper_repetitions_pair2"
        return int(simulation[key])
    return int(simulation[figure_key])


def run_figure1(config: dict) -> list[dict]:
    """Run the ratio sweep underlying the paper's Figure 1 and Appendix Fig. 3."""
    sim = config["simulation"]
    rng = np.random.default_rng(sim["seed"])
    output = []
    for case in config["cases"]:
        model_cfg = {
            **config["models"][case["pair"]],
            "gradient_estimator": sim.get("gradient_estimator", "exhaustive"),
        }
        ratios = sim["merton_ratio_grid"] if case["pair"] == "merton" else sim["mrjd_ratio_grid"]
        n_paths = (
            sim["paths_vanilla_call_fig1"]
            if case["id"] == "gbm_merton_vanilla_call"
            else sim["paths_primary"]
        )
        for ratio in ratios:
            for rate in sim["jump_rates"]:
                print(f"Ratio sweep: {case['id']}, ratio={ratio:g}, lambda={rate:g}", flush=True)
                for replication in range(_repetitions(sim, case, "repetitions_fig1")):
                    estimates = estimate_once(
                        rng,
                        n_paths,
                        case,
                        model_cfg,
                        rate,
                        ratio,
                        sim["alpha"],
                        sim["t_test_relative_tolerance"],
                    )
                    for result in estimates:
                        output.append(
                            {
                                **result,
                                "figure": "fig1",
                                "case": case["id"],
                                "ratio": ratio,
                                "jump_rate": rate,
                                "path_count": n_paths,
                                "replication": replication,
                            }
                        )
    return output


def run_figure2(config: dict) -> list[dict]:
    """Run Figure 2's path-count sweep."""
    sim = config["simulation"]
    rng = np.random.default_rng(sim["seed"] + 1)
    output = []
    for case in config["cases"]:
        model_cfg = {
            **config["models"][case["pair"]],
            "gradient_estimator": sim.get("gradient_estimator", "exhaustive"),
        }
        ratio = sim.get("fixed_ratios", {"merton": 0.50, "mrjd": 0.33})[case["pair"]]
        for rate in sim["jump_rates"]:
            for n_paths in sim["path_counts"]:
                print(f"Path sweep: {case['id']}, paths={n_paths}, lambda={rate:g}", flush=True)
                for replication in range(_repetitions(sim, case, "repetitions_fig23")):
                    estimates = estimate_once(
                        rng,
                        n_paths,
                        case,
                        model_cfg,
                        rate,
                        ratio,
                        sim["alpha"],
                        sim["t_test_relative_tolerance"],
                    )
                    for result in estimates:
                        output.append(
                            {
                                **result,
                                "figure": "fig2",
                                "case": case["id"],
                                "ratio": ratio,
                                "jump_rate": rate,
                                "path_count": n_paths,
                                "replication": replication,
                            }
                        )
    return output
