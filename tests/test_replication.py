from __future__ import annotations

import unittest

import numpy as np
from scipy.stats import t

from replication.estimators import (
    _expand_local_replacements,
    _randomized_mvd_estimators,
    pathwise_estimators,
)
from replication.experiments import _repetitions
from replication.models import (
    mix_transition_samples,
    mrjd_base_paths,
    mrjd_interval_effects,
    mrjd_scaled_means,
    sample_double_exponential_marks,
    sample_jump_times,
)
from replication.statistics import critical_value, noncentral_t_power
from replication.validation import (
    black_scholes_call,
    merton_call,
    mrjd_expected_level,
    mrjd_moments,
    run_jump_count_diagnostics,
    vasicek_moments,
)


class JumpSamplingTests(unittest.TestCase):
    def test_exponential_arrivals_have_poisson_count_marginal(self) -> None:
        rng = np.random.default_rng(412)
        paths = sample_jump_times(rng, 6000, 0.7, 1.0)
        counts = np.fromiter((len(path) for path in paths), dtype=int)
        self.assertAlmostEqual(float(counts.mean()), 0.7, delta=0.04)
        self.assertAlmostEqual(float(np.mean(counts == 0)), np.exp(-0.7), delta=0.015)
        self.assertTrue(all(np.all(np.diff(path) > 0) for path in paths))
        self.assertTrue(all(np.all((path > 0) & (path < 1)) for path in paths))

    def test_double_exponential_uses_beta_as_mean(self) -> None:
        rng = np.random.default_rng(52)
        counts = np.ones(30000, dtype=int)
        marks = sample_double_exponential_marks(rng, counts, 3.0, 5.0, 0.4)[:, 0]
        self.assertAlmostEqual(float(np.mean(marks)), 0.4 * 3.0 - 0.6 * 5.0, delta=0.09)
        self.assertAlmostEqual(float(np.mean(marks > 0)), 0.4, delta=0.015)

    def test_jump_marks_are_not_antithetically_paired(self) -> None:
        rng = np.random.default_rng(523)
        counts = np.ones(10000, dtype=int)
        marks = sample_double_exponential_marks(rng, counts, 2.0, 3.0, 0.5)[:, 0]
        correlation = np.corrcoef(marks[:5000], marks[5000:])[0, 1]
        self.assertLess(abs(float(correlation)), 0.04)

    def test_mixture_transition_has_exact_p_and_q_endpoints(self) -> None:
        rng = np.random.default_rng(87)
        p = np.arange(40, dtype=float).reshape(20, 2)
        q = p + 100.0
        np.testing.assert_array_equal(mix_transition_samples(rng, p, q, 0.0), p)
        np.testing.assert_array_equal(mix_transition_samples(rng, p, q, 1.0), q)
        mixed = mix_transition_samples(rng, p, q, 0.35)
        self.assertAlmostEqual(float(np.mean(mixed[:, 0] - p[:, 0]) / 100.0), 0.35, delta=0.12)

    def test_jump_count_diagnostics_include_poisson_stratum_weights(self) -> None:
        rows = run_jump_count_diagnostics(771, [0.08, 0.70], n_paths=12000)
        self.assertEqual(len(rows), 6)
        for rate in (0.08, 0.70):
            group = [row for row in rows if row["jump_rate"] == rate]
            self.assertAlmostEqual(
                sum(row["stratification_weight"] for row in group), 1.0, places=12
            )
            self.assertEqual(sum(row["observed_count"] for row in group), 12000)

    def test_figure_ratio_scales_mean_absolute_jump_over_volatility(self) -> None:
        cfg = {
            "ratio_interpretation": "mean_absolute_jump_over_volatility_fixed_mean",
            "beta_positive": 3.48,
            "beta_negative": 5.54,
            "positive_jump_probability": 0.5,
            "volatility": 5.16,
        }
        beta_plus, beta_minus = mrjd_scaled_means(cfg, 0.33)
        mean_abs = 0.5 * beta_plus + 0.5 * beta_minus
        self.assertAlmostEqual(mean_abs / cfg["volatility"], 0.33)
        self.assertGreater(beta_plus, 0.0)

    def test_mrjd_compensated_jump_effect_has_zero_mean(self) -> None:
        rng = np.random.default_rng(901)
        n = 12000
        rate = 0.35
        cfg = {
            "maturity": 1.0,
            "mean_reversion": 0.24,
            "long_run_mean": 0.63,
            "volatility": 5.16,
            "beta_positive": 3.48,
            "beta_negative": 5.54,
            "positive_jump_probability": 0.5,
        }
        times = sample_jump_times(rng, n, rate, 1.0)
        counts = np.fromiter((len(path) for path in times), dtype=int)
        marks = sample_double_exponential_marks(rng, counts, 3.48, 5.54, 0.5)
        effects = mrjd_interval_effects(times, marks, np.array([1.0]), rate, cfg)
        terminal_effect = effects.sum(axis=1)[:, 0]
        self.assertLess(abs(float(terminal_effect.mean())), 0.12)

    def test_mrjd_diffusion_risk_price_adjusts_local_mean(self) -> None:
        cfg = {
            "maturity": 1.0,
            "mean_reversion": 0.24,
            "long_run_mean": 0.63,
            "volatility": 5.16,
            "beta_positive": 3.48,
            "beta_negative": 5.54,
            "positive_jump_probability": 0.5,
            "diffusion_market_price_of_risk": 0.2,
        }
        effects = mrjd_interval_effects([np.empty(0)], np.zeros((1, 0)), np.array([1.0]), 0.0, cfg)
        expected = -0.2 * 5.16 * (1.0 - np.exp(-0.24))
        self.assertAlmostEqual(float(effects[0, 0, 0]), expected)

    def test_mrjd_closed_form_moments_match_simulated_path_moments(self) -> None:
        rng = np.random.default_rng(9017)
        n_paths = 50000
        maturity = 1.0
        rate = 0.22
        cfg = {
            "spot": 40.0,
            "maturity": maturity,
            "mean_reversion": 0.24,
            "long_run_mean": 0.63,
            "volatility": 5.16,
            "beta_positive": 2.2,
            "beta_negative": 3.0,
            "positive_jump_probability": 0.5,
        }
        times = sample_jump_times(rng, n_paths, rate, maturity)
        counts = np.fromiter((len(path) for path in times), dtype=int, count=n_paths)
        marks = sample_double_exponential_marks(
            rng, counts, cfg["beta_positive"], cfg["beta_negative"], 0.5
        )
        baseline = mrjd_base_paths(rng, n_paths, np.array([maturity]), cfg)
        effects = mrjd_interval_effects(times, marks, np.array([maturity]), rate, cfg)
        simulated = baseline[:, 0] + effects.sum(axis=1)[:, 0]
        expected_mean, expected_variance = mrjd_moments(
            cfg["spot"],
            cfg["long_run_mean"],
            cfg["mean_reversion"],
            cfg["volatility"],
            maturity,
            rate,
            cfg["beta_positive"],
            cfg["beta_negative"],
            cfg["positive_jump_probability"],
        )
        self.assertAlmostEqual(float(simulated.mean()), expected_mean, delta=0.08)
        self.assertAlmostEqual(float(simulated.var(ddof=1)), expected_variance, delta=0.8)


class EstimatorTests(unittest.TestCase):
    def test_full_mode_allocates_repetitions_by_model_pair(self) -> None:
        simulation = {
            "full_paper_counts": True,
            "paper_repetitions_pair1": 500,
            "paper_repetitions_pair2": 300,
            "repetitions_fig1": 4,
            "repetitions_fig23": 6,
        }
        self.assertEqual(_repetitions(simulation, {"pair": "merton"}, "repetitions_fig1"), 500)
        self.assertEqual(_repetitions(simulation, {"pair": "mrjd"}, "repetitions_fig23"), 300)

    def test_pairwise_gradient_uses_distinct_interval_replacements(self) -> None:
        baseline = np.array([[-1.0]])
        effects = np.array([[[1.0], [1.0]]])
        payoff_fn = lambda states: np.maximum(states[:, 0], 0.0)
        _, _, grad_one, grad_two = _expand_local_replacements(baseline, effects, payoff_fn)
        self.assertEqual(float(grad_one[0]), 0.0)
        self.assertEqual(float(grad_two[0]), 1.0)

    def test_randomized_mvd_weights_match_exhaustive_sums_in_expectation(self) -> None:
        n_paths = 30000
        baseline = np.full((n_paths, 1), -1.0)
        local_effects = np.broadcast_to(np.array([[[0.3], [0.8], [1.2]]]), (n_paths, 3, 1))
        interval_counts = np.full(n_paths, 3)
        payoff_fn = lambda states: np.maximum(states[:, 0], 0.0)

        _, _, exact_one, exact_two = _expand_local_replacements(baseline, local_effects, payoff_fn)
        _, _, randomized_one, randomized_two = _randomized_mvd_estimators(
            np.random.default_rng(915), baseline, local_effects, payoff_fn, interval_counts
        )
        self.assertAlmostEqual(float(randomized_one.mean()), float(exact_one.mean()), delta=0.01)
        self.assertAlmostEqual(float(randomized_two.mean()), float(exact_two.mean()), delta=0.02)

    def test_zero_jump_partition_has_one_interval_and_no_pair_term(self) -> None:
        baseline = np.array([[-1.0]])
        effects = np.array([[[1.0]]])
        payoff_fn = lambda states: np.maximum(states[:, 0], 0.0)
        _, _, grad_one, grad_two = _expand_local_replacements(baseline, effects, payoff_fn)
        np.testing.assert_array_equal(grad_one, grad_two)


class AnalyticalAndInferenceTests(unittest.TestCase):
    def test_merton_mixture_reduces_to_black_scholes_without_jumps(self) -> None:
        bs = black_scholes_call(40.0, 40.0, 1.0, 0.02, 0.25)
        merton = merton_call(40.0, 40.0, 1.0, 0.02, 0.25, 0.0, -0.1, 0.3)
        self.assertAlmostEqual(merton, bs, places=10)

    def test_jump_time_merton_simulation_matches_analytic_call(self) -> None:
        cfg = {
            "spot": 100.0,
            "strike": 100.0,
            "maturity": 1.0,
            "rate": 0.03,
            "mean_log_jump": -0.1,
            "log_jump_sd": 0.2,
        }
        case = {"pair": "merton", "observations": 1, "option": "call", "style": "vanilla"}
        n_paths = 50000
        _, q, _, _ = pathwise_estimators(
            np.random.default_rng(83), n_paths, case, cfg, jump_rate=0.5, ratio=1.0
        )
        discounted_mc = float(np.mean(q))
        standard_error = float(np.std(q, ddof=1) / np.sqrt(n_paths))
        analytic = merton_call(100.0, 100.0, 1.0, 0.03, 0.5, 0.5, -0.1, 0.2)
        self.assertLess(abs(discounted_mc - analytic), 4.0 * standard_error)

    def test_vasicek_and_compensated_mrjd_share_expected_level(self) -> None:
        mean, _ = vasicek_moments(40.0, 0.63, 0.24, 5.16, 1.0)
        self.assertAlmostEqual(mean, mrjd_expected_level(40.0, 0.63, 0.24, 1.0))
        adjusted = mrjd_expected_level(40.0, 0.63, 0.24, 1.0, 0.2, 5.16)
        self.assertLess(adjusted, mean)

    def test_student_t_quantile_and_null_power_are_exact(self) -> None:
        self.assertAlmostEqual(critical_value(0.05, 9), float(t.ppf(0.975, 9)), places=13)
        self.assertAlmostEqual(noncentral_t_power(0.0, 0.10, 255), 0.10, delta=1e-12)


if __name__ == "__main__":
    unittest.main()
