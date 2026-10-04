import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from replication.benchmarks import mrjd_option_price
from replication.config import load_config
from replication.models import mrjd_jump_moments, mrjd_scaled_means

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/diagnostics/specification_resolution"
VARIANTS = {
    "axis_fixed_signed_mean": "mean_absolute_jump_over_volatility_fixed_mean",
    "axis_fixed_asymmetry": "mean_absolute_jump_over_volatility",
    "table_beta_as_rates": "beta_table_values_are_rates",
    "absolute_beta_gap": "lambda_over_absolute_beta_gap",
    "fixed_marks_vary_sigma": None,
}


def run():
    config = load_config(ROOT / "config/experiments.json")
    model = config["models"]["mrjd"]
    cases = [case for case in config["cases"] if case["pair"] == "mrjd"]
    cases.append({**cases[-1], "id": "vasicek_mrjd_asian_call_12", "option": "call"})
    parameters, prices = [], []
    for variant, mode in VARIANTS.items():
        for rate in config["simulation"]["jump_rates"]:
            for ratio in config["simulation"]["mrjd_ratio_grid"]:
                scenario = {**model}
                if mode is None:
                    scenario["volatility"] = mrjd_jump_moments(model)["jump_absolute_mean"] / ratio
                else:
                    scenario["ratio_interpretation"] = mode
                    plus, minus = mrjd_scaled_means(scenario, ratio, rate)
                    scenario.update(beta_positive=plus, beta_negative=minus)
                moments = mrjd_jump_moments(scenario)
                record = {
                    "variant": variant,
                    "nominal_ratio": ratio,
                    "jump_rate": rate,
                    "spot": scenario["spot"],
                    "strike": scenario["strike"],
                    "maturity": scenario["maturity"],
                    "mean_reversion": scenario["mean_reversion"],
                    "long_run_mean": scenario["long_run_mean"],
                    "expected_jump_count": rate * scenario["maturity"],
                    "volatility": scenario["volatility"],
                    "beta_positive_mean": scenario["beta_positive"],
                    "beta_negative_mean": scenario["beta_negative"],
                    "positive_probability": scenario["positive_jump_probability"],
                    "diffusion_market_price_of_risk": scenario["diffusion_market_price_of_risk"],
                    **moments,
                    "actual_axis_ratio": moments["jump_absolute_mean"] / scenario["volatility"],
                }
                parameters.append(record)
                for case in cases:
                    p = mrjd_option_price(scenario, case, include_diffusion_risk_adjustment=False)
                    q = mrjd_option_price(scenario, case, rate)
                    count = case["observations"]
                    times = np.linspace(scenario["maturity"] / count, scenario["maturity"], count)
                    kernel_average = (
                        np.mean(-np.expm1(-scenario["mean_reversion"] * times))
                        / scenario["mean_reversion"]
                    )
                    bound = (
                        rate
                        * (moments["jump_absolute_mean"] + abs(moments["jump_mean"]))
                        * kernel_average
                    )
                    bound *= np.exp(-scenario["rate"] * scenario["maturity"])
                    if abs(q - p) > bound + 1e-8:
                        raise AssertionError(
                            "Price difference exceeds the compensated Lipschitz bound"
                        )
                    prices.append(
                        {
                            **record,
                            "case": case["id"],
                            "option": case["option"],
                            "observations": case["observations"],
                            "p_price": p,
                            "q_price": q,
                            "relative_difference": abs(q - p) / abs(p),
                            "expected_price_difference_upper_bound": bound,
                            "relative_expected_difference_upper_bound": bound / abs(p),
                        }
                    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(parameters).to_csv(OUTPUT / "parameter_grid.csv", index=False)
    frame = pd.DataFrame(prices)
    frame.to_csv(OUTPUT / "direct_prices.csv", index=False)
    decisions = {
        "baseline": "axis_fixed_signed_mean",
        "basis": "Figure axis plus the p.747 statement that signed mean and sign probability stay fixed.",
        "signed_beta_gap": "Unmappable: positive intensity divided by negative Table-2 beta gap is negative.",
        "author_presentation_mapping": "Unspecified: no unique executable mapping is supplied.",
        "contract_12": "Put baseline from Example 4 and panel heading; call sensitivity retained.",
        "price_method": "Characteristic-function quadrature: expected prices, not medians of noisy estimates.",
        "reference_status": "No variant is selected by visual fit to the published curves.",
    }
    (OUTPUT / "decisions.json").write_text(json.dumps(decisions, indent=2) + "\n")
    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    for axis, case in zip(axes.flat, cases, strict=True):
        subset = frame[(frame["case"] == case["id"]) & (frame["jump_rate"] == 0.70)]
        for variant in VARIANTS:
            curve = subset[subset["variant"] == variant]
            axis.plot(
                curve["nominal_ratio"],
                curve["relative_difference"],
                "o-",
                markersize=3,
                label=variant.replace("_", " "),
            )
        axis.set_title(f"{case['style'].title()} {case['option']}, {case['observations']} dates")
        axis.set_xlabel("Nominal analysis ratio (interpretation varies)")
        axis.set_ylabel("Relative difference of expected prices")
        axis.grid(alpha=0.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside lower center", ncol=2, fontsize=9)
    figure.suptitle("MRJD specification sensitivities: independent prices, jump intensity 0.70")
    figure.savefig(OUTPUT / "price_sensitivities.png", dpi=160)
    figure.savefig(OUTPUT / "price_sensitivities.pdf")
    plt.close(figure)
    print(f"Wrote {len(parameters)} parameter settings and {len(prices)} direct-price checks.")
    print(
        frame[
            (frame["variant"] == "axis_fixed_signed_mean")
            & (frame["jump_rate"] == 0.7)
            & frame["nominal_ratio"].isin([0.67, 1.0])
        ][["case", "nominal_ratio", "p_price", "q_price", "relative_difference"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    run()
