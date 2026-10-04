# Parameters

## Table 1: Model Pair 1 (paper p.746)

Contract: `S0=40`, `K=40`, `T=1`. Both null GBM and alternative Merton use `r=0`, `sigma=1.698e-2`. Merton intensities: `{0.01,0.08,0.70}`. Table shows `mu_J=-3.3e-5`, `delta=3.347e-2`. Mapping `mu_J` to normal log-jump mean is an interpretation because Eq. (6) also names a drift `mu_J`.

## Table 2: Model Pair 2 (paper p.746)

Contract: `S0=40`, `K=35`, `T=1`. Vasicek/MRJD: `r=0`, `kappa=.24`, `mu=.63`, `sigma=5.16`. MRJD rates `{.01,.08,.70}`, `beta+=3.48`, `beta-=5.54`. The study's displayed density implies `pi+=pi-=1/2`; this is paper-specified for the numerical setup. Betas are exponential means, not rates.

## Sweeps / repetitions (paper pp.747-748)

Pair 1 x grid `{.25,.40,.50,.63,.79,1.00,1.59,2.00}` for `lambda/sigma`. Pair 2 plotted x grid `{.20,.25,.29,.33,.40,.50,.67,1.00}` for `E|J|/sigma`; the adjacent prose instead writes `lambda/(beta+ - beta-)`. `n=256` primary estimates; Figure 1's Merton vanilla-call panel explicitly says 16,384 paths. `N=500` Pair 1, `N=300` Pair 2. Figure 2 path grid is `2^6,...,2^14`.

## Not supplied

Original random seed; `lambda^M`; exact random-number generator/stream; numerical tolerance; complete numeric Figure 1-3 curve data; exact stopping/antithetic/stratification randomization details beyond the broad statements in Section 4.

