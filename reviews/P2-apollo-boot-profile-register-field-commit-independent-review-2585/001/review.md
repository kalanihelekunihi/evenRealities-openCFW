# Independent review 2585

**Result: PASS_SCOPED.**

The candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-profile-register-field-commit-2584/001` is bound to the pinned source. The receipt, artifact hashes, body `[0x42AB7C,0x42ABB2)` and pointer literals match. I replayed it into an isolated output directory; all 54 original-instruction fixtures passed.

The dispatch guard mismatch returns zero without MMIO reads or writes. On a match, the leaf inserts state word32 bits 7–16 into register `0x40020080` bits 0–9, word104 bits 2–7 into `0x40020088` bits 0–5, and word104 bits 0–1 into `0x400201B0` bits 15–16, preserving unrelated register bits. The independent bit-insertion oracle checks all three ordered read/write pairs for the tested state and initial-register patterns, along with zero return, SP and high registers.

The routine executes original code with RAM-mapped peripheral fixtures. The report does not validate physical register meaning, hardware effects, concurrency, or enclosing ownership. Its loads are executed sequentially against stable state; it does not model concurrent change to word104 between the two source reads. Private evidence only; accepted:false and no canonical admission.
