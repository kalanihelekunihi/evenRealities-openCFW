# Independent review 1907 — extended reset traces

**Result: PASS_SCOPED.** Candidate `touch-storage-reset-extended-traces-1900/002`; receipt SHA-256 `93721715a3d0971ec17e85dc9eaf7e15e9f25a5b42226b3cdd8e6a271c0e4540`.

Candidate receipt and source hash match; the corrected packet records 20 fixtures. Isolated replay passes all 20 and produces byte-identical replays.json.

The original mode-zero traces support the stated path: sequence helper writes 41 and its return is ignored; pointer selection advances from context+24; scratch sequence/checksum are set before initial publication. The optional mirror publication is attempted even when primary publication fails, with primary error precedence. Initial publication errors leave context+24 unchanged. On successful initial publication, later 890C rows and optional mirrors are attempted; a later error is retained while the bounded remaining loop continues. Exact write target order and return/current-row fields in the traces are consistent with this scoped description.

Only count 2/3, one copy and width 128 are covered, with sequence/pointer/checksum/write helpers controlled. These are trace-only observations, not full pseudocode or path coverage; other dimensions, callback mutation, sequence wrap, physical storage/hardware and canonical admission remain unresolved.
