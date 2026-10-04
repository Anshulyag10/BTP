from __future__ import annotations

import numpy as np


def payoff(observed_spots: np.ndarray, strike: float, option: str, style: str) -> np.ndarray:
    """Evaluate vanilla or discretely monitored Asian call/put payoffs."""
    if style not in {"vanilla", "asian"}:
        raise ValueError(f"Unsupported option style: {style}")
    if observed_spots.ndim != 2 or observed_spots.shape[1] == 0:
        raise ValueError("Spots must have shape (paths, observations)")
    reference = observed_spots[:, -1] if style == "vanilla" else observed_spots.mean(axis=1)
    if option == "call":
        return np.maximum(reference - strike, 0.0)
    if option == "put":
        return np.maximum(strike - reference, 0.0)
    raise ValueError(f"Unsupported option type: {option}")
