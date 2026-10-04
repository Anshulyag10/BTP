import copy
import unittest
from itertools import product
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from replication.config import load_config
from replication.estimators import _expand_local_replacements
from replication.experiments import run_figure1, run_figure2
from replication.models import merton_interval_effects, mrjd_interval_effects, sample_jump_times
from replication.payoffs import payoff
from replication.plotting import write_figures

ROOT = Path(__file__).resolve().parents[1]


class PaperDesignTests(unittest.TestCase):
    def test_figures_one_and_three_share_ratio_data(self):
        rows = [{"figure": "fig1", "ratio": 0.25}, {"figure": "fig2", "path_count": 64}]
        with (
            patch("replication.plotting._plot_ratio_figure") as ratio_plot,
            patch("replication.plotting._plot_path_sweep") as path_plot,
        ):
            write_figures(rows, ROOT / "tmp" / "test-plots")
        self.assertEqual(ratio_plot.call_count, 2)
        for call in ratio_plot.call_args_list:
            self.assertEqual(call.args[0]["figure"].tolist(), ["fig1"])
        self.assertEqual(ratio_plot.call_args_list[1].kwargs["aggregation"], "mean")
        self.assertEqual(path_plot.call_args.args[0]["figure"].tolist(), ["fig2"])

    def test_paper_counts_and_grids(self):
        config = load_config(ROOT / "config" / "experiments.json")
        config = copy.deepcopy(config)
        config["simulation"]["full_paper_counts"] = True
        with (
            patch("replication.experiments.estimate_once", return_value=[{"method": "GradOne"}]),
            patch("builtins.print"),
        ):
            ratios = pd.DataFrame(run_figure1(config))
            paths = pd.DataFrame(run_figure2(config))
        for frame in (ratios, paths):
            for case in config["cases"]:
                subset = frame[frame["case"] == case["id"]]
                expected = 500 if case["pair"] == "merton" else 300
                self.assertEqual(subset["replication"].nunique(), expected)
        self.assertEqual(sorted(paths["path_count"].unique()), config["simulation"]["path_counts"])
        self.assertEqual(set(paths["figure"]), {"fig2"})

    def test_gradient_terms_match_mixture_polynomial(self):
        base = np.array([[-0.6]])
        effects = np.array([[[0.3], [0.7], [-0.2]]])
        fn = lambda states: np.maximum(states[:, 0], 0.0)
        p, q, one, two = _expand_local_replacements(base, effects, fn)
        values = []
        thetas = np.linspace(0, 1, 4)
        for theta in thetas:
            expectation = 0.0
            for included in product((0, 1), repeat=3):
                count = sum(included)
                weight = theta**count * (1 - theta) ** (3 - count)
                state = base + (effects * np.array(included)[None, :, None]).sum(axis=1)
                expectation += weight * fn(state)[0]
            values.append(expectation)
        coefficients = np.polynomial.polynomial.polyfit(thetas, values, 3)
        self.assertAlmostEqual(one[0], coefficients[1], places=12)
        self.assertAlmostEqual(two[0], coefficients[1] + coefficients[2], places=12)
        self.assertAlmostEqual(p[0], values[0])
        self.assertAlmostEqual(q[0], values[-1])

    def test_vectorized_effects_match_direct_transitions(self):
        times = [np.array([0.2, 0.8]), np.array([]), np.array([0.5])]
        marks = np.array([[0.1, -0.3], [0.0, 0.0], [0.4, 0.0]])
        obs = np.array([0.1, 0.2, 0.5, 0.9, 1.0])
        cfg = {
            "maturity": 1.0,
            "mean_log_jump": -0.1,
            "log_jump_sd": 0.2,
            "mean_reversion": 0.24,
            "volatility": 5.16,
            "positive_jump_probability": 0.5,
            "beta_positive": 3.48,
            "beta_negative": 5.54,
            "diffusion_market_price_of_risk": 0.2,
        }
        rate = 0.7
        merton = merton_interval_effects(times, marks, obs, rate, cfg).sum(axis=1)
        ou = mrjd_interval_effects(times, marks, obs, rate, cfg).sum(axis=1)
        gamma = rate * np.expm1(-0.1 + 0.5 * 0.2**2)
        kappa = cfg["mean_reversion"]
        mean_shift = -0.2 * 5.16 - rate * (0.5 * 3.48 - 0.5 * 5.54) / kappa
        for row, events in enumerate(times):
            direct_merton = -gamma * obs
            direct_ou = mean_shift * (1 - np.exp(-kappa * obs))
            for j, event in enumerate(events):
                direct_merton += marks[row, j] * (obs >= event)
                direct_ou += (
                    marks[row, j] * np.exp(-kappa * np.maximum(obs - event, 0)) * (obs >= event)
                )
            np.testing.assert_allclose(merton[row], direct_merton, atol=1e-14)
            np.testing.assert_allclose(ou[row], direct_ou, atol=1e-14)

    def test_single_jump_is_uniform_conditional_on_count(self):
        times = sample_jump_times(np.random.default_rng(53), 50000, 0.7, 1.0)
        single = np.array([path[0] for path in times if len(path) == 1])
        self.assertAlmostEqual(float(single.mean()), 0.5, delta=0.01)
        self.assertAlmostEqual(float(single.var()), 1 / 12, delta=0.004)

    def test_invalid_payoff_style_is_rejected(self):
        with self.assertRaises(ValueError):
            payoff(np.ones((2, 2)), 1.0, "call", "typo")


if __name__ == "__main__":
    unittest.main()
