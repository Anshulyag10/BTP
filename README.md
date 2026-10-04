# Replication of Gradient Estimation Methods for Jump-Diffusion Option Pricing

## Overview

This repository contains a computational replication of the study:

**W. Volk-Makarewicz, S. Borovkova, and B. Heidergott (2022)**  
*Assessing the impact of jumps in an option pricing model: A gradient estimation approach*  
European Journal of Operational Research.  
DOI: [10.1016/j.ejor.2021.07.015](https://doi.org/10.1016/j.ejor.2021.07.015)

The objective of this project is to independently implement the stochastic models, gradient estimation methods, simulation experiments, statistical procedures, and figure-generation pipeline described in the paper, and to evaluate how closely the reproduced results agree with the published study.

The implementation is designed to be **reproducible, testable, and explicit about assumptions** where the source paper leaves details unspecified or contains internal inconsistencies.

---

## Project Objectives

The project focuses on the following objectives:

1. Implement the **GBM/Merton** and **Vasicek/Merton-Reduced-Jump-Diffusion (MRJD)** models used in the numerical study.
2. Implement the gradient estimation methods described in the paper, including the **single-replacement and pairwise cross-difference estimators**.
3. Reproduce the experimental parameter grids, option contracts, simulation settings, and statistical comparisons used for Figures 1–3.
4. Validate the implementation using independent analytical and numerical checks.
5. Document ambiguities in the source paper and make all adopted interpretations explicit.
6. Compare the regenerated results with the published figures and quantify remaining discrepancies.

---

## Methodology

### Stochastic Models

The implementation includes:

- **Geometric Brownian Motion (GBM)**
- **Merton Jump-Diffusion**
- **Vasicek model with Markovian/compound jump extensions (MRJD)**

The simulations explicitly model:

- Brownian motion
- Poisson jump arrivals
- Jump-size distributions
- Compensated jump dynamics
- Antithetic sampling
- Stratification of jump occurrence
- Observation-date based option payoffs

The option values are discounted to time zero according to the model specification.

### Gradient Estimation

The primary implementation uses an **exhaustive local-replacement construction** for the gradient estimators described in the paper.

The implementation supports:

- First-order singleton replacements
- Pairwise cross-differences
- GradTwo-type estimators
- Randomized interval selection as an alternative implementation

The exhaustive implementation is used as the principal baseline because it provides a direct enumeration of the local replacement terms required by the corresponding equations in the paper.

---

## Experimental Design

The experiments reproduce the main numerical study using the parameter grids specified by the paper.

### Model Pairs

| Pair | Model | Option |
|---|---|---|
| Pair 1 | GBM / Merton | Vanilla Call |
| Pair 2 | Vasicek / MRJD | Vanilla Put |
| Pair 2 | Vasicek / MRJD | Asian Call |
| Pair 2 | Vasicek / MRJD | Asian Put |

### Simulation Settings

The configuration includes the experiment grids, jump rates, path counts, number of outer repetitions, model parameters, and estimator selection.

The main paper-replication configuration uses:

- **500 repetitions** for Pair 1
- **300 repetitions** for Pair 2
- Path counts ranging from **64 to 16,384**
- Jump-rate values specified by the experimental design
- Fixed random seeds for reproducibility

All experiment parameters are centralized in:

```text
config/experiments.json
```

---

## Reproduced Figures

The implementation regenerates the three principal experimental figures.

### Figure 1

Comparison across the model-ratio grid:

- Median estimated power
- Relative difference in median price estimates

### Figure 2

Comparison across the number of paths:

- Empirical rejection frequency
- Median estimated power

### Figure 3

Comparison across the model-ratio grid:

- Mean estimated power
- Relative difference in mean price estimates

All curves are generated from simulation output rather than manually reproduced from the published figures.

Generated figures are stored under:

```text
outputs/figures/
```

---

## Validation and Verification

Several independent checks are included to ensure that the implementation is internally consistent.

### Model Validation

The project tests:

- Transition distributions
- Model moments
- Jump-count behavior
- Mixture-polynomial derivatives
- Zero-jump boundary behavior
- Closed-form option-price relationships

### Independent Pricing Checks

The repository contains independent analytical/numerical benchmarks for:

- Black–Scholes pricing
- Merton option pricing
- MRJD vanilla and Asian option pricing

These checks are intentionally separated from the simulation-based pricing pipeline.

### Statistical Validation

The statistical implementation is tested through controlled simulation experiments involving:

- Null distributions
- Alternative distributions
- Rejection probabilities
- Noncentral-t power calculations
- Plug-in power estimation

Validation outputs are stored under:

```text
outputs/validation/
```

---

## Interpretation of the Source Paper

A significant part of the replication work involved identifying and resolving ambiguities in the published specification.

Examples include:

- The interpretation of the MRJD ratio used on the plotted axis versus the corresponding textual definition.
- The interpretation of the jump-size parameter `mu_J`.
- The unspecified value of the diffusion market price of risk `lambda^M`.
- The interpretation of the twelve-observation Asian option.
- Details of the exact power-estimation procedure.
- Dependence introduced by antithetic and stratified simulation when applying the reported inference procedure.

Rather than silently choosing arbitrary values, these issues are explicitly documented in:

```text
paper/specification/
```

with the adopted assumptions and alternative interpretations recorded for reproducibility.

The main discussion of unresolved specification issues is provided in:

```text
paper/specification/inconsistency_resolution.md
```

and:

```text
reproduction/deviations_from_paper.md
```

---

## Reproducibility

The project is structured so that experiments can be regenerated from a clean environment.

### Environment Setup

```powershell
python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.lock

.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

### Run Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Run the Main Replication

```powershell
.\.venv\Scripts\python.exe -m replication.cli --mode PAPER_REPLICATION
```

### Run Validation

```powershell
.\.venv\Scripts\python.exe -m replication.cli --mode VALIDATION
```

Additional diagnostic and comparison scripts are available under:

```text
scripts/
```

A consolidated execution guide is provided in:

```text
reproduction/RUN_ALL.md
```

---

## Repository Structure

```text
BTP/
│
├── config/
│   └── experiments.json
│
├── data/
│   └── README.md
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── validation/
│
├── paper/
│   ├── reference_paper.pdf
│   └── specification/
│
├── reproduction/
│   ├── README.md
│   ├── REPRODUCTION_CHECKLIST.md
│   ├── RUN_ALL.md
│   ├── deviations_from_paper.md
│   └── paper_vs_replication.csv
│
├── scripts/
│
├── src/
│   └── replication/
│       ├── benchmarks.py
│       ├── cli.py
│       ├── config.py
│       ├── diagnostics.py
│       ├── estimators.py
│       ├── experiments.py
│       ├── models.py
│       ├── payoffs.py
│       ├── pipeline.py
│       ├── plotting.py
│       ├── random_streams.py
│       ├── statistics.py
│       ├── tables.py
│       └── validation.py
│
├── tests/
│
├── pyproject.toml
└── requirements.lock
```

---

## Results and Reproducibility Status

The repository contains the regenerated experimental results, validation checks, figures, and comparison tables produced by the implementation.

Because the original paper does not provide the authors' executable source code, random seeds, or numerical curve data, **exact numerical identity with every published curve cannot be assumed from the paper alone**.

Accordingly, the replication distinguishes between:

- results directly generated by the present implementation,
- independently validated quantities,
- approximate readings of published figures, and
- interpretations required where the paper does not fully specify the computational procedure.

This distinction is maintained throughout the repository to avoid presenting inferred values as original data.

---

## Data Provenance

The paper describes a simulation study rather than providing a conventional observation-level dataset.

Therefore:

- model parameters are specified in `config/experiments.json`,
- simulation paths are generated programmatically,
- processed summaries and final results are produced from the simulation pipeline,
- no proprietary or external observation-level dataset is required for the core replication.

---

## Academic Attribution

This project is a **research replication and independent implementation** based on the published work cited above.

The mathematical models, equations, experimental design, and reported methodology originate from the cited paper. The source paper is included only as reference material, while the simulation code, validation framework, experiment pipeline, and analysis in this repository constitute the implementation developed for this project.

Any interpretation or deviation from the published specification is explicitly documented rather than presented as part of the original work.

---

## Contribution Note

The Git history contains contributions from multiple project collaborators during development.

For formal academic assessment, individual responsibilities and contributions should be interpreted according to the contribution breakdown provided in the accompanying BTP report.

---

## Citation

If referring to the source methodology, please cite:

> Volk-Makarewicz, W., Borovkova, S., & Heidergott, B. (2022). *Assessing the impact of jumps in an option pricing model: A gradient estimation approach*. European Journal of Operational Research. https://doi.org/10.1016/j.ejor.2021.07.015

---

## Project Status

**Status: Replication implementation and validation completed with documented numerical/specification discrepancies.**

The repository prioritizes transparency and reproducibility: unresolved differences from the published results are explicitly reported rather than concealed.
