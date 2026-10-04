# Current Parameters Audit

## Model Pair 1: GBM / Merton

Transcribed Table 1 values in `config/experiments.json`: `S0=40`, `K=40`, `T=1`, `r=0`, `sigma=0.01698`, `lambda in {0.01,0.08,0.70}`, `mu_J=-3.3e-5`, `delta=3.347e-2`. The implementation maps `mu_J` to the normal log-jump mean and `delta` to its standard deviation. This is plausible but the paper also defines a `mu_J` drift symbol in Eq. (6); record as AMBIGUOUS, not exact.

The plotted Pair 1 ratio grid is `{0.25,0.40,0.50,0.63,0.79,1.00,1.59,2.00}` and source Figure 1 labels it `lambda/sigma`. Code sets `sigma=lambda/ratio`, consistent with that interpretation.

## Model Pair 2: Vasicek / MRJD

Table 2 values: `S0=40`, `K=35`, `T=1`, `r=0`, `kappa=0.24`, `mu=0.63`, `sigma=5.16`, `lambda in {0.01,0.08,0.70}`, `beta+=3.48`, `beta-=5.54`. The asymmetric double-exponential density associates beta-plus with positive jumps and beta-minus with negative jumps; each is a mean magnitude. The numerical-study specification uses equal sign probabilities in its displayed density. Code uses `pi+=pi-=0.5`.

Current sweep scales both beta means so `E|J|/sigma` equals the plotted x value. However, the paragraph after Figure 1 also states an analysis ratio `lambda/(beta+ - beta-)`. These two rules do not determine the same parameter sweep. The plotted axis/grid and prose conflict must remain visible.

Equation (8) contains a diffusion market-price term `lambda^M sigma`, but the numerical tables supply no value. The current code sets `lambda^M=0`; that is an explicit reconstruction choice. The 12-observation payoff is implemented as an Asian put, following Example 4 and the in-panel heading; its subfigure caption says call.

