# Models

Primary source: supplied paper, *European Journal of Operational Research* 298 (2022), pp. 740-751.

## GBM (Example 1, p.742, Eqs. (3)-(4))

Under the equivalent martingale measure, log price `X_t=ln S_t` follows `dX_t=(r-sigma^2/2)dt+sigma dW_t`, with `S_0` common across models. For a lag `u`, the log transition is normal with mean `x+(r-sigma^2/2)u` and variance `sigma^2 u`. Code: `models.merton_base_paths`, which simulates the GBM baseline on contract observation dates.

## Merton (Example 1, pp.742-743, Eqs. (5)-(6))

The log price adds a compound Poisson term. Interarrival times are exponential with rate `lambda`; log jump sizes are normal with parameters denoted `kappa, delta` in the text. The compensator is `gamma=lambda E[J]`, where for a normal log jump with mean `kappa` and SD `delta`, `E[J]=exp(kappa+delta^2/2)-1`. Under the EMM, log drift is `r-sigma^2/2-gamma`. Jumps are inserted at actual event times. Code: `sample_jump_times`, `sample_merton_marks`, `merton_interval_effects`.

Table 1's `mu_J` cannot unambiguously be assigned to the jump-size mean because Eq. (6) also uses `mu_J` for a drift. Current assignment is documented as an interpretation.

## Vasicek (Example 2, p.742, Eq. (7))

Arithmetic OU process `dX_t=kappa(mu-X_t)dt+sigma dW_t`; exact transition mean `mu+(x-mu)e^{-kappa u}` and variance `sigma^2(1-e^{-2kappa u})/(2kappa)`. Code: `mrjd_base_paths`.

## MRJD (Example 2, p.743, Eq. (8))

`dY(t-) = kappa(mu-lambda^M sigma-lambda E[J]/kappa-Y(t-))dt + sigma dW(t)+JdN(t)`. The numerical double-exponential jump density has positive/negative exponential mean magnitudes `beta+`/`beta-`; paper's study density assigns one-half mass to each sign. Code: `sample_double_exponential_marks`, `mrjd_interval_effects`.

The `lambda^M` number is absent from Tables 1-2. Current config sets it to zero; this is not paper-specified.

