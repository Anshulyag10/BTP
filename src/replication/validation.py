from __future__ import annotations

import math

import numpy as np
from scipy.special import ndtr
from scipy.stats import poisson

from .models import (
    merton_base_paths,
    mrjd_base_paths,
    mrjd_interval_effects,
    mrjd_scaled_means,
    sample_double_exponential_marks,
    sample_jump_times,
)
from .payoffs import payoff


def black_scholes_call(
    spot: float, strike: float, maturity: float, rate: float, volatility: float
) -> float:
    """Closed-form European call value under geometric Brownian motion."""
    if maturity <= 0:
        return max(spot - strike, 0.0)
    if volatility <= 0:
        return max(spot - strike * math.exp(-rate * maturity), 0.0)
    root_t = math.sqrt(maturity)
    d1 = (math.log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / (volatility * root_t)
    d2 = d1 - volatility * root_t
    return spot * ndtr(d1) - strike * math.exp(-rate * maturity) * ndtr(d2)


def merton_call(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
    jump_rate: float,
    mean_log_jump: float,
    log_jump_sd: float,
    tail_probability: float = 1e-12,
) -> float:
    """Merton European call price from its Poisson mixture representation."""
    if jump_rate <= 0 or maturity <= 0:
        return black_scholes_call(spot, strike, maturity, rate, volatility)

    mean_relative_jump = math.expm1(mean_log_jump + 0.5 * log_jump_sd**2)
    compensator = jump_rate * mean_relative_jump
    poisson_mean = jump_rate * maturity
    max_count = int(poisson.ppf(1.0 - tail_probability, poisson_mean))
    max_count = max(max_count, 0)
    log_strike = math.log(strike)
    value = 0.0

    for count in range(max_count + 1):
        weight = float(poisson.pmf(count, poisson_mean))
        log_mean = (
            math.log(spot)
            + (rate - 0.5 * volatility**2 - compensator) * maturity
            + count * mean_log_jump
        )
        variance = volatility**2 * maturity + count * log_jump_sd**2
        if variance <= 0:
            conditional_call = max(math.exp(log_mean) - strike, 0.0)
        else:
            root_variance = math.sqrt(variance)
            d2 = (log_mean - log_strike) / root_variance
            d1 = d2 + root_variance
            conditional_call = math.exp(log_mean + 0.5 * variance) * ndtr(d1) - strike * ndtr(d2)
        value += weight * conditional_call
    return math.exp(-rate * maturity) * value


def vasicek_moments(
    initial: float, long_run_mean: float, kappa: float, volatility: float, maturity: float
) -> tuple[float, float]:
    """Exact mean and variance of the Vasicek/OU level at maturity."""
    decay = math.exp(-kappa * maturity)
    mean = long_run_mean + (initial - long_run_mean) * decay
    variance = volatility**2 * (1.0 - decay**2) / (2.0 * kappa)
    return mean, variance


def mrjd_expected_level(
    initial: float,
    long_run_mean: float,
    kappa: float,
    maturity: float,
    diffusion_market_price_of_risk: float = 0.0,
    volatility: float = 0.0,
) -> float:
    """Risk-neutral MRJD mean after jump and diffusion-risk adjustments."""
    adjusted_mean = long_run_mean - diffusion_market_price_of_risk * volatility
    return adjusted_mean + (initial - adjusted_mean) * math.exp(-kappa * maturity)


def mrjd_moments(
    initial: float,
    long_run_mean: float,
    kappa: float,
    volatility: float,
    maturity: float,
    jump_rate: float,
    beta_positive: float,
    beta_negative: float,
    positive_jump_probability: float,
    diffusion_market_price_of_risk: float = 0.0,
) -> tuple[float, float]:
    """Closed-form level mean/variance for compensated double-exponential MRJD."""
    p_positive = positive_jump_probability
    jump_mean = p_positive * beta_positive - (1.0 - p_positive) * beta_negative
    jump_second_moment = 2.0 * (
        p_positive * beta_positive**2 + (1.0 - p_positive) * beta_negative**2
    )
    adjusted_long_run_mean = (
        long_run_mean - diffusion_market_price_of_risk * volatility - jump_rate * jump_mean / kappa
    )
    decay = math.exp(-kappa * maturity)
    mean = (
        adjusted_long_run_mean
        + (initial - adjusted_long_run_mean) * decay
        + jump_rate * jump_mean * (1.0 - decay) / kappa
    )
    integrated_variance_factor = (1.0 - math.exp(-2.0 * kappa * maturity)) / (2.0 * kappa)
    variance = (volatility**2 + jump_rate * jump_second_moment) * integrated_variance_factor
    return mean, variance


def validate_model_config(config: dict) -> None:
    """Raise clear errors for invalid core model and experiment parameters."""
    for name in ("merton", "mrjd"):
        model = config["models"][name]
        for key in ("spot", "strike", "maturity"):
            if model[key] <= 0:
                raise ValueError(f"models.{name}.{key} must be positive")
    mrjd = config["models"]["mrjd"]
    if mrjd["mean_reversion"] <= 0 or mrjd["volatility"] < 0:
        raise ValueError("MRJD mean reversion must be positive and volatility nonnegative")
    if mrjd["beta_positive"] <= 0 or mrjd["beta_negative"] <= 0:
        raise ValueError("MRJD beta parameters are positive jump-size means")
    if not 0 < mrjd["positive_jump_probability"] < 1:
        raise ValueError("MRJD positive_jump_probability must lie strictly between zero and one")


def run_analytical_validation(config: dict, seed: int, n_paths: int = 100000) -> list[dict]:
    """Compare the implemented simulators with independent analytical moments/prices."""
    from .estimators import pathwise_estimators

    rows: list[dict] = []

    def add(
        name: str, analytic: float, estimate: float, standard_error: float, detail: str
    ) -> None:
        z_score = (estimate - analytic) / standard_error if standard_error > 0 else 0.0
        rows.append(
            {
                "benchmark": name,
                "analytic_value": analytic,
                "monte_carlo_value": estimate,
                "standard_error": standard_error,
                "z_score": z_score,
                "status": "PASS" if abs(z_score) <= 4.0 else "REVIEW",
                "details": detail,
                "paths": n_paths,
            }
        )

    rng = np.random.default_rng(seed)
    m = config["models"]["merton"]
    t = m["maturity"]
    p_log = merton_base_paths(rng, n_paths, np.array([t]), m, m["volatility"])
    p_payoff = payoff(np.exp(p_log), m["strike"], "call", "vanilla")
    bs_price = black_scholes_call(m["spot"], m["strike"], t, m["rate"], m["volatility"])
    discount = math.exp(-m["rate"] * t)
    add(
        "GBM vanilla call / Black-Scholes",
        bs_price,
        float(p_payoff.mean() * discount),
        float(p_payoff.std(ddof=1) / math.sqrt(n_paths) * discount),
        "Exact GBM endpoint transition; discounted payoff compared with Black-Scholes.",
    )

    merton_case = {"pair": "merton", "observations": 1, "option": "call", "style": "vanilla"}
    _, q_payoff, _, _ = pathwise_estimators(rng, n_paths, merton_case, m, jump_rate=0.08, ratio=0.5)
    merton_analytic = merton_call(
        m["spot"],
        m["strike"],
        t,
        m["rate"],
        0.08 / 0.5,
        0.08,
        m["mean_log_jump"],
        m["log_jump_sd"],
    )
    add(
        "Merton vanilla call / Poisson mixture",
        merton_analytic,
        float(q_payoff.mean()),
        float(q_payoff.std(ddof=1) / math.sqrt(n_paths)),
        "Exponential jump times and normal marks; discounted MC compared with the Merton mixture price.",
    )

    j = config["models"]["mrjd"]
    mrjd_obs = np.array([j["maturity"]])
    vasicek = mrjd_base_paths(rng, n_paths, mrjd_obs, j)[:, 0]
    vasicek_mean, vasicek_variance = vasicek_moments(
        j["spot"], j["long_run_mean"], j["mean_reversion"], j["volatility"], j["maturity"]
    )
    add(
        "Vasicek terminal mean",
        vasicek_mean,
        float(vasicek.mean()),
        float(vasicek.std(ddof=1) / math.sqrt(n_paths)),
        "Exact OU transition compared with the closed-form mean.",
    )
    variance_se = vasicek_variance * math.sqrt(2.0 / (n_paths - 1))
    add(
        "Vasicek terminal variance",
        vasicek_variance,
        float(vasicek.var(ddof=1)),
        variance_se,
        "Gaussian sample-variance standard error uses the exact OU variance.",
    )

    rate = 0.08
    ratio = 0.33
    beta_plus, beta_minus = mrjd_scaled_means(j, ratio)
    effect_cfg = {**j, "beta_positive": beta_plus, "beta_negative": beta_minus}
    times = sample_jump_times(rng, n_paths, rate, j["maturity"])
    counts = np.fromiter((len(path) for path in times), dtype=int, count=n_paths)
    marks = sample_double_exponential_marks(
        rng, counts, beta_plus, beta_minus, j["positive_jump_probability"]
    )
    effects = mrjd_interval_effects(times, marks, mrjd_obs, rate, effect_cfg).sum(axis=1)[:, 0]
    mrjd_states = vasicek + effects
    expected = mrjd_expected_level(
        j["spot"],
        j["long_run_mean"],
        j["mean_reversion"],
        j["maturity"],
        j.get("diffusion_market_price_of_risk", 0.0),
        j["volatility"],
    )
    add(
        "MRJD terminal mean after jump compensation",
        expected,
        float(mrjd_states.mean()),
        float(mrjd_states.std(ddof=1) / math.sqrt(n_paths)),
        "Jump compensation plus the configured diffusion market-price adjustment compared with its closed-form mean.",
    )
    _, expected_mrjd_variance = mrjd_moments(
        j["spot"],
        j["long_run_mean"],
        j["mean_reversion"],
        j["volatility"],
        j["maturity"],
        rate,
        beta_plus,
        beta_minus,
        j["positive_jump_probability"],
        j.get("diffusion_market_price_of_risk", 0.0),
    )
    sample_mrjd_variance = float(mrjd_states.var(ddof=1))
    centered = mrjd_states - mrjd_states.mean()
    fourth_central_moment = float(np.mean(centered**4))
    variance_standard_error = math.sqrt(
        max(fourth_central_moment - sample_mrjd_variance**2, 0.0) / n_paths
    )
    add(
        "MRJD terminal variance",
        expected_mrjd_variance,
        sample_mrjd_variance,
        variance_standard_error,
        "Compound-OU variance includes lambda*E[J^2]; sample-based SE is approximate and does not resolve stratified/antithetic dependence.",
    )
    return rows


def run_jump_count_diagnostics(
    seed: int,
    jump_rates: list[float],
    maturity: float = 1.0,
    n_paths: int = 100000,
) -> list[dict]:
    """Compare stratified jump-count samples with Poisson category masses."""
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    categories = (
        ("zero_jumps", lambda values: values == 0, lambda mean: float(poisson.pmf(0, mean))),
        ("one_jump", lambda values: values == 1, lambda mean: float(poisson.pmf(1, mean))),
        ("multiple_jumps", lambda values: values >= 2, lambda mean: float(poisson.sf(1, mean))),
    )
    for rate in jump_rates:
        times = sample_jump_times(rng, n_paths, rate, maturity)
        counts = np.fromiter((len(path) for path in times), dtype=int, count=n_paths)
        poisson_mean = rate * maturity
        for label, predicate, probability_fn in categories:
            observed = int(predicate(counts).sum())
            expected_probability = probability_fn(poisson_mean)
            rows.append(
                {
                    "jump_rate": rate,
                    "maturity": maturity,
                    "n_paths": n_paths,
                    "category": label,
                    "observed_count": observed,
                    "observed_probability": observed / n_paths,
                    "expected_probability": expected_probability,
                    "stratification_weight": expected_probability,
                    "per_path_randomized_stratum_weight": 1.0 / n_paths,
                    "status": "PASS"
                    if abs(observed / n_paths - expected_probability) < 5.0 / n_paths + 0.01
                    else "REVIEW",
                }
            )
    return rows
