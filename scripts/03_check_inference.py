from pathlib import Path

import numpy as np
import pandas as pd

from replication.statistics import critical_value, noncentral_t_power

ROOT = Path(__file__).resolve().parents[1]


def run():
    rng = np.random.default_rng(20260934)
    alpha, n, replications = 0.1, 256, 10000
    rows = []
    cutoff = critical_value(alpha, n - 1)
    for label, shift in (("iid_null", 0.0), ("iid_alternative", 0.1)):
        values = rng.standard_normal((replications, n)) + shift
        statistics = values.mean(axis=1) / (values.std(axis=1, ddof=1) / np.sqrt(n))
        from scipy.stats import nct

        powers = nct.cdf(-cutoff, n - 1, statistics) + nct.sf(cutoff, n - 1, statistics)
        rows.append(
            {
                "design": label,
                "paths": n,
                "replications": replications,
                "rejection_probability": np.mean(np.abs(statistics) > cutoff),
                "theoretical_power": noncentral_t_power(shift * np.sqrt(n), alpha, n - 1),
                "mean_plugin_power": powers.mean(),
                "median_plugin_power": np.median(powers),
            }
        )
    output = ROOT / "outputs" / "validation" / "inference_calibration.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    run()
