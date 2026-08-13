Work only inside this isolated openCFW copy. The authoritative read-only Ghidra
corpus is /var/tmp/opencfw-apollo64.A58cAv/full64-j64-auth. Do not access
hardware, sign, flash, erase, or modify any official firmware blob.

Task: turn the authenticated Apollo source-path/Ghidra evidence into a narrow,
reviewable LVGL source-recovery increment. First inspect current docs, tools,
tests, vendored LVGL snapshot, and production manifests so you do not duplicate
already integrated work. Use `tools/analyze_apollo_embedded_source_paths.py`
with the corpus and the existing LVGL version analyzer. Correlate retained
LVGL path anchors, assertion line numbers, call topology, constants, and the
pinned official-history interval with vendored source. You may use official
upstream Git history when local evidence needs a discriminator.

Implement the highest-confidence bounded result that is genuinely supported:
prefer a fail-closed function/source mapping analyzer and tests; if one small
function has complete ABI, boundary, caller, relocation, and behavioral
closure, add a production-excluded source candidate and host oracle. Do not
edit the production overlay merely to show progress. Do not infer whole-file
ownership from `__FILE__` adjacency. Update the relevant research/progress
documentation with exact evidence and explicit uncertainty. Run focused tests
and `git diff --check` if available. Leave all changes in this isolated copy
and finish with a concise list of modified files, tests, evidence, and blockers.
