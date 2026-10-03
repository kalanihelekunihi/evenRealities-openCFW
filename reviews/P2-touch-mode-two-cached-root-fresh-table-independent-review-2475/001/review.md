# Independent review 2475

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-cached-root-fresh-table-2474/001`. Receipt SHA-256 `2311343209bbaf4db3b4038adbaac84833614d4e3eccc5b2501574b73f16d69d`; all four file hashes match, and all five listed spans match the pinned source image.

The isolated replay passed all 160 cases. Original 6AC0, list/pair wrappers, and 8FD0 execute; only 5FC6 is controlled. The first pin call replaces ctx.word0 and changes word8 of the original root to a new table. Assertions show that list traversal and paired port calls use the replacement root, while the dispatcher retains the original root address and later reloads its now-updated word8 for the loader version pointer. The peripheral base remains the earlier cached value. The replacement version 1 causes original 8FD0 to exit before configuration copies; 6AC0 returns 64 and preserves the old mode. The exact calls, preparation/direction writes, absence of peripheral config writes, status, and R4–R11/SP are checked.

**Limits:** This is a controlled pointer-mutation fixture, not evidence that 5FC6 performs this mutation in normal operation. Factory selector behavior is bypassed on the mismatch path. Physical hardware behavior and further mutations/faults remain unresolved. Private evidence only; accepted:false, no canonical admission.
