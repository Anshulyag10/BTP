# Option Payoffs

Paper p.746, Examples 1-4:

1. European call: `max(S_T-K,0)`.
2. European put: `max(K-S_T,0)`.
3. Discrete arithmetic Asian call: `max((1/o) sum_i S_i-K,0)`.
4. Discrete arithmetic Asian put: `max(K-(1/o) sum_i S_i,0)`.

For pair 2, monitoring dates are equally spaced `t_i=iT/o`; Example 3 uses four observations and Example 4 twelve. The 12-observation panel heading identifies a put; its Figure 1/2 subfigure caption says call. Current code follows Example 4 and panel heading. Payoff implementation is in `src/replication/payoffs.py`.

