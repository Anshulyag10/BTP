# Current Figure Audit

Reviewed saved PNGs and the paper's rendered pages 747 (Figure 1), 748 (Figure 2), and 750 (Figure 3/Appendix A).

| Figure | Current status | Findings |
|---|---|---|
| Figure 1 | DIFFERENT overall | Four cases and two rows per case are present. Panel (a) relative-difference scale is close to the source; panel (b) current max is 0.166 vs visual paper read about 1.2; panel (c) is 0.494 vs about 0.38; panel (d) is 0.464 vs about 5.8. Paper values are approximate image reads. The small-sample power curves are irregular. Current headings/labels, colors, typography, legends, grids and page composition differ from the paper. |
| Figure 2 | NOT REPRODUCED | Conceptual quantities and path grid are present, but the current rejection probabilities are restricted to 0/.25/.5/.75/1 by four outer runs. The article shows smooth repeated-run curves. The saved values are not comparable as a numerical reproduction. |
| Figure 3 / Appendix A | NOT REPRODUCED | Mean power and relative mean price difference are structurally plotted, but the same four-run limitation and unresolved MRJD specification apply. The 12-observation Asian label is inconsistent between panel heading/Example 4 and caption. |

The paper provides curves as plots rather than a numeric source series. The comparison file includes only approximate reads of four price-difference maxima; other values remain unresolved rather than being presented as precise digitization. Plotted reads in `current_results.md` are explicitly approximate.

The root-level `figure1_median_power.pdf` is not a faithful article figure and is not referenced by the current pipeline. The pipeline writes the figures under `outputs/figures/`.

