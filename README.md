# Jump-diffusion gradient replication

Python implementation of Volk-Makarewicz, Borovkova, and Heidergott (2022),
*Assessing the impact of jumps in an option pricing model: A gradient estimation approach*,
[DOI](https://doi.org/10.1016/j.ejor.2021.07.015).

This part of the repository contains the simulation core: model samplers, gradient
estimators, inference statistics, experiment grids, and closed-form reference checks.
The execution pipeline, independent benchmarks, figures, and reports are added separately.

## Setup and tests

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate
pip install -r requirements.lock
pip install -e . --no-deps
python -m unittest discover -s tests -v
python scripts/03_check_inference.py
```

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

## Files

- `config/experiments.json`: model parameters, grids, counts, and estimator choice.
- `src/replication/models.py`, `random_streams.py`: jump-time partitions, marks, base paths, interval effects.
- `src/replication/payoffs.py`, `estimators.py`: option payoffs, pathwise and MVD gradient estimators.
- `src/replication/statistics.py`: t statistic, critical values, noncentral-t power.
- `src/replication/config.py`, `experiments.py`: configuration loading and the Figure 1/2 experiment runners.
- `src/replication/validation.py`: closed-form option prices and model moments used as references.
- `tests/test_replication.py`: unit tests for the above.
- `scripts/03_check_inference.py`: calibration check of the plug-in power calculation.
