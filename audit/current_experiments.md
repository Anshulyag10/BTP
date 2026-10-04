# Current Experiment Audit

| Setting | Paper | Saved DEBUG run | Configured paper mode |
|---|---:|---:|---:|
| Type-I error | 0.10 | 0.10 | 0.10 |
| Primary paths | 256 | 256 except Figure 1 Merton call | Same |
| Figure 1 Merton call paths | 16,384 | 16,384 | 16,384 |
| Outer repetitions, Pair 1 | 500 | 4 | 500 |
| Outer repetitions, Pair 2 | 300 | 4 | 300 |
| Figures 2/3 path grid | 64 through 16,384 | 64 through 16,384 | Same |
| Jump rates | 0.01, 0.08, 0.70 | Same | Same |
| Figure 1 ratio grids | As printed | Transcribed | Same |
| Figure 2/3 fixed ratio | Pair 1: 0.50; Pair 2: 0.33 | Same | Same |
| Seed | Not supplied | 20260930 | Local deterministic choice |

The saved DEBUG run contains 2,448 replicate-method rows and 612 summaries. Each plotted case has four outer repetitions. Therefore Figure 2 rejection probabilities are quantized in quarters. The run metadata records start/end timestamps, runtime, environment, counts, validation outcomes and limitations; the reproduction manifest hashes configuration, paper, source/test/scripts and generated outputs.

The CLI has `DEBUG`, `VALIDATION`, and `PAPER_REPLICATION` modes. Full mode maps 500 repetitions to Pair 1 and 300 to Pair 2, but exits before simulation because `paper_replication_ready=false`. That gate is intentional: numerical Figure 1 discrepancies, estimator-distribution fidelity and dependence-aware inference remain unresolved. The paper-scale experiment has not been run.
