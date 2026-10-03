# Independent review 6125

**Result:** PASS_SCOPED.

Source/dependency/artifact hashes match. All instruction bytes match the locked image, and [0x42a08c, 0x42a19c) tiles exactly (272 bytes, 102 instructions) under both the ledger and GNU Thumb disassembly.

The frame is eight bytes; POP returns the saved incoming R7 in R0. Early checks short-circuit to the true byte store: descriptor byte +16 equals 3, shifted word test `(word0 << 2)` nonzero (equivalent to original bits 30-31 nonzero), `(word4 & 0x4c4)` nonzero, or the fresh platform word bit 29 set. Otherwise a child call runs; a nonzero child result gates two fresh low-nibble reads, requiring the first >=1 and the second <3 before setting the flag. If that does not succeed, a 16-entry loop checks per-entry word bit 0 and indexed bitmap bit; eligible channel fields use fresh loads for each successive comparison. Values below 6 or 19..24 match; the >=256/<480 branch passes through two XOR inversions and also matches. A first match writes byte 1; exhaustion writes byte 0.

**Limits:** Static review only; no execution rerun. This does not establish hardware or child semantics, global completeness, canonical admission, or C/freeze gates. Private evidence remains `accepted:false`.
