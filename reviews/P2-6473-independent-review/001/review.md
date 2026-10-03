# Independent review 6473

Disposition: **PASS_SCOPED**; `accepted:false`.

The F530..F5F0 source slice and packet hashes match. GNU Thumb decoding confirms the continuation's 24-byte frame and six ordered selected-byte updates. R1 and R0 are independently truncated to u8 and drive each selection; each branch loads a byte from one of two literal-backed locations, and the selected byte is freshly paired with a destination word for BFI/store. The order is: R1-selected five-bit field at bits25..29; R0-selected field at bits11..15 in the same word; R1-selected field at bits8..12 in another word; R0-selected field at bits17..21 in another; then R1-selected bits25..29 and R0-selected bits11..15 in a further word. Boolean registers are used live and are not overwritten until their final selection.

The captured original bit0 in R5 is u8-tested. If nonzero, a fresh R4 word is ORed with 1 and stored, then 41D1C0(5) and 41C838(1) are called in that order. Both results are ignored. The body returns zero and restores R4-R8/PC from its frame.

This verifies the literal selections, BFI order, and call sequence only. No table/hardware semantics or atomicity are inferred; canonical files and gates remain unchanged.
