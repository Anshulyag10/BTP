import json
import unittest
from pathlib import Path

import numpy as np

from replication.benchmarks import mrjd_option_price, normal_option_price
from replication.estimators import pathwise_estimators
from replication.models import mrjd_scaled_means
from replication.validation import black_scholes_call, vasicek_moments


class CharacteristicFunctionTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.config = json.loads((root / "config" / "experiments.json").read_text())

    def test_no_jumps_matches_normal_terminal_price(self):
        cfg = self.config["models"]["mrjd"]
        case = self.config["cases"][1]
        mean, variance = vasicek_moments(
            cfg["spot"],
            cfg["long_run_mean"],
            cfg["mean_reversion"],
            cfg["volatility"],
            cfg["maturity"],
        )
        expected = normal_option_price(mean, variance, cfg["strike"], "put")
        self.assertAlmostEqual(mrjd_option_price(cfg, case), expected, places=12)

    def test_zero_jump_merton_retains_baseline_volatility(self):
        cfg = {**self.config["models"]["merton"], "rate": 0.03, "volatility": 0.25}
        case = self.config["cases"][0]
        p, q, one, two = pathwise_estimators(np.random.default_rng(75), 60000, case, cfg, 0.0, 0.5)
        expected = black_scholes_call(40, 40, 1, 0.03, 0.25)
        self.assertLess(abs(p.mean() - expected), 4 * p.std(ddof=1) / np.sqrt(len(p)))
        np.testing.assert_array_equal(p, q)
        np.testing.assert_array_equal(one, np.zeros_like(one))
        np.testing.assert_array_equal(two, np.zeros_like(two))

    def test_put_call_parity_for_asian_jump_price(self):
        cfg = self.config["models"]["mrjd"]
        case = self.config["cases"][3]
        put = mrjd_option_price(cfg, case, 0.7)
        call = mrjd_option_price(cfg, {**case, "option": "call"}, 0.7)
        times = np.linspace(cfg["maturity"] / 12, cfg["maturity"], 12)
        mean = np.mean(
            cfg["long_run_mean"]
            + (cfg["spot"] - cfg["long_run_mean"]) * np.exp(-cfg["mean_reversion"] * times)
        )
        self.assertAlmostEqual(call - put, mean - cfg["strike"], places=11)

    def test_diffusion_risk_adjustment_survives_zero_jump_rate(self):
        cfg = {**self.config["models"]["mrjd"], "diffusion_market_price_of_risk": 0.2}
        case = self.config["cases"][1]
        p, q, _, _ = pathwise_estimators(np.random.default_rng(19), 60000, case, cfg, 0.0, 0.5)
        p_expected = mrjd_option_price(cfg, case, include_diffusion_risk_adjustment=False)
        q_expected = mrjd_option_price(cfg, case)
        for values, expected in ((p, p_expected), (q, q_expected)):
            self.assertLess(
                abs(values.mean() - expected), 4 * values.std(ddof=1) / np.sqrt(len(values))
            )

    def test_jump_prices_match_simulation_at_all_monitoring_grids(self):
        model = self.config["models"]["mrjd"]
        plus, minus = mrjd_scaled_means(model, 1.0)
        cfg = {**model, "beta_positive": plus, "beta_negative": minus}
        for case in self.config["cases"][1:]:
            _, q, _, _ = pathwise_estimators(
                np.random.default_rng(319), 60000, case, model, 0.7, 1.0
            )
            analytic = mrjd_option_price(cfg, case, 0.7)
            se = np.std(q, ddof=1) / np.sqrt(len(q))
            self.assertLess(abs(q.mean() - analytic), 4 * se)


if __name__ == "__main__":
    unittest.main()
