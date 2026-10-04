# Paper vs. Code Summary

The source is the supplied 12-page EJOR paper, DOI `10.1016/j.ejor.2021.07.015`. Equation-by-equation details are in `paper/specification/`; broad implementation coverage is recorded in `paper_to_code_matrix.csv`.

## Implemented and Checked

- GBM/Merton and Vasicek/MRJD model scaffolding, the realized Poisson stopping-time partition, local transition replacements, option payoffs, and paper parameter grids are implemented.
- Pair-2 double-exponential jumps use Table 2 beta values as mean magnitudes and use the 1/2 positive/negative probabilities in the numerical-study density.
- The `p_theta` mixture endpoint helper is implemented and tested at theta 0 and 1.
- Randomized GradOne/GradTwo use a uniform selected interval and the `N+1` / `(N+1)/2` weight construction, supported as a reconstruction by the authors' [2018 technical presentation](https://www.researchgate.net/publication/350193285_When_do_Jumps_Matter_in_Option_Prices). The paper's equations state exhaustive derivative sums; exact author implementation and estimator variance are not established.
- Six analytical simulator checks pass. The test suite has 17 passing tests. These establish selected model laws and internal properties, not exact reproduction of the paper's power curves.
- The final saved DEBUG run has fresh figures, 2,448 replicate-method rows, four outer repetitions, and a manifest hashing source/config/paper/output inputs. It is not the paper-scale run.

## Unresolved Interpretations

- Figure axes give Pair-2 `E|J|/sigma`; nearby prose gives `lambda/(beta+ - beta-)`, negative under the table's beta ordering. Baseline follows the positive plotted axis; controlled interpretations are logged separately.
- Eq. (8) includes a diffusion market-price adjustment whose numerical value is not supplied; baseline sets it to zero.
- Table 1 `mu_J` is overloaded; baseline treats `-3.3e-5` as the mean log jump.
- The 12-date option is a put in Example 4 and the in-panel heading, while a subfigure caption calls it a call. Baseline follows the put formula and panel heading.
- Antithetic/stratified sampling induces dependence, but the implemented t statistic uses path-level iid standard errors and `n-1` df. The article does not resolve this convention.
- No original seed, executable source, raw paper curve values, or commit are available.

## Output Comparison

Current Figure 1 relative-difference maxima are approximately `0.052110`, `0.166304`, `0.493713`, and `0.463548` for panels (a)-(d). Approximate reads from the paper image are `0.058`, `1.2`, `0.38`, and `5.8`; only panel (a) is close in scale. Panel (d)'s current value at `x=0.67` is `0.278711`, and its maximum is at `x=1`. Paper reads are approximate visual estimates, not source data. Figure 2/3 results are likewise not validated and the DEBUG rejection curve is quantized by four repetitions.

**Assessment: RECONSTRUCTED FOUNDATION; NOT YET REPRODUCED.** Paper mode remains gated and has not been run.
