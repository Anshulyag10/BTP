# Notation

| Symbol | Meaning in the paper | Implementation name |
|---|---|---|
| `P`, `Q` | Null/base and alternative/jump transition kernels | Base diffusion and jump-diffusion |
| `p_{i,theta}` | `(1-theta)p_i + theta q_i` on jump interval i | Endpoint sample helper `mix_transition_samples`; gradients use local replacements |
| `tau_i` | Poisson event/partition times | `jump_times` |
| `N(T)` | Number of jumps before maturity | `len(jump_times[path])` |
| `J_i` | Jump mark at event i | `marks[path,i]` |
| `lambda` | Poisson intensity | `jump_rate` |
| `sigma` | Diffusion volatility | `volatility` |
| `kappa`, `mu` | MRJD mean-reversion speed and long-run level | `mean_reversion`, `long_run_mean` |
| `beta+`, `beta-` | Positive and negative exponential mean magnitudes in the study density | `beta_positive`, `beta_negative` |
| `lambda^M` | Diffusion market-price adjustment in Eq. (8) | `diffusion_market_price_of_risk` |
| `Phi` | Payoff functional | `payoff` |
| `G0`, `G1` | First-order and first-plus-second-order gradient test statistics | GradOne, GradTwo |
| `delta` | Practical option-price tolerance for CRN t-test alternative | `t_test_relative_tolerance * p_price` |
| `n` | Paths per option estimate | `path_count` |
| `N` | Number of repeated experiments | outer replication count |

The paper overloads `mu_J` in the Merton discussion/table; see `ambiguities.md`.

