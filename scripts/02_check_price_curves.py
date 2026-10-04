from pathlib import Path

import pandas as pd

from replication.benchmarks import mrjd_option_price
from replication.config import load_config
from replication.models import mrjd_scaled_means
from replication.validation import black_scholes_call, merton_call

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = load_config(ROOT / "config" / "experiments.json")
    rows = []
    for case in config["cases"]:
        model = config["models"][case["pair"]]
        grid = config["simulation"][f"{case['pair']}_ratio_grid"]
        for rate in config["simulation"]["jump_rates"]:
            for ratio in grid:
                if case["pair"] == "merton":
                    sigma = rate / ratio
                    args = (model["spot"], model["strike"], model["maturity"], model["rate"], sigma)
                    p = black_scholes_call(*args)
                    q = merton_call(*args, rate, model["mean_log_jump"], model["log_jump_sd"])
                else:
                    plus, minus = mrjd_scaled_means(model, ratio, rate)
                    scenario = {**model, "beta_positive": plus, "beta_negative": minus}
                    p = mrjd_option_price(scenario, case, include_diffusion_risk_adjustment=False)
                    q = mrjd_option_price(scenario, case, rate)
                rows.append(
                    {
                        "case": case["id"],
                        "jump_rate": rate,
                        "ratio": ratio,
                        "p_analytic": p,
                        "q_analytic": q,
                        "relative_difference_analytic": abs(q - p) / max(abs(p), 1e-12),
                    }
                )
    output = ROOT / "outputs" / "validation" / "price_benchmarks.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output, index=False)
    print(frame.groupby("case")["relative_difference_analytic"].max().to_string())
    return frame


if __name__ == "__main__":
    run()
