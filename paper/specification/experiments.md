# Experiments

Section 4 (pp.746-749) compares GBM/Merton on an ATM vanilla call and Vasicek/MRJD on vanilla put, four-observation Asian call, and twelve-observation Asian put. Rates are `{.01,.08,.70}`. Pair 1 modifies volatility with jump rate; Pair 2 modifies both jump-size means while holding sign probability fixed. Figures report median power/relative median estimate (Fig. 1), rejection probability/median power against path count (Fig. 2), and mean power/relative mean estimate (Appendix Fig. 3). CRN t-test tolerances are stated as `.1%`, `.2%`, `.5%` of diffusion price in p.749; Figure 1 and Figure 3 captions set `.2%`. Current config includes one `.2%` CRN alternative for all runs; the paper does not make clear how the three tolerance values map to all curve series.

The general prose says 256 paths, while Figure 1(a) explicitly prints 16,384; the panel-specific count is used for Merton. The full saved experiment uses 500 Pair-1 and 300 Pair-2 independent runs at each setting. Four repetitions apply only to DEBUG, whose outputs are isolated. Figures are generated from saved simulation rows, not hard-coded coordinates.

