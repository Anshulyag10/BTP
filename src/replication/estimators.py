from __future__ import annotations

from itertools import combinations

import numpy as np

from .models import (
    merton_base_paths,
    merton_interval_effects,
    mrjd_base_paths,
    mrjd_interval_effects,
    mrjd_scaled_means,
    sample_double_exponential_marks,
    sample_jump_times,
    sample_merton_marks,
)
from .payoffs import payoff
from .statistics import estimated_power, reject, t_statistic


def _expand_local_replacements(
    base_states: np.ndarray,
    effects: np.ndarray,
    payoff_fn,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate the zeroth, first, and pairwise Taylor path constructions."""
    n_paths, max_intervals, _ = effects.shape
    base = payoff_fn(base_states)
    single_values = np.empty((n_paths, max_intervals), dtype=float)
    for i in range(max_intervals):
        single_values[:, i] = payoff_fn(base_states + effects[:, i, :])

    grad_one = np.sum(single_values - base[:, None], axis=1)
    second_order = np.zeros(n_paths, dtype=float)
    for i, j in combinations(range(max_intervals), 2):
        both = payoff_fn(base_states + effects[:, i, :] + effects[:, j, :])
        second_order += both - single_values[:, i] - single_values[:, j] + base

    q_value = payoff_fn(base_states + effects.sum(axis=1))
    grad_two = grad_one + second_order
    return base, q_value, grad_one, grad_two


def _randomized_mvd_estimators(
    rng: np.random.Generator,
    base_states: np.ndarray,
    effects: np.ndarray,
    payoff_fn,
    interval_counts: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Estimate the first two Taylor terms with a randomly selected interval."""
    n_paths, max_intervals, _ = effects.shape
    interval_counts = np.asarray(interval_counts, dtype=np.int64)
    if interval_counts.shape != (n_paths,):
        raise ValueError("interval_counts must contain one count per path")
    if np.any(interval_counts < 1) or np.any(interval_counts > max_intervals):
        raise ValueError("Each path must have between 1 and max_intervals intervals")

    base = payoff_fn(base_states)
    q_value = payoff_fn(base_states + effects.sum(axis=1))

    path_indices = np.arange(n_paths)
    selected_intervals = rng.integers(0, interval_counts)
    selected_effects = effects[path_indices, selected_intervals, :]
    selected_values = payoff_fn(base_states + selected_effects)
    grad_one = interval_counts * (selected_values - base)

    pair_sum = np.zeros(n_paths, dtype=float)
    for other_interval in range(max_intervals):
        active = (other_interval < interval_counts) & (selected_intervals != other_interval)
        if not np.any(active):
            continue
        other_values = payoff_fn(base_states + effects[:, other_interval, :])
        both_values = payoff_fn(base_states + selected_effects + effects[:, other_interval, :])
        cross_difference = both_values - selected_values - other_values + base
        pair_sum += np.where(active, cross_difference, 0.0)

    grad_two = grad_one + 0.5 * interval_counts * pair_sum
    return base, q_value, grad_one, grad_two


def local_replacement_inputs(
    rng: np.random.Generator,
    n_paths: int,
    case: dict,
    model_cfg: dict,
    jump_rate: float,
    ratio: float,
):
    """Build shared paths and payoff inputs for either gradient construction."""
    maturity = model_cfg["maturity"]
    observation_times = np.linspace(maturity / case["observations"], maturity, case["observations"])
    jump_times = sample_jump_times(rng, n_paths, jump_rate, maturity)
    counts = np.fromiter((len(times) for times in jump_times), dtype=np.int64, count=n_paths)

    if case["pair"] == "merton":
        volatility = jump_rate / ratio if jump_rate > 0 else model_cfg["volatility"]
        marks = sample_merton_marks(
            rng, counts, model_cfg["mean_log_jump"], model_cfg["log_jump_sd"]
        )
        base_states = merton_base_paths(rng, n_paths, observation_times, model_cfg, volatility)
        effects = merton_interval_effects(
            jump_times, marks, observation_times, jump_rate, model_cfg
        )

        def payoff_fn(states: np.ndarray) -> np.ndarray:
            return payoff(np.exp(states), model_cfg["strike"], case["option"], case["style"])

    elif case["pair"] == "mrjd":
        beta_positive, beta_negative = mrjd_scaled_means(model_cfg, ratio, jump_rate=jump_rate)
        marks = sample_double_exponential_marks(
            rng,
            counts,
            beta_positive,
            beta_negative,
            model_cfg["positive_jump_probability"],
        )
        base_states = mrjd_base_paths(rng, n_paths, observation_times, model_cfg)
        effect_cfg = {**model_cfg, "beta_positive": beta_positive, "beta_negative": beta_negative}
        effects = mrjd_interval_effects(
            jump_times,
            marks,
            observation_times,
            jump_rate,
            effect_cfg,
            include_jump_compensation=model_cfg.get("include_jump_compensation", True),
        )

        def payoff_fn(states: np.ndarray) -> np.ndarray:
            return payoff(states, model_cfg["strike"], case["option"], case["style"])

    else:
        raise ValueError(f"Unsupported model pair: {case['pair']}")

    discount = np.exp(-model_cfg["rate"] * maturity)
    raw_payoff_fn = payoff_fn

    def discounted_payoff(states):
        return discount * raw_payoff_fn(states)

    return base_states, effects, discounted_payoff, counts + 1


def pathwise_estimators(
    rng: np.random.Generator,
    n_paths: int,
    case: dict,
    model_cfg: dict,
    jump_rate: float,
    ratio: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return P/Q payoffs and GradOne/GradTwo for one independent run."""
    base_states, effects, discounted_payoff, interval_counts = local_replacement_inputs(
        rng, n_paths, case, model_cfg, jump_rate, ratio
    )
    method = model_cfg.get("gradient_estimator", "exhaustive")
    if method == "exhaustive":
        return _expand_local_replacements(base_states, effects, discounted_payoff)
    if method == "randomized":
        return _randomized_mvd_estimators(
            rng, base_states, effects, discounted_payoff, interval_counts
        )
    raise ValueError(f"Unknown gradient estimator: {method}")


def estimate_once(
    rng: np.random.Generator,
    n_paths: int,
    case: dict,
    model_cfg: dict,
    jump_rate: float,
    ratio: float,
    alpha: float,
    tolerance: float,
) -> list[dict]:
    """Estimate paired prices, test statistics, rejection, and t-based power."""
    p, q, grad_one, grad_two = pathwise_estimators(rng, n_paths, case, model_cfg, jump_rate, ratio)
    paired_difference = q - p
    estimates = {"GradOne": grad_one, "GradTwo": grad_two, "t-Test CRN": paired_difference}
    p_price = float(np.mean(p))
    q_price = float(np.mean(q))
    results = []

    for method, values in estimates.items():
        statistic = t_statistic(values)
        shift = tolerance * p_price if method == "t-Test CRN" else 0.0
        power = estimated_power(values, alpha, shift=shift)
        results.append(
            {
                "method": method,
                "statistic": statistic,
                "rejected": reject(statistic, alpha, n_paths - 1),
                "power": power,
                "p_price": p_price,
                "q_price": q_price,
                "relative_difference": abs(q_price - p_price) / max(abs(p_price), 1e-12),
            }
        )
    return results
