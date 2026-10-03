# Independent review 6085

**Result:** PASS_SCOPED.

The locked image and dependency/artifact hashes match. Every recorded instruction byte equals the image bytes, and the body exactly tiles [0x4298d0, 0x429962) (146 bytes, 50 instructions). Independent GNU Thumb disassembly agrees with the ledger boundaries and branch/load/store effects.

The active path is the 60-poll loop: it freshly reads the status word and delays/increments while bit 30 is clear, then exits via the helper on bit-set or limit; the inactive path bypasses polling. It publishes argument/index and fresh row fields, then computes delta as fresh SP4 metadata minus R10. A signed delta >= 1 is doubled, the sum is checked unsigned against 128, and saturation sets the low seven bits to ones; otherwise the sum replaces those bits and updates R10. SP4 remains unchanged. The continuation lies beyond this packet.

**Limits:** Static review only; no execution rerun. These packet-local instruction/register/stack observations do not establish packed-channel meaning, child or hardware behavior, global completeness, canonical admission, or freeze/C gates. Private evidence remains `accepted:false`.
