# Current Implementation Inventory

## Scope Inspected

Inspected the project on 2026-10-01 (Asia/Kolkata): source under `src/replication/`, tests, config, scripts, READMEs, generated CSV/JSON and figures, the root PDF, and the supplied 12-page paper copied to `paper/main.pdf`. No `.git` directory or ZIP archive is present. The root `figure1_median_power.pdf` is a separate one-page Matplotlib artifact, not the paper figure and not produced by the active pipeline.

## Active Layout

```text
audit/                         # implementation, result, figure and paper comparison audits
config/experiments.json        # parameters, cases, seed, grids and readiness gate
data/processed/                # final DEBUG replicate and summary CSVs
outputs/figures/               # generated Figures 1-3, PNG and PDF
outputs/tables/                # parameter, validation and paper-design CSVs
outputs/logs/run_metadata.json # mode, counts, environment, checks and limitations
outputs/diagnostics/           # jump-count and MRJD interpretation sensitivity outputs
outputs/validation/            # approximate paper-vs-replication comparison CSV
paper/specification/           # equation/model/experiment/ambiguity specifications
reproduction/                  # run record, manifest, deviations and commands
scripts/                       # validation, MRJD diagnostic, full-mode and compare scripts
src/replication/               # simulator, estimators, inference, plots and pipeline
tests/test_replication.py      # 17 automated tests
```

## Module Map

| Module | Responsibility | Current assessment |
|---|---|---|
| `models.py` | Poisson jump-time partitions, marks, P paths, local Q-P effects and theta-mixture helper | Actual jump times; Brownian/time antithetics and event stratification; marks iid across paths. Analytical model checks pass, full transition-law validation remains incomplete. |
| `estimators.py` | Exhaustive Taylor oracle and randomized weighted GradOne/GradTwo; CRN comparator | Uniformly selects one of `N+1` intervals; weights single term by `N+1`, selected-pair sum by `(N+1)/2`. Toy expectation tests pass; estimator variance/distribution is not verified against authors. |
| `payoffs.py` | Vanilla and arithmetic-Asian call/put | Formula structure matches examples; 12-date baseline follows put formula/in-panel title despite caption conflict. |
| `statistics.py` | Paired statistic, Student-t critical value, noncentral-t power | Exact critical quantile; power and standard-error construction are reconstructed; path dependence is not corrected. |
| `experiments.py` | Figure 1 ratio sweep and Figures 2/3 path sweeps | DEBUG run uses four reps; configured full mode chooses 500/300 by model pair but remains gated. |
| `plotting.py` | Figures 1-3 | Reproduces broad organization, not exact paper typography or numerics. |
| `validation.py` | Closed-form checks and jump-count diagnostics | Six analytical checks pass, including MRJD mean and variance; no exact MVD variance or t-calibration proof. |
| `tables.py` | CSV exports | CSV tables exist; paper numeric curve tables cannot be generated from unavailable source data. |
| `pipeline.py` | Run modes, output, metadata, reproducibility manifest | Current final DEBUG run records hashes of source/config/paper/generated outputs and runtime environment. No Git revision exists in this checkout. |

## Final Run Provenance

The latest saved pipeline run is the DEBUG run recorded in `outputs/logs/run_metadata.json`: seed `20260930`; Python 3.12.14; Windows 11; 12 logical CPUs; NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1, Matplotlib 3.11.2; 173.88 seconds; 2,448 method rows and 612 summary rows; four repetitions per pair/figure. `reproduction/reproducibility_manifest.json` records hashes for 18 source/test/script files and 18 generated outputs, plus config and paper hashes. It records `git_commit: null` because no `.git` directory is available.

The current figures are fresh for the current implementation, but are small diagnostic outputs rather than paper-scale results. A separate MRJD sensitivity run wrote 12,420 method rows across nine executable interpretations and one unmappable literal signed-ratio interpretation. Diagnostics do not resolve the paper inconsistency or reproduce panel (d).
