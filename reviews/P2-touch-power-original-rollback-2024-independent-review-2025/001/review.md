# Independent review 2025

**Result:** PASS_SCOPED.

- Source and artifact pins match; isolated replay reproduced all 32 rows exactly.
- On successful probes, all three callbacks run in mode 1, the optional mode-4 pass runs under PRIMASK 1 unless skipped, the original WFI leaf executes under PRIMASK 1, and mode 8 traverses 2,1,0 after mask restoration.
- For a sentinel at node k, probing stops at k; mode-2 rollback walks only predecessors in reverse order (k-1..0), WFI is not reached, and the wrapper retains the sentinel result even when controlled rollback callbacks return zero. Frame and entry PRIMASK restore.

**Limits:** Synthetic callbacks and WFI continuation are controlled; this does not establish physical wake, callback behavior or concurrency. No canonical admission is made.
