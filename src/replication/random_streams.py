from __future__ import annotations

import numpy as np


def antithetic_normal(rng: np.random.Generator, shape: tuple[int, ...]) -> np.ndarray:
    """Return standard normal draws paired with their negatives on axis zero."""
    n = shape[0]
    half = (n + 1) // 2
    first = rng.standard_normal((half, *shape[1:]))
    paired = np.concatenate((first, -first), axis=0)
    return paired[:n]


def antithetic_uniform(rng: np.random.Generator, shape: tuple[int, ...]) -> np.ndarray:
    """Return uniforms paired with their complements on axis zero."""
    n = shape[0]
    half = (n + 1) // 2
    first = rng.random((half, *shape[1:]))
    paired = np.concatenate((first, 1.0 - first), axis=0)
    return paired[:n]
