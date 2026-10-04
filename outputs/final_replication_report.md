# Replication correction report

Run mode: PAPER_REPLICATION. Recorded simulation runtime: 485.60 seconds.
Estimator: exhaustive.
Raw method rows: 214,200. Summary rows: 612.

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
| a | 2.00 | 0.058 | 0.057702 |
| b | 0.67 | 0.800 | 0.080431 |
| c | 1.00 | 0.370 | 0.463874 |
| d | 0.67 | 5.200 | 0.260139 |

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
