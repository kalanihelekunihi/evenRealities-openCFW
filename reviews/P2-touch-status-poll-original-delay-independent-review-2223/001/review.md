# Independent review 2223

**Result:** PASS_SCOPED.

The source, code range [0x6608, 0x664A), and receipt files match their hashes; the stored listing agrees with Thumb/M-class decoding.

An isolated replay regenerated all 72 fixtures exactly. Original 6608, A324 and 4480 execute without helper interception. The model supplies scale byte 2, so delay argument 1 becomes leaf input 2 and yields one loop iteration. Fixtures verify status mutation at selected delay-entry observations, budget/mode boundaries, status reads, delay counts, return values and R4/SP.

The mask/wanted calculation and fresh pointer-chain reads match the decoded poll loop. A mismatch returns 0; a matching value with exhausted budget returns 4; otherwise the original delay wrapper runs and the reduced budget is polled again.

**Limits:** Status changes are injected at delay-entry observations; this does not establish hardware timing, readiness or physical MMIO behavior. Scale provenance, pointer mutation and concurrency remain unresolved. No canonical admission is made.
