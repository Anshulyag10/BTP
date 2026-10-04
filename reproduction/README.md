# Reproduction records

The latest simulation uses the published 500/300 repetition counts. This records a completed
paper-count run, not verified numerical agreement. See ../outputs/final_replication_report.md.

experiment_log.csv records actual executions. reproducibility_manifest.json hashes the current
source, configuration, paper, environment lock, and output snapshot. Validation-only executions
use validation_manifest.json and preserve the full experiment metadata.

legacy_baseline/ preserves the original simulation and four-repetition DEBUG results.
before_specification_resolution.zip preserves the subsequent full run that used
proportional beta scaling. The current baseline keeps the signed jump mean fixed.
DEBUG executions now write outputs/debug/ and debug_manifest.json.
