# Independent review 6087

**Result:** PASS_SCOPED.

The locked image and dependency/artifact hashes match. Every recorded instruction byte equals the image bytes, and the body exactly tiles [0x429962, 0x4299fc) (154 bytes, 61 instructions). Independent GNU Thumb disassembly agrees with the ledger boundaries and branch/load/store effects.

The first adjustment reads a fresh row byte, masks to seven bits, subtracts R9 modulo 2^32, and doubles the wrapped delta unconditionally. It adds back R9 and applies unsigned saturation at 128; R9 is unchanged. Thus a negative mathematical difference wraps rather than being clamped. The second adjustment computes R8-R7 modulo 2^32, doubles only for signed delta >= 1, sums with R7, and applies the same unsigned saturation; R7 updates only on the nonsaturating path. The code then calls the delay helper with 50, merges original R8 into the low seven bits of a fresh register word, inserts fresh row fields into a fresh word, and calls the delay helper with 5. Those child results are ignored; subsequent control flow is outside this packet.

**Limits:** Static review only; no execution rerun. These packet-local instruction/register/stack observations do not establish packed-channel meaning, child or hardware behavior, global completeness, canonical admission, or freeze/C gates. Private evidence remains `accepted:false`.
