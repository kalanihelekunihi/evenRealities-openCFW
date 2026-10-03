# Independent review 2943/001

**PASS_SCOPED**; `accepted` remains false.

I independently reran the 4,608 original-instruction fixtures in a fresh output directory. The source and decoder body hashes match the previously reviewed static map; all replay-output hashes match the receipt. The fixture grid varies type, choice, condition, guard words, flag byte 0/1, clock low bits, and initial PRIMASK. The expected output-table/status oracle is consistent with the original decoder; ordered writes, R1/R2, R4/R5, SP, PRIMASK, and stop state are asserted. The flag dimension exercises the low-bit set/clear path (as `LDRB; LSLS #31; BPL` dictates).

The evidence remains bounded to stable synthetic inputs and original instruction execution. It does not establish volatile mutation/aliasing, physical MMIO behavior, or global ownership.

Candidate receipt SHA-256: `78c9a0bee98c016fa32073cb59049c660914349298d566d404d8fea3213c0024`.
