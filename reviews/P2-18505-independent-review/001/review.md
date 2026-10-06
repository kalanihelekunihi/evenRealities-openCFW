# Independent review P2-18505

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 106-byte continuation `0x46082E..0x460898`; instruction/reference manifests match. The error route at entry writes `0xFFFFFFFF` to R0 and branches to `0x460D56`. The success route reads byte fields from retained R7 in order: byte 0 into R5, byte 1 into R4, and halfword +2 into R6, replacing the previous length/buffer/input values.

The first fresh flag sequence controls whether the diagnostic block writes low16(R6), low8(R4), low8(R5), a literal, and 414 to SP16/SP12/SP8/SP4/SP0 before calling `0x43D574`. Those offsets are local frame locations. A separate fresh mask sequence tests bit 0 and conditionally bit 2. The second logger route sets R1 from literal `0x461360`, writes low16(R6) to SP4 and low8(R4) to SP0, and passes low8(R5) in R3. These stack stores happen after the first diagnostic and overwrite SP0/SP4 only. R4/R5/R6 retain the sampled header fields across the calls.

Fresh flag reads, stack argument ordering, and branch targets are confirmed; later mask setup, child call, dispatch, and epilogue are outside this span. Partial/unaccepted only.
