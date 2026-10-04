# Computational Equations

Paper page/equation references below use journal pages 740-751 (PDF pages 1-12).

| Ref. | Computational content | Code consequence |
|---|---|---|
| p.742, (1) | Option value is payoff expectation under a transition law. | Evaluate payoff on all contract observation states; estimate by Monte Carlo mean. |
| p.742, (2) | Markov transition composition over monitoring dates. | Observation dates determine payoff state vector, not jump partition. |
| p.742, (3)-(4) | Risk-neutral GBM log drift `r-sigma^2/2`. | Base log path. |
| pp.742-743, (5)-(6) | Merton jump process and compensator `gamma=lambda E[J]`. | Add local drift compensation and jump marks on jump-time intervals. |
| p.743, (7) | Vasicek/OU process. | Exact OU transition. |
| p.743, (8) | Risk-adjusted MRJD mean-reverting drift plus compound Poisson jumps. | Include jump compensation and explicit `lambda^M` parameter. |
| p.744, (9)-(12) | Two-sided hypotheses, paired CRN t statistic, practical alternative `delta=d(P-O)`. | Paired difference test; t-test alternative shifts by a configured proportion of P price. |
| pp.744-745, (13)-(14) | Jump times and path likelihood products over random intervals. | Construct `0=tau_0<...<tau_N<tau_(N+1)=T`. |
| p.745, (15)-(17) | First derivative is a sum of single `q_i-p_i` replacements; GradOne tests derivative zero. | Exhaustive oracle is sum of local payoff replacement differences; randomized implementation requires explicit unbiased weighting. |
| p.745, (18)-(20) | Printed Eq. (18) omits the factor 2 on its unordered pair sum. Differentiating the product gives ordered pairs, and Taylor's one-half restores unordered cross terms. | GradTwo uses the singleton sum plus unordered pair cross-differences; the independent mixture-polynomial test verifies the coefficient. |
| pp.745-746, (A1)-(A3), Theorem 1, (21) | Strong Markov, at-most-linear payoff growth, square-integrability; finite Taylor expansion conditional on jumps. | Validate assumptions for options and mark laws; exhaustive sums are the reference construction. |
| p.746, Examples 1-4 | Call/put and arithmetic Asian payoffs; equidistant observation dates. | Payoff module. |
| pp.747-749, Section 4 | `alpha=.10`; antithetics; stratified jump occurrence; outer counts; plotted quantities. | Reproduce repeated experiments and aggregate median/mean. |

The article gives no software pseudocode, seed, exact RNG, explicit standard-error correction for antithetic/stratified dependence, or numerical point table for Figures 1-3.

