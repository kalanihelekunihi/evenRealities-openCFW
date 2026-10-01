# Independent review 1917 — reset geometry traces

**Result: PASS_SCOPED.** Candidate `touch-storage-reset-geometry-traces-1910/003`; receipt SHA-256 `70172b67b9b3b623bfaba3148b94f599f878da9e7a0da49f0930f21158862242`.

Receipt source pin matches; the corrected candidate records 120 fixtures and its artifact hashes agree. Isolated replay passes all 120 traces and byte-matches candidate output. Review binds to 1910/003, not the superseded 002 wording.

Traces vary count 1/2/3, copies 1/2, width 64/128, mirror disabled/enabled, and write-failure position. Original sequence, checksum, and 810C pointer helpers execute; writes alone are controlled. Observed call count follows count×copies, initial-row successor selection and later pointer wrap agree with the modeled geometry, and optional mirror destinations use the captured row count and width. Status precedence and continued later writes match the bounded traces.

The corrected description says remaining iterations are captured product(count×copies) minus one, which matches the 003 fixtures with copies=2. It does not rely on the earlier copies=1-only prose in 002.

Trace-only fixture ranges; no full extended-mode pseudocode or completeness claim. Write helpers are controlled, and dimensions outside the tested sets, callback mutation, physical storage/hardware and canonical admission remain unresolved.
