import math

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr


def normal_option_price(mean, variance, strike, option):
    if option not in {"call", "put"}:
        raise ValueError("option must be call or put")
    sign = 1 if option == "call" else -1
    difference = sign * (mean - strike)
    if variance <= 0:
        return max(difference, 0.0)
    sd = math.sqrt(variance)
    return difference * ndtr(difference / sd) + sd * math.exp(
        -0.5 * (difference / sd) ** 2
    ) / math.sqrt(2 * math.pi)


def mrjd_option_price(cfg, case, jump_rate=0.0, include_diffusion_risk_adjustment=True):
    """Price vanilla/Asian OU options by characteristic-function quadrature."""
    count = case["observations"] if case["style"] == "asian" else 1
    times = np.linspace(cfg["maturity"] / count, cfg["maturity"], count)
    kappa = cfg["mean_reversion"]
    sigma = cfg["volatility"]
    decay = np.exp(-kappa * times)
    mean = np.mean(cfg["long_run_mean"] + (cfg["spot"] - cfg["long_run_mean"]) * decay)
    covariance = (
        sigma**2
        / (2 * kappa)
        * (
            np.exp(-kappa * np.abs(times[:, None] - times[None, :]))
            - decay[:, None] * decay[None, :]
        )
    )
    variance = covariance.mean()
    if include_diffusion_risk_adjustment:
        mean -= cfg.get("diffusion_market_price_of_risk", 0.0) * sigma * np.mean(1 - decay)
    discount = math.exp(-cfg["rate"] * cfg["maturity"])
    if jump_rate == 0:
        return discount * normal_option_price(mean, variance, cfg["strike"], case["option"])

    positive = cfg["positive_jump_probability"]
    beta_plus, beta_minus = cfg["beta_positive"], cfg["beta_negative"]
    jump_mean = positive * beta_plus - (1 - positive) * beta_minus
    starts = np.concatenate(([0.0], times[:-1]))
    weights = np.cumsum(decay[::-1])[::-1] / count
    left = weights * np.exp(kappa * starts)
    right = weights * np.exp(kappa * times)
    integrated_weight = np.mean(1 - decay) / kappa
    compensated = cfg.get("include_jump_compensation", True)
    deterministic = (
        mean - cfg["strike"] - (jump_rate * jump_mean * integrated_weight if compensated else 0)
    )
    expected = (
        mean - cfg["strike"] + (0 if compensated else jump_rate * jump_mean * integrated_weight)
    )
    jump_second = 2 * (positive * beta_plus**2 + (1 - positive) * beta_minus**2)
    total_variance = variance + jump_rate * jump_second * np.sum((right**2 - left**2) / (2 * kappa))

    def integrand(u):
        if u < 1e-7:
            return (expected**2 + total_variance) / 2
        plus = np.log1p(-1j * u * beta_plus * left) - np.log1p(-1j * u * beta_plus * right)
        minus = np.log1p(1j * u * beta_minus * left) - np.log1p(1j * u * beta_minus * right)
        log_phi = (
            1j * u * deterministic
            - 0.5 * variance * u**2
            + jump_rate / kappa * np.sum(positive * plus + (1 - positive) * minus)
        )
        return -np.expm1(log_phi).real / u**2

    # E|X-K| = (2/pi) integral (1-Re phi(u))/u^2 du.
    absolute_moment = 2 / math.pi * quad(integrand, 0, np.inf, epsabs=1e-8, limit=200)[0]
    sign = 1 if case["option"] == "call" else -1
    return discount * (absolute_moment + sign * expected) / 2
