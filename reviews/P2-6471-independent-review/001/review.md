# Independent review 6471

Disposition: **PASS_SCOPED**; `accepted:false`.

The F4B2..F530 body and packet hashes match. GNU Thumb decoding confirms a 24-byte frame preserving R4-R8/LR. It captures a fresh hardware bit0 in R5. If set, it calls 41C838(0) and 41D1C0(5), ignores both results, then freshly clears the hardware word's bit0. The captured bit remains available in R5 for the continuation.

It truncates input R0 to u8: zero selects row 0. Otherwise it truncates input R1; zero selects row 1, nonzero row 2. It computes row*3 from the literal table base and loads byte at offset +1, producing R1=1 only when the byte equals 1. It recomputes row*3 and loads offset +2, producing R0=1 only on exact equality to 1. It then freshly reads a distinct literal-backed hardware word, ORs bit31, and stores it. The packet ends before the following control flow.

This verifies the listed calls, row/byte selection, and ordered stores only. No interrupt-mask operation, table purpose, hardware semantics, or atomicity is inferred. No canonical files or gates changed.
