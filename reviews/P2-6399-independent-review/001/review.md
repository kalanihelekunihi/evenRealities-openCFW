# Independent review 6399

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and all three source extents match. GNU Thumb decoding confirms E4A0's 32-byte save, alignment branch, and raw call order. The low two bits of input R2 select the early literal return; only the aligned branch subtracts 0x00400000 and shifts right two. It saves the result of 41B8EC at SP4, calls 41BD92, places input R3 at SP0, then calls E8A4(input R0, 1, input R1, transformed R2, fifth argument input R3). It ignores 41BDE4's result, restores the saved PRIMASK, and returns either zero or the child result ORed with 0x08000100. The aligned POP exposes the overwritten SP0/SP4 saved slots as R1/R2; the early path preserves the incoming slots.

E4F4 independently checks input R2's low nibble and input R3's low two bits before tail-calling E4A0; failures return the literal at E510. The E514 leaf truncates to u8, stores 212 or 27 to the referenced words and loops on those paths; all other values return 6. E50E..E514 remains excluded from the claimed code body.

This is static instruction and ABI evidence only. It makes no atomicity, hardware, child-purpose, or admission claim; no canonical files or gates changed.
