Work only inside this isolated openCFW copy. The authoritative read-only Ghidra
corpus is /var/tmp/opencfw-apollo64.A58cAv/full64-j64-auth. Do not access
hardware, sign, flash, erase, or modify any official firmware blob.

Task: turn the authenticated Apollo source-path/Ghidra evidence into a narrow,
reviewable Cordio source-recovery increment. First inspect current docs, tools,
tests, the production-excluded r20.05c snapshot, and production manifests so
you do not duplicate existing work. Use
`tools/analyze_apollo_embedded_source_paths.py` with the corpus and the existing
Cordio version analyzer. Correlate the 36 retained Cordio translation-unit
paths and their function anchors with assertion line numbers, call topology,
constants, and the authenticated public r20.05--r20.05c interval. Keep Ambiq
FreeRTOS/HCI ports and Even glue outside the public upstream boundary.

Implement the highest-confidence bounded result that is genuinely supported:
prefer a fail-closed function/source mapping analyzer and tests; if one small
function has complete ABI, boundary, caller, relocation, and behavioral
closure, add a production-excluded source candidate and host oracle. Do not
edit the production overlay merely to show progress or claim the public tag is
the exact vendor tree. Update relevant research/progress documentation with
exact evidence and uncertainty. Run focused tests and `git diff --check` if
available. Leave all changes in this isolated copy and finish with a concise
list of modified files, tests, evidence, and blockers.
