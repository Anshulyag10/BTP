# Statistical Tests and Power

The paper tests two-sided hypotheses at `alpha=0.10` in Section 2.3-2.4. CRN uses paired pathwise differences; its statistic is a centered sample mean divided by the sample standard error and compared with a Student-t critical value with `n-1` degrees of freedom (Eq. 11). The practical alternative subtracts `delta=d(P-O)` (Eq. 12). GradOne tests the first derivative equal to zero (Eq. 17); GradTwo tests the Taylor sum of first and half second derivative equal to zero (Eqs. 19-20).

Code uses exact `scipy.stats.t.ppf`, a paired/one-sample t statistic, and `scipy.stats.nct` tail probabilities. The article describes power as the probability under the alternative that the statistic falls outside the null rejection region; it does not give a fully explicit noncentrality-estimation recipe. Current noncentral-t power is therefore an interpreted implementation, not independently verified as the authors' calculation.

Important unresolved detail: paths are antithetic and jump-occurrence-stratified in the paper, but the article continues to state `n-1` degrees of freedom and does not explain whether antithetic pair means or strata are the independent units. Current code treats individual path rows as iid; this must be investigated before final inference claims.

