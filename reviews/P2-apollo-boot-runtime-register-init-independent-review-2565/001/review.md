# Independent review 2565

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-runtime-register-init-2564/001` binds to the locked source. I checked the body and literal-pool hashes against the source, and the receipt/artifact hashes match. An isolated replay passed all 18 cases.

The body `[0x41CC04,0x41CC48)` is a leaf with seven ordered peripheral writes and two reads. The six literal words match the pointers listed in the packet. The replay checks the first pointer’s bit-0 clear then overwrite with `0x110`, the writes of `0x100`, `0xFFFFFFFF` twice and `0xC0000000`, and the final read/OR-`0x40000000` write. It verifies incidental R0 as the final pointer, R1 as the final updated word, PRIMASK, SP and high-register preservation across the selected patterns.

This confirms instruction-level RAM-mapped behavior only. Peripheral meaning, hardware side effects between reads, write readback semantics, installation and caller ownership remain unverified. The parent’s ignored return is separate evidence. Private evidence only; accepted:false and no canonical admission.
