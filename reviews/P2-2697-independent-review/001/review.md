# Independent review 2697 — indexed state popcount

**Result: PASS_SCOPED.** The candidate’s pinned source and all three artifact hashes match their receipt. I independently replayed its verifier into `analysis/replay-2697-independent`; all 712 original-instruction fixtures passed.

The disassembly at `0x421584–0x4215AE` matches the documented SWAR population count: successive masks `0x55555555`, `0x33333333`, and `0x0F0F0F0F`, followed by multiplication by `0x01010101`, extraction of the high byte, and `UXTB`. The helper returns the number of set bits for the tested 32-bit inputs and does not access memory. The body is exactly 42 bytes and its SHA-256 matches the receipt.

At `0x4215FE–0x421632`, the routine truncates the operation to its low byte, reads two adjacent words from `0x20026E74 + 8*(operation & 0xFF)`, calls the original popcount helper for each word, accumulates both results, narrows to a byte, and restores the saved registers/frame. The 448 aggregate cases confirm the ordered word reads and calls, including low-byte aliases and selectors outside the observed operation set. The 264 leaf cases include eight boundary patterns and 256 deterministic random words. Both body ranges match the receipt hashes; no calls were intercepted.

The aggregate’s table is synthetic in this replay, so this does not establish valid operation bounds, table provenance, or caller behavior. The fixtures also do not establish aliasing, concurrent mutation, or hardware behavior. This is private evidence only: `accepted` remains false and no canonical admission or whole-image completeness is claimed.
