# Independent review 6387

Disposition: **PASS_SCOPED**; `accepted:false`.

All three source extents and packet file hashes match. GNU Thumb decoding confirms the first routine's 24-byte save and 16-byte local area. It captures the literal-pointed word in R4, stages that word, a literal, and tag 64, loads three diagnostic arguments, and calls 0x4176CE; the child return is ignored. It returns the zero-extended predicate `captured_word == 0x55555555`, independently of that child result. The stack stores at SP0/SP4/SP8 overwrite saved incoming R0/R1/R2 slots; ADD SP,#16 discards the local area and POP restores R4/PC.

The next frame-8 routine calls 0x4164DA(0), stores the result at record+0x1C, and freshly checks the slot. Nonzero returns the fresh word. Zero calls 0x41B2F8, stores zero to 0xFFFFFFFF, and loops if that store completes. The leaf at 0x42E276 is BX LR. The wrapper at 0x42E278 saves R7/LR, calls 0x42E53C then 0x42E284, and returns the saved incoming R7 in R0. In 0x42E284, each 0x4161C6 result is passed to 0x4161CE with R1=8 or R1=48 respectively; between those pairs a literal-pointed word is freshly loaded and called indirectly via BLX. It too returns saved incoming R7 through POP R0/PC.

This verifies instruction flow, stack aliasing, and raw call sequence only. No child purpose, hardware/runtime, C-equivalence, or admission claim is made. No canonical files or gates changed.
