# Jump-diffusion gradient replication

Python implementation of Volk-Makarewicz, Borovkova, and Heidergott (2022),
*Assessing the impact of jumps in an option pricing model: A gradient estimation approach*,
[DOI](https://doi.org/10.1016/j.ejor.2021.07.015).

The aim is a checked replication baseline for subsequent research. The experiment grids
and figure definitions now follow the paper. Numerical agreement with all published curves
is not yet established; see `outputs/final_replication_report.md`.

## Setup and execution

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m replication.cli --mode DEBUG
.\.venv\Scripts\python.exe -m replication.cli --mode PAPER_REPLICATION
.\.venv\Scripts\python.exe scripts/02_check_price_curves.py
.\.venv\Scripts\python.exe scripts/03_check_inference.py
.\.venv\Scripts\python.exe scripts/07_resolve_specification.py
.\.venv\Scripts\python.exe scripts/08_compare_mvd.py
.\.venv\Scripts\python.exe scripts/13_compare_with_paper.py
```

`DEBUG` uses four repetitions per setting. `PAPER_REPLICATION` uses 500 for GBM/Merton
and 300 for Vasicek/MRJD. The mode specifies sample counts; it does not certify agreement.
`VALIDATION` runs the model checks without generating experiment figures. DEBUG results
are isolated under `outputs/debug/`, with `reproduction/debug_manifest.json`; they cannot
overwrite full-run results. Configuration fields containing four repetitions apply to DEBUG only.

## Models and estimators

GBM/Merton use log prices and normal log-jump marks. Vasicek/MRJD use exact OU transitions
and signed exponential marks. Positive/negative jump probabilities are one half, and beta
parameters are mean magnitudes. All option outputs are discounted to time zero.

Each path has a Poisson jump-time partition. Observation dates determine the payoff,
not the gradient intervals. Brownian noise and jump times use antithetics, jump occurrence
is stratified, and marks are independent across paths.

The default `simulation.gradient_estimator="exhaustive"` evaluates all singleton and
pairwise local replacements from Eqs. (15), (18), and (19). GradTwo is the first-order sum
plus unordered pair cross-differences. `"randomized"` retains the legacy uniform-interval
estimator as a research alternative; equal expectations do not imply equal variances.
The optional weighting reconstruction was informed by the authors'
[2018 presentation](https://www.researchgate.net/publication/350193285_When_do_Jumps_Matter_in_Option_Prices).

Tests use an independently enumerated mixture polynomial, direct compensated transitions,
closed-form model moments, option prices, and conditional jump-time distributions.
`benchmarks.py` prices MRJD vanilla and arithmetic Asian options independently by
characteristic-function quadrature, without simulating jump paths.

## Figure definitions

| Figure | Horizontal axis | Upper plots | Lower plots |
|---|---|---|---|
| 1 | Model ratio | Median estimated power | Relative difference of median price estimates |
| 2 | Paths per estimate | Empirical rejection frequency | Median estimated power |
| 3 | Same ratio grid as Figure 1 | Mean estimated power | Relative difference of mean price estimates |

Figures 1 and 3 share the ratio-sweep data. Figure 2 has its own path-count sweep.
Prices are deduplicated across the three method rows before aggregation. Plot ticks,
method colors, legends, panel arrangement, and displayed path counts follow the source
more closely; every curve comes from generated data.

## Remaining interpretations

- MRJD figure axes show `E|J|/sigma`, but Section 4 gives `lambda/(beta+ - beta-)`.
  The revised baseline follows the axes and preserves `E[J]=-1.03` and equal sign probabilities,
  reconciling the unchanged-mean statement. With `a=ratio*sigma`, it solves
  `beta+=(a+E[J])/(2p)` and `beta-=(a-E[J])/(2(1-p))`. This requires `a>|E[J]|`.
  The ratio interpretation is mandatory in `models.mrjd.ratio_interpretation`.
  The previous proportional mapping and other readings remain explicit diagnostics.
- The Table 1 `mu_J` value is interpreted as a log-jump mean, although the text also uses
  that symbol for a drift. MRJD's unspecified `lambda^M` is set to zero.
- The twelve-date option follows the Asian put formula and panel headings; captions say call.
- Remark 1 says gradients vanish on no-jump paths, while the Q drift adjustment gives
  a nonzero singleton replacement. The baseline keeps the compensated kernel equations.
- The paper does not give the authors' exact power-estimation algorithm. The inherited
  plug-in noncentral-t calculation is explicit, and its calibration limitations are measured.
  Path-level `n-1` inference follows the reported convention despite dependent sampling.

The source supplies neither original code/seeds nor numerical curve arrays. Approximate
paper readings are labelled as such; they are never substituted for simulated results.
The complete evidence and decisions are in `paper/specification/inconsistency_resolution.md`.
The supplied PDF has the same page text and figure images as the original project copy.

## Files

- `config/experiments.json`: model parameters, grids, counts, and estimator choice.
- `src/replication/`: simulation, gradients, inference, benchmarks, exports, and plots.
- `data/processed/`: raw replicate rows and summaries.
- `outputs/figures/`: regenerated PNG/PDF figures.
- `outputs/validation/`: independent price checks, inference calibration, paper comparisons.
- `reproduction/`: hashes, environment, seed conventions, and experiment log.
- `reproduction/legacy_baseline/`: preserved simulation source and previous DEBUG outputs.
- `reproduction/before_specification_resolution.zip`: previous proportional-mapping full run and source.
- `outputs/diagnostics/specification_resolution/`: all parameter moments, independent price alternatives,
  and conditional exhaustive/randomized MVD checks.
- `paper/specification/`: transcriptions of the supplied paper.
- `audit/`: historical audit of the original implementation; consult the new report for current status.
