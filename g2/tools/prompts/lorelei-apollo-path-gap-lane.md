Work only inside this isolated openCFW copy. The authoritative read-only Ghidra
corpus is /var/tmp/opencfw-apollo64.A58cAv/full64-j64-auth. Do not access
hardware, sign, flash, erase, or modify any official firmware blob.

Task: investigate the 43 retained C source paths that the current
`tools/analyze_apollo_embedded_source_paths.py` report cannot correlate to a
Ghidra-discovered function, plus obvious function-discovery gaps exposed by
their pointer cells. Distinguish unused data/literal pools from missed Thumb
functions. Use raw decoding, Ghidra scripts, Rizin/Capstone, vector/call xrefs,
and neighboring authenticated function boundaries. Run independent shards in
parallel where useful, but keep all writes inside this isolated copy.

Implement a deterministic, fail-closed recovery tool and tests for any
promotable findings. Seed/decompile new functions only when entry evidence is
independent of path adjacency. If recovered semantics are strong enough, add
a production-excluded clean-room source candidate for one small bounded leaf;
do not modify the production overlay without complete ABI/caller/relocation
and behavioral closure. Update research/progress/memory documentation with
per-path state: function-anchored, path-only data, missed-code candidate, or
recovered function. Run focused tests and `git diff --check` if available.
Leave all changes in this isolated copy and finish with modified files, tests,
evidence, and blockers.
