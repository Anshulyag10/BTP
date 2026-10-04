import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

METHODS = ("GradOne", "GradTwo", "t-Test CRN")
CASE_TITLES = {
    "gbm_merton_vanilla_call": "GBM Model vs. Merton Model, Vanilla Call Option",
    "vasicek_mrjd_vanilla_put": "Vasicek Model vs. MRJD Model, Vanilla Put Option",
    "vasicek_mrjd_asian_call_4": "Vasicek Model vs. MRJD Model, Asian Call Option, 4 observations",
    "vasicek_mrjd_asian_put_12": "Vasicek Model vs. MRJD Model, Asian Put Option, 12 observations",
}
METHOD_COLORS = {
    "GradOne": ("#9ad5ab", "#59b978", "#237b46"),
    "GradTwo": ("#a5c6df", "#699fd0", "#355f9d"),
    "t-Test CRN": ("#ffe4a3", "#ffd06a", "#efb341"),
}
PRICE_COLORS = ("#f9beac", "#f38c73", "#e45d3a")


def _axes():
    fig, axes = plt.subplots(4, 2, figsize=(12.4, 12.6))
    fig.subplots_adjust(left=0.07, right=0.83, bottom=0.06, top=0.95, hspace=0.76, wspace=0.85)
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=7)
        ax.grid(True, color="#eeeeee", linewidth=0.4)
    return fig, axes


def _label(ax, title, xlabel, ylabel, grid):
    ax.set_title(title, fontsize=7, weight="bold", loc="left", pad=9)
    ax.set_xlabel(xlabel, fontsize=7)
    ax.set_ylabel(ylabel, fontsize=7)
    ax.set_xticks(np.arange(len(grid)), [f"{x:.2f}" for x in grid], rotation=45)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=5.6,
        frameon=False,
        title="Stat. Test",
        title_fontsize=6,
    )


def _method_curves(ax, subset, coordinate, metric, aggregation, grid):
    for method in METHODS:
        for rate_index, rate in enumerate(sorted(subset["jump_rate"].unique())):
            curve = subset[(subset["method"] == method) & (subset["jump_rate"] == rate)]
            values = curve.groupby(coordinate)[metric].agg(aggregation).reindex(grid)
            ax.plot(
                np.arange(len(grid)),
                values,
                color=METHOD_COLORS[method][rate_index],
                marker="x",
                markersize=3,
                linewidth=0.8,
                label=rf"{method}, $\lambda={rate:g}$",
            )
    ax.set_ylim(0, 1.02)


def _plot_ratio_figure(frame: pd.DataFrame, path: Path, aggregation="median"):
    fig, axes = _axes()
    statistic = aggregation.capitalize()
    for index, (case_id, title) in enumerate(CASE_TITLES.items()):
        row, column = divmod(index, 2)
        upper, lower = axes[2 * row, column], axes[2 * row + 1, column]
        subset = frame[frame["case"] == case_id]
        grid = sorted(subset["ratio"].unique())
        _method_curves(upper, subset, "ratio", "power", aggregation, grid)
        prices = subset.drop_duplicates(["ratio", "jump_rate", "replication", "path_count"])
        for rate_index, rate in enumerate(sorted(subset["jump_rate"].unique())):
            values = (
                prices[prices["jump_rate"] == rate]
                .groupby("ratio")[["p_price", "q_price"]]
                .agg(aggregation)
                .reindex(grid)
            )
            relative = (values["q_price"] - values["p_price"]).abs() / values["p_price"].abs().clip(
                lower=1e-12
            )
            lower.plot(
                np.arange(len(grid)),
                relative,
                color=PRICE_COLORS[rate_index],
                marker="x",
                markersize=3,
                linewidth=0.8,
                label=rf"$\lambda={rate:g}$",
            )
        count = int(subset["path_count"].iloc[0])
        option = title.split(", ", 1)[1]
        model_pair = title.split(", ", 1)[0]
        xlabel = (
            r"Jump Rate/Spot Volatility, $\lambda/\sigma$"
            if case_id.startswith("gbm")
            else r"Mean Abs. Jump Amplitude/Spot Volatility, $E[|J|]/\sigma$"
        )
        heading = (
            f"Hypothesis Tests: {statistic} Power Estimate to Option Value Difference.\n"
            f"{option}. {count} Paths/Estimate.\n{model_pair}. Two-sided Test."
        )
        _label(upper, heading, xlabel, "Power", grid)
        _label(lower, "", xlabel, f"Rel. Diff. {statistic} Estimate", grid)
        lower.set_ylim(bottom=0)
        lower.get_legend().set_title("Jump Rate")
        lower.text(
            0,
            -0.35,
            textwrap.fill(f"({chr(97 + index)}) {title}", 60),
            transform=lower.transAxes,
            fontsize=8,
            va="top",
        )
    _save(fig, path)


def _plot_path_sweep(frame: pd.DataFrame, path: Path):
    fig, axes = _axes()
    for index, (case_id, title) in enumerate(CASE_TITLES.items()):
        row, column = divmod(index, 2)
        upper, lower = axes[2 * row, column], axes[2 * row + 1, column]
        subset = frame[frame["case"] == case_id]
        grid = sorted(subset["path_count"].unique())
        ratio = float(subset["ratio"].iloc[0])
        _method_curves(upper, subset, "path_count", "rejected", "mean", grid)
        _method_curves(lower, subset, "path_count", "power", "median", grid)
        heading = (
            f"Hypothesis Tests: Probability of Rejection to Median Power Estimate.\n"
            f"{title.split(', ', 1)[1]}. Ratio = {ratio:g}.\nTwo-sided Test."
        )
        _label(upper, heading, "No. Paths/Estimate", "Prob. Rejection", grid)
        _label(lower, "", "No. Paths/Estimate", "Power", grid)
        labels = [rf"$2^{{{int(np.log2(n))}}}$" for n in grid]
        for ax in (upper, lower):
            ax.set_xticklabels(labels, rotation=0)
        lower.text(
            0,
            -0.29,
            textwrap.fill(f"({chr(97 + index)}) {title}", 60),
            transform=lower.transAxes,
            fontsize=8,
            va="top",
        )
    _save(fig, path)


def _save(fig, path):
    fig.savefig(path.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def write_figures(rows: list[dict], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    ratios = frame[frame["figure"] == "fig1"]
    paths = frame[frame["figure"].isin(["fig2", "fig23"])]
    _plot_ratio_figure(ratios, output_dir / "figure1_median_power")
    _plot_path_sweep(paths, output_dir / "figure2_rejection_and_median_power")
    _plot_ratio_figure(ratios, output_dir / "figure3_mean_power", aggregation="mean")
