from __future__ import annotations

import copy
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from replication.config import load_config
from replication.estimators import estimate_once

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "diagnostics" / "mrjd_parameterization"
RATIOS = [0.20, 0.33, 0.50, 0.67, 1.00]
RATES = [0.01, 0.08, 0.70]
REPETITIONS = 12
PATH_COUNT = 256

CASES = [
    ("vasicek_mrjd_vanilla_put", "Vanilla put, 1 observation", "put", "vanilla", 1),
    ("vasicek_mrjd_asian_call_4", "Asian call, 4 observations", "call", "asian", 4),
    ("vasicek_mrjd_asian_put_12", "Asian put, 12 observations", "put", "asian", 12),
]

VARIANTS = [
    ("A_plotted_ratio", "Mean |J| / sigma; paper's plotted axis", {}, None),
    (
        "C_beta_as_rates",
        "Treat Table 2 beta values as exponential rates",
        {"ratio_interpretation": "beta_table_values_are_rates"},
        None,
    ),
    (
        "D_pi_plus_025",
        "Positive-jump probability 0.25 sensitivity",
        {"positive_jump_probability": 0.25},
        None,
    ),
    (
        "D_pi_plus_075",
        "Positive-jump probability 0.75 sensitivity",
        {"positive_jump_probability": 0.75},
        None,
    ),
    (
        "E_lambdaM_01",
        "Illustrative lambda^M=0.1 sensitivity",
        {"diffusion_market_price_of_risk": 0.1},
        None,
    ),
    (
        "E_no_jump_compensation",
        "Omit jump compensator ablation",
        {"include_jump_compensation": False},
        None,
    ),
    (
        "F_lambda_over_abs_gap",
        "Scale beta gap to lambda / |beta+ - beta-|",
        {"ratio_interpretation": "lambda_over_absolute_beta_gap"},
        None,
    ),
    (
        "G_12date_call",
        "12-date Asian call caption interpretation",
        {},
        ("vasicek_mrjd_asian_call_12_caption", "call", "asian", 12, "vasicek_mrjd_asian_call_4"),
    ),
    (
        "H_12date_put",
        "12-date Asian put Example-4 interpretation",
        {},
        ("vasicek_mrjd_asian_put_12", "put", "asian", 12, "vasicek_mrjd_asian_put_12"),
    ),
]


def run() -> None:
    config = load_config(ROOT / "config" / "experiments.json")
    base_model = {
        **config["models"]["mrjd"],
        "ratio_interpretation": "mean_absolute_jump_over_volatility",
    }
    sim = config["simulation"]
    alpha = sim["alpha"]
    tolerance = sim["t_test_relative_tolerance"]
    raw_rows: list[dict] = []
    register_rows = [
        {
            "variant": "B_literal_signed_gap",
            "interpretation": "lambda / (beta_positive - beta_negative), with positive plotted x values",
            "status": "UNMAPPABLE",
            "reason": "Table-2 beta_positive (3.48) is less than beta_negative (5.54); the literal ratio is negative and cannot produce the positive Figure 1 grid without an additional convention.",
        }
    ]

    for variant_index, (variant_id, label, overrides, special_case) in enumerate(VARIANTS):
        variant_model = copy.deepcopy(base_model)
        variant_model.update(overrides)
        for case_index, (case_id, case_label, option, style, observations) in enumerate(CASES):
            if special_case is not None:
                special_id, special_option, special_style, special_observations, source_case = (
                    special_case
                )
                if case_id != source_case:
                    continue
                case_id = special_id
                option, style, observations = special_option, special_style, special_observations
                case_label = (
                    "Asian call, 12 observations (caption alternative)"
                    if variant_id.startswith("G_")
                    else "Asian put, 12 observations (Example 4)"
                )

            case = {
                "id": case_id,
                "pair": "mrjd",
                "option": option,
                "style": style,
                "observations": observations,
            }
            for ratio_index, ratio in enumerate(RATIOS):
                for rate_index, rate in enumerate(RATES):
                    for replication in range(REPETITIONS):
                        seed = (
                            sim["seed"]
                            + 100000
                            + case_index * 10000
                            + ratio_index * 1000
                            + rate_index * 100
                            + replication
                        )
                        rng = np.random.default_rng(seed)
                        results = estimate_once(
                            rng,
                            PATH_COUNT,
                            case,
                            variant_model,
                            rate,
                            ratio,
                            alpha,
                            tolerance,
                        )
                        for result in results:
                            raw_rows.append(
                                {
                                    **result,
                                    "variant": variant_id,
                                    "variant_label": label,
                                    "case": case_id,
                                    "case_label": case_label,
                                    "ratio": ratio,
                                    "jump_rate": rate,
                                    "path_count": PATH_COUNT,
                                    "replication": replication,
                                }
                            )
        register_rows.append(
            {
                "variant": variant_id,
                "interpretation": label,
                "status": "RUN",
                "reason": "Diagnostic sensitivity only; no candidate is selected by visual similarity alone.",
            }
        )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    raw = pd.DataFrame(raw_rows)
    raw.to_csv(OUTPUT / "raw.csv", index=False)
    group_cols = ["variant", "variant_label", "case", "case_label", "ratio", "jump_rate", "method"]
    summary = (
        raw.groupby(group_cols)
        .agg(
            median_power=("power", "median"),
            mean_power=("power", "mean"),
            median_p_price=("p_price", "median"),
            median_q_price=("q_price", "median"),
            outer_repetitions=("power", "count"),
        )
        .reset_index()
    )
    summary["relative_difference_in_median_estimates"] = (
        summary["median_q_price"] - summary["median_p_price"]
    ).abs() / summary["median_p_price"].abs().clip(lower=1e-12)
    summary.to_csv(OUTPUT / "summary.csv", index=False)
    pd.DataFrame(register_rows).to_csv(OUTPUT / "variant_register.csv", index=False)
    write_diagnostic_figure(summary)
    print(f"Wrote {len(raw):,} method rows to {OUTPUT}")


def write_diagnostic_figure(summary: pd.DataFrame) -> None:
    """Plot high-jump-rate price differences and GradTwo median power."""
    variants = [item[0] for item in VARIANTS]
    colors = plt.get_cmap("tab10").colors
    fig, axes = plt.subplots(3, 2, figsize=(13, 10), constrained_layout=True)
    for row_index, (case_id, case_label, _, _, _) in enumerate(CASES):
        case_ids = [case_id]
        if case_id == "vasicek_mrjd_asian_put_12":
            case_ids.append("vasicek_mrjd_asian_call_12_caption")
        panel = summary[
            summary["case"].isin(case_ids)
            & (summary["jump_rate"] == 0.70)
            & (summary["method"] == "GradTwo")
        ]
        for variant_index, variant_id in enumerate(variants):
            series = panel[panel["variant"] == variant_id].sort_values("ratio")
            if series.empty:
                continue
            label = series["variant_label"].iloc[0]
            axes[row_index, 0].plot(
                series["ratio"],
                series["relative_difference_in_median_estimates"],
                marker="o",
                linewidth=1.2,
                markersize=3,
                color=colors[variant_index % len(colors)],
                label=label,
            )
            axes[row_index, 1].plot(
                series["ratio"],
                series["median_power"],
                marker="o",
                linewidth=1.2,
                markersize=3,
                color=colors[variant_index % len(colors)],
                label=label,
            )
        axes[row_index, 0].set_title(f"{case_label}: relative median price difference")
        axes[row_index, 1].set_title(f"{case_label}: GradTwo median estimated power")
        for ax in axes[row_index]:
            ax.set_xlabel("Nominal Figure 1 ratio grid")
            ax.grid(True, linewidth=0.5, alpha=0.55)
        axes[row_index, 0].set_ylabel("Relative difference")
        axes[row_index, 1].set_ylabel("Power")
        axes[row_index, 1].set_ylim(0, 1.03)
    handles, labels = [], []
    for ax in axes.flat:
        axis_handles, axis_labels = ax.get_legend_handles_labels()
        for handle, label in zip(axis_handles, axis_labels):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(handles, labels, loc="outside lower center", ncol=3, fontsize=7, frameon=False)
    fig.suptitle("MRJD interpretation sensitivity (diagnostic only; lambda=0.70)")
    fig.savefig(OUTPUT / "diagnostic_figure1.png", dpi=180, bbox_inches="tight")
    fig.savefig(OUTPUT / "diagnostic_figure1.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    run()
