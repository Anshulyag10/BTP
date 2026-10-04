# Current ambiguity register

The reviewed evidence, algebra, and decisions are in `inconsistency_resolution.md`.
This register supersedes the earlier debug-era audit.

| Topic | Current decision | What remains unknown |
|---|---|---|
| MRJD ratio and beta scaling | Follow E|J|/sigma while preserving signed E[J] and sign probability. Require an explicit mode. | Authors' executed mapping; the signed-gap prose conflicts with the positive axis. |
| Twelve-date contract | Put from Example 4 and figure headings; call retained as sensitivity. | Which contract generated the source data. |
| Jump density | Normalized double exponential with beta as mean magnitude and p=0.5. | No ambiguity in the displayed study density; nearby prose/general-density typos are documented. |
| Merton table mu_J | Treat as normal log-mark mean; compensate using E[exp(Y)-1]. | Table symbol also denotes drift in the model section. |
| MRJD lambda^M | Explicit zero assumption. | Its numerical value is not supplied. |
| Gradient pair coefficient | Second derivative has factor 2; Taylor contribution is one unordered pair sum. | Authors' executable implementation. |
| No-event gradients | Retain compensated local drift, following the full P/Q kernels. | Whether author code instead measured a jump-only derivative. |
| MVD randomization | Exhaustive baseline; randomized conditional expectation verified on shared paths. | Authors' interval randomization and estimator variance. |
| Variance reduction / inference | Antithetic diffusion and times; independent marks; stratified occurrence; path-level n-1 convention. | Exact strata, pairing, effective sampling unit, and dependence-adjusted standard errors. |
| Power | Explicit plug-in noncentral-t calculation with a recorded null-calibration limitation. | Authors' noncentrality/power estimation procedure. |
| Numerical comparisons | Re-read visible raster markers; avoid clipped endpoints. | Exact author figure arrays and seeds are unavailable. |

The 500/300 outer-count and Figure 3 data-routing issues are corrected. DEBUG uses
four runs and separate output directories; it is not the current full experiment.
