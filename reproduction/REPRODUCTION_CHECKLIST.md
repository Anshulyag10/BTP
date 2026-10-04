# Reproduction checklist

- [x] Preserve the legacy simulation and DEBUG outputs.
- [x] Correct Figure 3 to use the ratio sweep and mean aggregation.
- [x] Use exhaustive kernel derivatives as the baseline; retain randomized selection as an option.
- [x] Apply discounting and validate the zero-jump boundary.
- [x] Run 500 Pair-1 and 300 Pair-2 outer repetitions.
- [x] Verify model laws, mixture derivatives, experiment grids, and independent MRJD option prices.
- [x] Format/lint source and shorten comments.
- [x] Regenerate and inspect Figures 1-3.
- [x] Quantify the remaining discrepancy using explicitly approximate paper readings.
- [x] Select and document a consistent MRJD parameter construction and compensated no-jump convention.
- [x] Compare call/put and parameter interpretations with independent prices and full parameter tables.
- [x] Verify randomized MVD conditional expectations against exhaustive sums on identical paths.
- [x] Isolate DEBUG data, figures, metadata, and manifest from the paper-count outputs.
- [ ] Verify the selected MRJD construction against the authors' actual experiment.
- [ ] Resolve the paper's power calculation and dependent-sample inference.
- [ ] Establish numerical agreement of all published curves before comparing new approaches.
