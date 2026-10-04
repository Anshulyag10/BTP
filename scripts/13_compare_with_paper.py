import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def run():
    summary = pd.read_csv(ROOT / "data/processed/simulation_summary.csv")
    reference = pd.read_csv(ROOT / "paper/specification/figure_reference.csv")
    curves = summary[summary["figure"] == "fig1"].drop_duplicates(["case", "ratio", "jump_rate"])
    comparison = reference.merge(curves, on=["case", "jump_rate", "ratio"], validate="one_to_one")
    comparison["replicated_value"] = comparison["relative_difference_in_median_estimates"]
    comparison["abs_error"] = abs(comparison["paper_value"] - comparison["replicated_value"])
    comparison["relative_error"] = comparison["abs_error"] / comparison["paper_value"]
    comparison["status"] = "UNVERIFIED_APPROXIMATE_REFERENCE"
    comparison["figure"] = "Figure 1"
    comparison.to_csv(ROOT / "outputs/validation/figure_comparison.csv", index=False)

    benchmarks_path = ROOT / "outputs/validation/price_benchmarks.csv"
    if benchmarks_path.exists():
        benchmark = pd.read_csv(benchmarks_path)
        checked = curves.merge(benchmark, on=["case", "jump_rate", "ratio"], validate="one_to_one")
        checked["p_mean_error"] = checked["mean_p_price"] - checked["p_analytic"]
        checked["q_mean_error"] = checked["mean_q_price"] - checked["q_analytic"]
        checked.to_csv(ROOT / "outputs/validation/simulation_vs_analytic_prices.csv", index=False)

    metadata = json.loads((ROOT / "outputs/logs/run_metadata.json").read_text())
    report = f"""# Replication correction report

Run mode: {metadata["mode"]}. Recorded simulation runtime: {metadata["runtime_seconds"]:.2f} seconds.
Estimator: {metadata["simulation_settings"].get("gradient_estimator", "exhaustive")}.
Raw method rows: {metadata["rows"]:,}. Summary rows: {len(summary):,}.

## Implemented corrections

- Figure 3 uses Figure 1's ratio sweep with mean aggregation, rather than Figure 2's path-count sweep.
- Exhaustive local first- and second-order sums are the baseline; randomized selection remains optional.
- Discounting is applied to all simulated prices and gradients.
- Vectorized arrival sampling and interval effects retain the model laws and remove expensive nested loops.
- Figure styling follows the paper's arrangement, categorical ratio ticks, method colors, and external legends.
- Verbose code comments were removed or reduced to short function descriptions.
- Independent characteristic-function prices check all MRJD monitoring grids.
- MRJD beta means now preserve the signed mean jump while satisfying the plotted absolute-mean ratio.
- The ratio interpretation is mandatory in the experiment configuration.
- DEBUG output is isolated under outputs/debug/ and cannot replace the full-run data or manifest.
- The legacy simulation and DEBUG outputs are preserved in reproduction/legacy_baseline/.

## Figure 1 comparison

Paper values below are approximate visual readings from the supplied paper, not numerical source data.

| Panel | Ratio | Paper reading | Current relative median difference |
|---|---:|---:|---:|
"""
    for row in comparison.itertuples():
        report += f"| {row.panel} | {row.ratio:.2f} | {row.paper_value:.3f} | {row.replicated_value:.6f} |\n"
    report += """
## Unresolved differences

The regenerated figures do not yet reproduce all published curves. Increasing repetitions removes
the four-run sampling limitation, but cannot resolve conflicting parameter definitions or an
unspecified power algorithm. Independent quadrature agrees with the simulated MRJD prices under
the current mapping. The remaining MRJD price discrepancy is not fixed by changing the gradient estimator.

The baseline reconciles the plotted E|J|/sigma ratio with the unchanged signed-mean statement.
It follows the normalized beta-as-mean density, the Asian-put formula and panel heading,
zero unspecified diffusion risk premium, and path-level n-1 t inference. The prose signed-gap
ratio, no-jump gradient remark, and call captions conflict with those choices.
The decisions and remaining limits are in paper/specification/inconsistency_resolution.md.

The earlier visual references also needed correction: panel b at ratio 1 is clipped, so the
comparison now uses its visible ratio-0.67 point; panel d at ratio 0.67 is about 5.2, not 5.8.
No approximate raster reading is treated as exact author data.

The plug-in power calculation is not a calibrated empirical rejection frequency. The independent
inference diagnostic measures its bias under a known null. See outputs/validation/inference_calibration.csv.

Status: paper-count simulation and corrected figure design; numerical replication remains unverified.
"""
    (ROOT / "outputs/final_replication_report.md").write_text(report, encoding="utf-8")
    print(
        comparison[["panel", "paper_value", "replicated_value", "relative_error"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    run()
