# Independent review 1919 — unaligned-width reset traces

**Result: PASS_SCOPED.** Candidate `touch-storage-reset-unaligned-width-traces-1912/001`; receipt SHA-256 `36bf33d256843890328ef96c88f68eb47f7e6d7bc2b48af215632b87a994532b`.

Receipt/source binding and 240-fixture artifact hashes agree. Isolated replay passes all fixtures and byte-matches candidate replays.json.

Traces execute original sequence/checksum/pointer routines with only 8554/890C write calls controlled. Across widths 64, 127, 128, and 129, pointers advance by width rounded down to a multiple of four, while the wrap limit is based on total captured width (N×width). Mirror offset uses N times the rounded step. Fixture-derived addresses match these formulas for count×copies totals and show wrap behavior; write failure order and current-row/result observations match the recorded bounded traces.

This remains trace evidence for the finite tested combinations, not full extended-mode pseudocode or coverage. Helpers for writes are controlled; dimensions beyond listed widths/counts/copies, callback mutation, physical storage/hardware and canonical admission remain unresolved.
