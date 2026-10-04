# Assumptions and Reconstruction Choices

1. Table 1 `mu_J` is used as the mean of normal log jumps; this is not certain because Eq. (6) uses the same notation for drift.
2. MRJD plotted ratio uses `E|J|/sigma`. The revised mapping fixes `E[J]` and the sign probability and solves both moment constraints for the beta means. This reconciles the axis with the unchanged-mean statement; the incompatible signed-gap ratio is excluded.
3. `lambda^M=0` because no numerical value is printed.
4. Twelve-date case is an Asian put, based on Example 4 and the in-panel heading despite its caption.
5. Seed `20260930` is chosen for determinism; it is not an original author seed.
6. Exhaustive sums are the baseline; optional uniform interval selection reconstructs the MVD weights; the article itself does not provide implementation pseudocode.
7. Noncentral-t estimated power is selected as an interpretation of the described alternative-test power.
8. No correction for dependence among antithetic/stratified samples is applied in the replication convention; its calibration is not paper-validated.

See `inconsistency_resolution.md` for page-level evidence, algebraic corrections, and explicit alternatives.

