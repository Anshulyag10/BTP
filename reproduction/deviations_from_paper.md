# Remaining reconstruction choices

1. The MRJD plotted ratio E|J|/sigma conflicts with the signed-gap ratio in Section 4.
   The revised baseline follows the axes and preserves the signed mean and sign probability.
   This reconciles two statements; the authors' actual mapping is still unverified.
2. Merton mu_J is treated as the log-jump mean; the drift notation is overloaded.
3. The unspecified MRJD diffusion risk premium is zero.
4. The twelve-date Asian option follows the put formula and panel heading, not the call caption.
5. Exhaustive derivatives follow the kernel equations. The no-jump remark conflicts with
   the compensated singleton replacement, and the authors' randomized implementation is unknown.
6. Path-level n-1 t inference and plug-in noncentral-t power remain reconstruction choices.
   Calibration results are in ../outputs/validation/inference_calibration.csv.
7. The authors' seed, software, and numerical curve data are unavailable.

The paper repetition counts have now been run, and Figure 3 uses the correct ratio sweep.
Neither change resolves the remaining MRJD price or power-curve discrepancy.
