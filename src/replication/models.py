from __future__ import annotations

import math

import numpy as np

from .random_streams import antithetic_normal, antithetic_uniform


class JumpTimes(list):
    def __init__(self, padded: np.ndarray, counts: np.ndarray):
        super().__init__(padded[i, :count] for i, count in enumerate(counts))
        self.padded = padded
        self.counts = counts


def sample_jump_times(
    rng: np.random.Generator, n_paths: int, jump_rate: float, maturity: float
) -> list[np.ndarray]:
    """Stratify jump occurrence, then sample antithetic exponential gaps."""
    if n_paths < 1 or jump_rate < 0 or maturity <= 0:
        raise ValueError("Require positive paths/maturity and nonnegative jump rate")
    if jump_rate == 0:
        return JumpTimes(np.empty((n_paths, 0)), np.zeros(n_paths, dtype=int))
    half = (n_paths + 1) // 2
    paired = n_paths - half
    probability_any = -math.expm1(-jump_rate * maturity)
    strata = (np.arange(half) + rng.random(half)) / n_paths
    occurrence = np.concatenate((strata, 1.0 - strata[:paired])) < probability_any
    first = antithetic_uniform(rng, (n_paths,))
    times = -np.log1p(-first * probability_any) / jump_rate
    times = np.where(occurrence, times, np.inf)
    columns = []
    while np.any(times < maturity):
        columns.append(np.where(times < maturity, times, np.inf))
        uniforms = antithetic_uniform(rng, (n_paths,))
        times += -np.log(np.maximum(uniforms, np.finfo(float).tiny)) / jump_rate
    padded = np.column_stack(columns) if columns else np.empty((n_paths, 0))
    return JumpTimes(padded, np.isfinite(padded).sum(axis=1))


def _interval_arrays(jump_times, marks, maturity):
    counts = np.fromiter((len(times) for times in jump_times), dtype=int)
    maximum = int(counts.max(initial=0))
    if isinstance(jump_times, JumpTimes):
        padded = jump_times.padded
    else:
        padded = np.full((len(jump_times), maximum), np.inf)
        for i, times in enumerate(jump_times):
            padded[i, : len(times)] = times
    ends = np.full((len(jump_times), maximum + 1), maturity)
    ends[:, :maximum] = np.minimum(padded, maturity)
    starts = np.column_stack((np.zeros(len(jump_times)), ends[:, :-1]))
    active = np.arange(maximum + 1)[None, :] <= counts[:, None]
    jumps = np.zeros_like(ends)
    jumps[:, :maximum] = np.where(
        np.arange(maximum)[None, :] < counts[:, None], marks[:, :maximum], 0.0
    )
    return starts[:, :, None], ends[:, :, None], jumps[:, :, None], active[:, :, None]


def sample_merton_marks(
    rng: np.random.Generator,
    counts: np.ndarray,
    mean_log_jump: float,
    log_jump_sd: float,
) -> np.ndarray:
    """Draw independent normal log-jump marks, padded to the batch maximum."""
    maximum = int(counts.max(initial=0))
    if maximum == 0:
        return np.zeros((len(counts), 0), dtype=float)
    z = rng.standard_normal((len(counts), maximum))
    return mean_log_jump + log_jump_sd * z


def sample_double_exponential_marks(
    rng: np.random.Generator,
    counts: np.ndarray,
    beta_positive: float,
    beta_negative: float,
    positive_probability: float,
) -> np.ndarray:
    """Draw signed double-exponential marks using the published mean sizes."""
    if beta_positive <= 0 or beta_negative <= 0:
        raise ValueError("Double-exponential mean jump sizes must be positive")
    if not 0.0 < positive_probability < 1.0:
        raise ValueError("positive_probability must be strictly between zero and one")
    maximum = int(counts.max(initial=0))
    if maximum == 0:
        return np.zeros((len(counts), 0), dtype=float)

    u = rng.random((len(counts), maximum))
    positive = u < positive_probability
    positive_tail = np.maximum(1.0 - u / positive_probability, np.finfo(float).tiny)
    negative_tail = np.maximum((1.0 - u) / (1.0 - positive_probability), np.finfo(float).tiny)
    return np.where(
        positive,
        -beta_positive * np.log(positive_tail),
        beta_negative * np.log(negative_tail),
    )


def merton_base_paths(
    rng: np.random.Generator,
    n_paths: int,
    observation_times: np.ndarray,
    cfg: dict,
    volatility: float,
) -> np.ndarray:
    """Simulate the GBM baseline log-price with antithetic Brownian increments."""
    dt = np.diff(np.concatenate(([0.0], observation_times)))
    z = antithetic_normal(rng, (n_paths, len(observation_times)))
    increments = (cfg["rate"] - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * z
    return np.cumsum(increments, axis=1) + math.log(cfg["spot"])


def mrjd_base_paths(
    rng: np.random.Generator,
    n_paths: int,
    observation_times: np.ndarray,
    cfg: dict,
) -> np.ndarray:
    """Simulate the Vasicek baseline using exact OU transitions."""
    kappa = cfg["mean_reversion"]
    previous_times = np.concatenate(([0.0], observation_times[:-1]))
    dt = observation_times - previous_times
    decay = np.exp(-kappa * dt)
    scale = cfg["volatility"] * np.sqrt((1.0 - decay**2) / (2.0 * kappa))
    z = antithetic_normal(rng, (n_paths, len(observation_times)))

    states = np.empty((n_paths, len(observation_times)), dtype=float)
    state = np.full(n_paths, cfg["spot"], dtype=float)
    for j in range(len(observation_times)):
        state = (
            cfg["long_run_mean"] + (state - cfg["long_run_mean"]) * decay[j] + scale[j] * z[:, j]
        )
        states[:, j] = state
    return states


def merton_interval_effects(
    jump_times: list[np.ndarray],
    marks: np.ndarray,
    observation_times: np.ndarray,
    jump_rate: float,
    cfg: dict,
) -> np.ndarray:
    """Log-price changes from each local Q replacement."""
    starts, ends, jumps, active = _interval_arrays(jump_times, marks, cfg["maturity"])
    observations = observation_times[None, None, :]
    elapsed = np.clip(observations - starts, 0.0, ends - starts)
    gamma = jump_rate * math.expm1(cfg["mean_log_jump"] + 0.5 * cfg["log_jump_sd"] ** 2)
    return np.where(active, -gamma * elapsed + jumps * (observations >= ends), 0.0)


def mrjd_interval_effects(
    jump_times: list[np.ndarray],
    marks: np.ndarray,
    observation_times: np.ndarray,
    jump_rate: float,
    cfg: dict,
    include_jump_compensation: bool = True,
) -> np.ndarray:
    """OU level changes from local drift adjustments and decaying jumps."""
    starts, ends, jumps, active = _interval_arrays(jump_times, marks, cfg["maturity"])
    observations = observation_times[None, None, :]
    kappa = cfg["mean_reversion"]
    expected_jump = (
        cfg["positive_jump_probability"] * cfg["beta_positive"]
        - (1.0 - cfg["positive_jump_probability"]) * cfg["beta_negative"]
    )
    mean_shift = -cfg.get("diffusion_market_price_of_risk", 0.0) * cfg["volatility"]
    if include_jump_compensation:
        mean_shift -= jump_rate * expected_jump / kappa
    elapsed = np.clip(observations - starts, 0.0, ends - starts)
    partial = mean_shift * -np.expm1(-kappa * elapsed)
    full = mean_shift * -np.expm1(-kappa * (ends - starts)) + jumps
    after = full * np.exp(-kappa * np.maximum(observations - ends, 0.0))
    return np.where(active, np.where(observations < ends, partial, after), 0.0)


def mrjd_scaled_means(
    cfg: dict, analysis_ratio: float, jump_rate: float | None = None
) -> tuple[float, float]:
    """Map a ratio to beta means under an explicitly selected interpretation."""
    if analysis_ratio <= 0 or cfg["volatility"] <= 0:
        raise ValueError("MRJD plotted ratio requires positive volatility and ratio")
    mode = cfg["ratio_interpretation"]
    beta_positive = cfg["beta_positive"]
    beta_negative = cfg["beta_negative"]
    probability = cfg["positive_jump_probability"]

    if mode == "mean_absolute_jump_over_volatility_fixed_mean":
        signed_mean = probability * beta_positive - (1.0 - probability) * beta_negative
        target_absolute_mean = analysis_ratio * cfg["volatility"]
        if target_absolute_mean <= abs(signed_mean):
            raise ValueError("Fixed-mean ratio requires ratio * volatility > abs(E[J])")
        return (
            (target_absolute_mean + signed_mean) / (2.0 * probability),
            (target_absolute_mean - signed_mean) / (2.0 * (1.0 - probability)),
        )
    if mode == "beta_table_values_are_rates":
        beta_positive = 1.0 / beta_positive
        beta_negative = 1.0 / beta_negative
    elif mode == "lambda_over_signed_beta_gap":
        raise ValueError(
            "lambda/(beta_positive-beta_negative) is negative for the Table-2 ordering; "
            "it cannot equal a positive plotted ratio without another convention"
        )
    elif mode == "lambda_over_absolute_beta_gap":
        if jump_rate is None:
            raise ValueError("The prose-ratio interpretation requires jump_rate")
        base_gap = abs(beta_positive - beta_negative)
        if base_gap == 0:
            raise ValueError("The base beta gap must be nonzero")
        scale = (jump_rate / analysis_ratio) / base_gap
        return beta_positive * scale, beta_negative * scale
    elif mode != "mean_absolute_jump_over_volatility":
        raise ValueError(f"Unknown MRJD ratio interpretation: {mode}")

    mean_absolute_jump = probability * beta_positive + (1.0 - probability) * beta_negative
    scale = analysis_ratio * cfg["volatility"] / mean_absolute_jump
    return beta_positive * scale, beta_negative * scale


def mrjd_jump_moments(cfg: dict) -> dict[str, float]:
    """Moments of the signed exponential mark, with beta measured as a mean."""
    probability = cfg["positive_jump_probability"]
    plus, minus = cfg["beta_positive"], cfg["beta_negative"]
    mean = probability * plus - (1.0 - probability) * minus
    second = 2.0 * (probability * plus**2 + (1.0 - probability) * minus**2)
    return {
        "jump_mean": mean,
        "jump_absolute_mean": probability * plus + (1.0 - probability) * minus,
        "jump_second_moment": second,
        "jump_variance": second - mean**2,
    }


def mix_transition_samples(
    rng: np.random.Generator,
    p_samples: np.ndarray,
    q_samples: np.ndarray,
    theta: float,
) -> np.ndarray:
    """Sample the convex mixture `(1-theta)P + theta Q` row by row."""
    p_values = np.asarray(p_samples)
    q_values = np.asarray(q_samples)
    if p_values.shape != q_values.shape or p_values.ndim == 0:
        raise ValueError("P and Q samples must have the same non-scalar shape")
    if not 0.0 <= theta <= 1.0:
        raise ValueError("theta must lie in [0, 1]")
    if theta == 0.0:
        return p_values.copy()
    if theta == 1.0:
        return q_values.copy()
    choose_q = rng.random(p_values.shape[0]) < theta
    return np.where(choose_q.reshape((-1,) + (1,) * (p_values.ndim - 1)), q_values, p_values)
