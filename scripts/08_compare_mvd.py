from pathlib import Path

import numpy as np
import pandas as pd

from replication.config import load_config
from replication.diagnostics import conditional_randomized_moments
from replication.estimators import (
    _expand_local_replacements,
    _randomized_mvd_estimators,
    local_replacement_inputs,
)

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = load_config(ROOT / "config/experiments.json")
    rows = []
    for case_index, case in enumerate(config["cases"]):
        model = config["models"][case["pair"]]
        grid = config["simulation"][f"{case['pair']}_ratio_grid"]
        ratios = sorted({grid[0], grid[-1], config["simulation"]["fixed_ratios"][case["pair"]]})
        for rate_index, rate in enumerate(config["simulation"]["jump_rates"]):
            for ratio_index, ratio in enumerate(ratios):
                seed = (
                    config["simulation"]["seed"]
                    + 200000
                    + 100 * case_index
                    + 10 * rate_index
                    + ratio_index
                )
                rng = np.random.default_rng(seed)
                base, effects, payoff_fn, counts = local_replacement_inputs(
                    rng, 8192, case, model, rate, ratio
                )
                exact = _expand_local_replacements(base, effects, payoff_fn)
                random = _randomized_mvd_estimators(rng, base, effects, payoff_fn, counts)
                means, variances = conditional_randomized_moments(base, effects, payoff_fn, counts)
                for i in (0, 1):
                    np.testing.assert_array_equal(exact[i], random[i])
                for index, method in enumerate(("GradOne", "GradTwo")):
                    np.testing.assert_allclose(
                        means[:, index], exact[index + 2], rtol=1e-10, atol=1e-10
                    )
                    exact_variance = exact[index + 2].var()
                    extra_variance = variances[:, index].mean()
                    conditional_se = np.sqrt(variances[:, index].sum()) / len(counts)
                    residual = (random[index + 2] - exact[index + 2]).mean()
                    rows.append(
                        {
                            "case": case["id"],
                            "jump_rate": rate,
                            "ratio": ratio,
                            "method": method,
                            "paths": len(counts),
                            "seed": seed,
                            "exhaustive_mean": exact[index + 2].mean(),
                            "randomized_mean": random[index + 2].mean(),
                            "max_conditional_mean_error": np.max(
                                abs(means[:, index] - exact[index + 2])
                            ),
                            "exhaustive_path_variance": exact_variance,
                            "randomization_added_variance": extra_variance,
                            "randomized_mixture_variance": exact_variance + extra_variance,
                            "conditional_residual_se": conditional_se,
                            "residual_z": residual / conditional_se
                            if conditional_se > 1e-15
                            else 0.0,
                            "status": "PASS_EXACT_CONDITIONAL_EXPECTATION",
                        }
                    )
    output = ROOT / "outputs/diagnostics/specification_resolution/mvd_comparison.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output, index=False)
    print(
        f"Verified identical P/Q payoffs and conditional MVD expectations for {len(frame)} method settings."
    )
    print("Largest conditional mean error:", frame["max_conditional_mean_error"].max())
    print("Largest absolute conditional residual z:", frame["residual_z"].abs().max())


if __name__ == "__main__":
    run()
