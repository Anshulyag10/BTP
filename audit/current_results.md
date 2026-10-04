# Current Results Audit

## Saved run

The final saved run is a reproducible DEBUG run, not the paper-scale experiment:

- Seed: `20260930` (replication choice; not stated in the paper).
- Replications: 4 per setting for both pairs and all three figures.
- `full_paper_outer_repetition_counts`: false.
- Rows: 2,448 (three methods per experiment); summary rows: 612.
- Every case in Figures 1-3 has four unique outer replication indices.
- Figure 2 rejection probabilities therefore lie on the grid `{0, .25, .50, .75, 1}`; the saved CSV confirms this.
- Six stored analytical checks are marked PASS; source test suite passes 17/17 tests.
- Final run metadata records DEBUG mode, 173.88 seconds, Python/package/environment details, and hashes for 18 generated outputs and 18 source/test/script files. Git revision is unavailable because the checkout has no `.git` directory.
- A controlled MRJD interpretation run wrote 12,420 method rows (12 outer repetitions, 256 paths per estimate) across nine executable variants; the literal signed prose ratio was recorded as unmappable.

The four-repetition files must not be labelled final paper results. The current CLI's `--full` chooses 500 replications for Pair 1 and 300 for Pair 2, but that run has not been performed and should remain gated on resolving the estimator/sweep questions.

## Current Figure 1 price-difference maxima

Computed from `simulation_summary.csv`, using the saved medians of P and Q prices and deduplicating the three repeated method rows:

| Panel/case | lambda | Maximum relative difference in median estimates | Ratio at maximum |
|---|---:|---:|---:|
| (a) GBM/Merton call | 0.01 | 0.052110 | 2.00 |
| (b) Vasicek/MRJD vanilla put | 0.70 | 0.166304 | 1.00 |
| (c) MRJD Asian call, 4 observations | 0.70 | 0.493713 | 1.00 |
| (d) MRJD Asian put, 12 observations | 0.70 | 0.463548 | 1.00 |

Visual reads from the source raster of Figure 1 (paper p.747) put panel (a) near 0.058, panel (b) near 1.2, panel (c) near 0.38, and panel (d) near 5.8. These are approximate graph readings, not tabulated paper values. The compared replication maxima are 0.052110, 0.166304, 0.493713, and 0.463548, respectively. Panel (a) is close in scale; b/d are materially lower; c is the same order but not numerically aligned. See the comparison CSV for approximate errors and caveats.

## Analytical validation

The current output reports six PASS rows at 100,000 paths: GBM call/Black-Scholes, Merton call/Poisson mixture, Vasicek terminal mean/variance, and compensated MRJD terminal mean/variance. These checks support selected model laws; they do not validate the randomized MVD distribution/variance, t inference under dependent sampling, or the paper's plotted numerical curves.

