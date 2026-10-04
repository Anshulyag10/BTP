import numpy as np

from .estimators import _randomized_mvd_estimators


def conditional_randomized_moments(base, effects, payoff_fn, counts):
    """Enumerate interval choices while holding every simulated path fixed."""
    counts = np.asarray(counts)
    means = np.zeros((len(counts), 2))
    seconds = np.zeros_like(means)

    class SelectedIntervals:
        def __init__(self, selected):
            self.selected = selected

        def integers(self, low, high):
            return np.where(self.selected < high, self.selected, 0)

    for selected in range(int(counts.max())):
        _, _, one, two = _randomized_mvd_estimators(
            SelectedIntervals(selected), base, effects, payoff_fn, counts
        )
        values = np.column_stack((one, two))
        weights = np.where(selected < counts, 1.0 / counts, 0.0)[:, None]
        means += weights * values
        seconds += weights * values**2
    return means, np.maximum(seconds - means**2, 0.0)
