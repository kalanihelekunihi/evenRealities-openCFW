# Offline case event_flags_offline

Independent C-like reconstruction for synthetic/offline comparison only. See bounded report (`pre-consolidation:g2/analysis/case-event-flags-closure-2026-10-08/REPORT.md`) for provenance, interfaces and explicit execution/model limits. Not production firmware, full-source completion or byte-identical output.

## Deduplication (2026-10-30)

Several files listed above were merged into a single implementation per stock
function; the superseded copies were removed and their names are now typed
aliases (`__attribute__((alias))`) of the kept body. Each kept file notes the
alias with a `Dedup (0x0800xxxx)` comment. The removed files and the decision
log (stock-address groups, differential test results) are under
`build/case-link/dedup/` in the working tree that did the merge.
