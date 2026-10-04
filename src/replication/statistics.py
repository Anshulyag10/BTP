from __future__ import annotations

import math

import numpy as np
from scipy.stats import nct, t


def t_statistic(samples: np.ndarray) -> float:
    """Return the one-sample t statistic, including the constant-sample case."""
    values = np.asarray(samples, dtype=float)
    if values.size < 2:
        return 0.0
    sd = float(np.std(values, ddof=1))
    mean = float(np.mean(values))
    if sd == 0.0:
        return math.copysign(math.inf, mean) if mean else 0.0
    return mean / (sd / math.sqrt(values.size))


def critical_value(alpha: float, degrees_of_freedom: int) -> float:
    """Exact two-sided Student-t critical value."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between zero and one")
    if degrees_of_freedom < 1:
        raise ValueError("degrees_of_freedom must be positive")
    return float(t.ppf(1.0 - alpha / 2.0, degrees_of_freedom))


def reject(statistic: float, alpha: float, df: int) -> bool:
    """Apply the paper's two-sided finite-df Student-t decision rule."""
    return abs(statistic) > critical_value(alpha, df)


def noncentral_t_power(noncentrality: float, alpha: float, df: int) -> float:
    """Two-sided power from the noncentral Student-t distribution."""
    cutoff = critical_value(alpha, df)
    if math.isnan(noncentrality):
        return float("nan")
    if math.isinf(noncentrality):
        return 1.0
    probability = nct.cdf(-cutoff, df, noncentrality) + nct.sf(cutoff, df, noncentrality)
    return float(np.clip(probability, 0.0, 1.0))


def estimated_power(samples: np.ndarray, alpha: float, shift: float = 0.0) -> float:
    """Estimate noncentral-t power using the sample's alternative t statistic."""
    values = np.asarray(samples, dtype=float) - shift
    return noncentral_t_power(t_statistic(values), alpha, max(1, values.size - 1))
