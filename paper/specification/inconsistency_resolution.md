# Paper inconsistencies and implementation decisions

Reviewed 4 October 2026 against the supplied `1-s2.0-S037722172100610X-main.pdf`.
Printed page numbers are used below. The supplied and project PDFs have different
file hashes but identical extracted text on all 12 pages and identical embedded
Figures 1-3. The supplied copy is preserved as `paper/reviewed_source.pdf`;
`source_verification.json` records the comparison.

## Evidence and decisions

| Issue | Evidence in the paper | Resolution in this project | Confidence / limit |
|---|---|---|---|
| MRJD horizontal ratio | Figures 1-3 label mean absolute jump amplitude / volatility. Section 4, p.747, gives `lambda/(beta+ - beta-)`, negative under Table 2. | Use `E[abs(J)]/sigma`. Keep the absolute-gap variant in diagnostics; reject the literal signed-gap mapping. | The literal requirements are incompatible. The authors' executed mapping is unknown. |
| What stays fixed during the MRJD sweep | p.747 says the mean jump and sign probability stay unchanged. Previous proportional beta scaling changed the signed mean. | Preserve `E[J]=-1.03` and `p=0.5` while solving for both beta means at the requested axis ratio. The interpretation is a required configuration field. | This reconciles the axis with a natural signed-mean reading of the prose. It is a documented reconstruction, not a recovered author algorithm. |
| Twelve-date contract | Example 4 and the numerical-study prose, p.746, specify a put. Figures 1-3 panel headings also say put; subfigure captions say call. | Keep the put as the baseline. Price a twelve-date call independently as a sensitivity case. | Stronger internal evidence favors the put; the actual author contract cannot be proved from the caption conflict. |
| Jump-size parameter units and signs | The generic density on p.743 omits a negative-side rate multiplier. On p.746 a sentence reverses the sign ordering of beta symbols, but the displayed normalized density assigns beta+ to positive marks and beta- to negative marks. | Use the normalized study density: beta values are positive mean magnitudes, with equal sign probability. Keep reciprocal table values as an explicit sensitivity only. | Normalization and the displayed study density resolve the mathematical convention. |
| Merton mark versus log mark | p.742 defines `log(1+J)` as normal, but the log-price SDE writes `J dN`; Table 1 uses `mu_J`, also a drift symbol in Eq. (6). | Use normal log marks `Y`, multiplicative price jumps `exp(Y)`, and compensator `lambda E[exp(Y)-1]`. Retain the table value as the log-mark mean, explicitly identified as an assumption. | The stochastic construction is consistent; the table symbol's intended role remains unresolved. |
| Second derivative coefficient | Eq. (18), p.745, prints an unordered pair sum without a factor 2 and uses an `n`th-derivative label. Eq. (19) applies the Taylor factor 1/2. The two-factor expansion on p.746 requires a factor 2 in the second derivative. | The second derivative is twice the unordered pair sum; its Taylor contribution is the unordered pair sum. GradTwo is singleton sum plus that contribution. | Resolved by direct differentiation and independent mixture-polynomial tests. |
| Terminal interval and Taylor order | The kernel product on p.745 has `N(T)+1` factors. Theorem 1 and its proof, p.746, have inconsistent indexing and a statement that derivatives vanish at order `>=N(T)+1`. | Include the terminal interval. The product degree is at most `N(T)+1`, so derivatives vanish above that degree, not necessarily at it. | Resolved algebraically; do not copy off-by-one indexing into the implementation. |
| Derivative signs in the proof | The two-factor example on p.746 differentiates `(1-theta)p1+theta q1` using `p1-q1` in one term, contrary to Eq. (15). | Use `q_i-p_i` for every derivative, verified by enumerating the full mixture polynomial. | A direct algebraic sign correction; no empirical fitting is involved. |
| Moneyness description | p.746 describes an in-the-money put and an out-of-the-money call, while Table 2 has spot 40 and strike 35. Reversion changes the forward mean and Asian averages differently. | Keep Table 2's spot and strike; record them in the parameter grid. Do not change a contract to enforce an informal moneyness description. | A spot-based reading of the sentence conflicts with the table; it is insufficient to infer a different strike or payoff. |
| No-jump gradient claim | Remark 1, p.745, says gradients vanish when no event is realized. The same remark acknowledges different compensated drifts; Eqs. (6), (8), and (15) retain those differences. | A realized no-jump path still has one compensated local replacement. Do not force its gradient to zero. | Follows the full P/Q kernel construction. A jump-only derivative would define a different target. |
| Diffusion risk adjustment | Eq. (8), p.743, contains `lambda^M`; Table 2 gives no value. | Keep the explicit assumption `lambda^M=0`. | Underspecified; do not choose it to fit a curve. |
| Paths and outer repetitions | p.747 describes 256 paths generally, but Figure 1(a) explicitly says 16,384. Outer counts are 500 and 300. | Use the panel-specific count for Merton, 256 for MRJD, and 500/300 outer runs. Figure 2 uses its printed path grid. | Paper-scale execution is verified from saved replicate IDs. Four-run DEBUG output is now isolated under `outputs/debug/`. |
| Figure 3 data | p.749 and Appendix A compare mean versus median summaries of the ratio experiment. | Figures 1 and 3 share ratio-sweep data; Figure 2 has its own path-count data. | Resolved; already corrected before this review. |
| Randomized gradient implementation | Eqs. (15)-(19) define local sums but do not specify the authors' precise random interval implementation. | Exhaustive baseline; compare uniform-interval randomization on identical paths. | Conditional expectation equality is checked at 72 method settings; equal means do not establish equal power curves. |
| Student-t law and sampling dependence | Eqs. (11), (16), (19) use Student-t conventions; Remark 2 invokes iid CLT arguments; p.748 uses antithetics and stratification. | Preserve `n-1` as the stated replication convention. Label estimated power as plug-in noncentral-t power. Do not claim exact finite-sample t calibration. | Neither nonnormal iid payoffs nor dependent variance-reduced paths give an automatic exact t law. The authors' effective sampling unit and power algorithm remain unknown. |
| Visual reference values | Panel 1(b)'s high-rate endpoint at ratio 1 is clipped above the axis. Panel 1(d)'s visible high-rate marker at ratio 0.67 is about 5.2, not the previously recorded 5.8. | Compare panel b at its visible ratio-0.67 point (about 0.8); revise panel c's endpoint to about 0.37 and panel d's marker to about 5.2. | Approximate raster readings only. These are neither author data nor exact error targets. |

## The revised MRJD mapping

Let `p` be the positive-jump probability, `m=E[J]` the fixed signed mean,
and `a=rho*sigma` the required absolute mean. Then

```
p beta+ - (1-p) beta- = m
p beta+ + (1-p) beta- = a

beta+ = (a+m)/(2p)
beta- = (a-m)/(2(1-p))
```

Positive mean magnitudes require `a > abs(m)`. With Table 2 and `p=0.5`,
`m=-1.03`; all configured ratios are feasible. At ratio 0.20 the means
are `(0.002, 2.062)`, while at ratio 1 they are `(4.13, 6.19)`.
The low-grid feasibility threshold is approximately 0.19961. This agreement
with the grid boundary is a useful consistency observation, not proof of
the authors' intent.

By contrast, preserving beta proportion preserves relative asymmetry but
changes `m`. The earlier proportional baseline is retained as a named
alternative and its previous full results are archived in
`reproduction/before_specification_resolution.zip`.

## Direct price checks and estimator checks

`scripts/07_resolve_specification.py` exports 120 parameter settings and
480 independent expected-price comparisons: every published MRJD grid point
and intensity, five parameter interpretations, and four contracts including
both twelve-date payoffs. The parameter table exposes beta means, signed
and absolute moments, jump variance, intensity, expected event count, and
the realized axis ratio. The absolute-gap variant's nominal x coordinate
does not represent `E[abs(J)]/sigma`; its actual ratio is recorded separately.
No executable mapping is invented for an unspecified author-presentation
variant.

Under the revised baseline, at intensity 0.70 and ratio 1, independently
priced relative differences are approximately 0.1547 (vanilla put),
0.4674 (four-date call), 0.4578 (twelve-date put), and 0.3581 (twelve-date
call). At ratio 0.67, the twelve-date put difference is about 0.2585.
These are ratios of expected prices from quadrature, not medians of
Monte Carlo estimates. They still do not explain the large published
MRJD curves. Selecting the closest-looking interpretation would not
establish a replication.

There is also a distribution-independent check on expected prices. Under
the compensated arithmetic OU construction with zero diffusion risk adjustment,
call and put payoffs are 1-Lipschitz. If
`g = mean_i[(1-exp(-kappa*t_i))/kappa]`, coupling the P/Q paths gives

```
abs(V_Q - V_P) <= exp(-r*T) * lambda * (E[abs(J)] + abs(E[J])) * g.
```

The triangle inequality bounds the decaying compound-jump contribution by
`lambda E[abs(J)] g` and the deterministic compensation by
`lambda abs(E[J]) g`. This bound applies to both European and monitored
arithmetic Asian payoffs. At intensity 0.70 and ratio 0.67, the bound on
the twelve-date put's relative expected-price difference is about 1.5431
(1.2069 for the call). The plotted marker near 5.2 is a median-of-estimates
quantity, so this is not a deterministic bound on that finite Monte Carlo
statistic. It does rule out an expected-price difference of 5.2 under
this specification. All 480 quadrature comparisons satisfy their
corresponding bound, recorded in `direct_prices.csv`.

`scripts/08_compare_mvd.py` enumerates every selected-interval choice on
the same simulated inputs at 36 settings (72 method comparisons). The
largest conditional-mean discrepancy is below `3e-13`. It reports
randomization's added conditional variance separately. Because only the
interval selection is randomized in that comparison, its conditional
residual standard error does not require the underlying simulated paths
to be independent. The check validates the randomized representation;
it does not identify which estimator distribution generated the paper.

## Research status

The revised full run completed in about 8.1 minutes with 214,200 method
records. Each Merton setting has 500 runs and each MRJD setting has 300.
The revised relative median differences at the selected visible reference
points are 0.057702 (panel a, ratio 2), 0.080431 (panel b, ratio 0.67),
0.463874 (panel c, ratio 1), and 0.260139 (panel d, ratio 0.67).
The corresponding approximate paper readings are 0.058, 0.80, 0.37,
and 5.20. The change resolves the mean-preservation inconsistency;
it does not make the MRJD curves numerically match.

The code now implements an explicit, internally consistent interpretation
of the paper. It does not establish one-to-one numerical replication.
The missing author parameter mapping, exact estimator randomization,
and inference/power procedure remain external information gaps. The
inconsistency corrections are supported by equations and contracts,
not by tuning parameters to the plotted outputs.
