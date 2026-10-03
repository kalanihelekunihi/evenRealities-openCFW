# Independent review 6127

**Result:** PASS_SCOPED.

Source/dependency/artifact hashes match. All instruction bytes match the locked image, and [0x42a19c, 0x42a1b2) tiles exactly (22 bytes, 10 instructions) under both the ledger and GNU Thumb disassembly.

The leaf zero-extends R1 and returns immediately when its low byte is not 1, leaving R0 untruncated on that path. When R1 low byte is 1, it zero-extends R0; if R0 low byte is not 2 it returns that truncated R0. If both match, it sets R0 to 1, stores byte 1 through the literal-selected address, and returns 1. No stack frame or child call is present.

**Limits:** Static review only; no execution rerun. This does not establish hardware or child semantics, global completeness, canonical admission, or C/freeze gates. Private evidence remains `accepted:false`.
