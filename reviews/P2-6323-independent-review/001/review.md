# Independent review 6323

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and pinned-source hashes match. GNU Thumb decoding confirms the exact 0x42D562–0x42D5CC code. The dispatcher saves R4/LR in an eight-byte frame, zeroes R4, and truncates the input mode to a byte. Mode 0 checks R2 for null, then checks its byte for exactly 2; only that case calls 0x42CFE0, whose return is ignored. Mode 1 does not null-check R2: byte 0 routes to 0x42D3BC and a nonzero byte is passed, zero-extended, to 0x42D104; either child return is retained in R4 and returned. Mode 2 calls 0x42CED8 with R2 and returns its result. The explicit branches for modes 3 through 6 and values at least 7 reach the zero-result return without a child call. The adjacent leaf stores byte value 1 to its literal-selected address and returns zero.

Source-level routing only; child behavior, hardware meaning, C equivalence, and admission are not established. No canonical files or gates changed.
