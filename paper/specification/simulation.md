# Simulation Design

## Paper-supported design

- P and Q share the initial value and a common probability space (p.742).
- Jump times are stopping times defining the random partition of `[0,T]` (pp.741, 744-745).
- Between successive jumps, couple the two diffusive dynamics; add the jump at its stopping time (pp.742, 744).
- Use common random numbers for paired price comparison (p.744, footnote 2).
- For each estimation approach, use antithetic sampling in the diffusion component and jump times, and stratify the probability that at least one jump occurs (p.748).
- Main estimates use 256 paths; the Merton Figure 1 call panel says 16,384. Pair 1 and Pair 2 use 500 and 300 outer runs, respectively (pp.747-748).

## Not specified

The article does not specify the exact antithetic pairing, whether every jump interarrival or only the first time is antithetic, the event-stratification weights/implementation, whether jump-size marks are antithetic, the RNG, seed, or t-statistic degrees-of-freedom adjustment for dependence. Current code makes choices for these; they are not exact transcriptions.

