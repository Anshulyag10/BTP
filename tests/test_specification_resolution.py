import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from replication.config import load_config
from replication.diagnostics import conditional_randomized_moments
from replication.estimators import _expand_local_replacements
from replication.models import mrjd_interval_effects, mrjd_jump_moments, mrjd_scaled_means

ROOT = Path(__file__).resolve().parents[1]


class SpecificationResolutionTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "config/experiments.json")
        self.model = self.config["models"]["mrjd"]

    def test_axis_mapping_preserves_signed_mean_at_every_point(self):
        original = mrjd_jump_moments(self.model)
        for ratio in self.config["simulation"]["mrjd_ratio_grid"]:
            plus, minus = mrjd_scaled_means(self.model, ratio)
            moments = mrjd_jump_moments(
                {**self.model, "beta_positive": plus, "beta_negative": minus}
            )
            self.assertAlmostEqual(moments["jump_mean"], original["jump_mean"], places=12)
            self.assertAlmostEqual(moments["jump_absolute_mean"] / self.model["volatility"], ratio)
            self.assertGreater(min(plus, minus), 0)

    def test_fixed_mean_mapping_has_a_feasibility_boundary(self):
        boundary = abs(mrjd_jump_moments(self.model)["jump_mean"]) / self.model["volatility"]
        with self.assertRaisesRegex(ValueError, "Fixed-mean ratio"):
            mrjd_scaled_means(self.model, boundary * 0.99)

    def test_proportional_mapping_is_an_explicit_alternative(self):
        model = {**self.model, "ratio_interpretation": "mean_absolute_jump_over_volatility"}
        plus, minus = mrjd_scaled_means(model, 0.33)
        self.assertAlmostEqual(plus / minus, model["beta_positive"] / model["beta_negative"])
        self.assertNotAlmostEqual(0.5 * (plus - minus), mrjd_jump_moments(model)["jump_mean"])

    def test_literal_signed_gap_cannot_match_positive_axis(self):
        model = {**self.model, "ratio_interpretation": "lambda_over_signed_beta_gap"}
        with self.assertRaisesRegex(ValueError, "negative"):
            mrjd_scaled_means(model, 0.33, 0.7)

    def test_missing_parameterization_is_rejected(self):
        del self.config["models"]["mrjd"]["ratio_interpretation"]
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps(self.config))
            with self.assertRaisesRegex(ValueError, "must be explicit"):
                load_config(path)

    def test_randomization_expectation_with_variable_partition_sizes(self):
        base = np.array([[-0.4], [-0.6], [0.2]])
        effects = np.array([[[0.1], [0.0], [0.0]], [[0.5], [0.4], [0.0]], [[-0.5], [0.8], [-0.1]]])
        counts = np.array([1, 2, 3])
        payoff_fn = lambda values: np.maximum(values[:, 0], 0)
        _, _, one, two = _expand_local_replacements(base, effects, payoff_fn)
        means, variances = conditional_randomized_moments(base, effects, payoff_fn, counts)
        np.testing.assert_allclose(means, np.column_stack((one, two)), atol=1e-14)
        np.testing.assert_array_equal(variances[0], np.zeros(2))
        self.assertTrue(np.any(variances[1:] > 0))

    def test_no_jump_realization_retains_compensated_drift(self):
        effects = mrjd_interval_effects(
            [np.array([])], np.zeros((1, 0)), np.array([1.0]), 0.7, self.model
        )
        expected = -0.7 * mrjd_jump_moments(self.model)["jump_mean"] / self.model["mean_reversion"]
        expected *= 1 - np.exp(-self.model["mean_reversion"])
        self.assertAlmostEqual(effects[0, 0, 0], expected)
        self.assertNotEqual(effects[0, 0, 0], 0)


if __name__ == "__main__":
    unittest.main()
