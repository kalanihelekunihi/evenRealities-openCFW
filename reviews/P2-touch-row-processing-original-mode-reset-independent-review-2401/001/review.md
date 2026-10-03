# Independent review 2401

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-row-processing-original-mode-reset-2398/001.

Independent isolated replay passes 512 cases; output hash matches pinned replays.json.

Original 6AC0(0,ctx), 7984, sequence helpers, predicate and division execute. Exact mode reuse/reset/unsupported-mode outcomes and the parent’s ignored mode status are consistent with instructions; ordered stores and registers pass.

**Limits:** Only representative old-mode/flag values and valid supplied pointer tables are covered; other helpers remain controlled. Private bounded evidence only; accepted:false.
