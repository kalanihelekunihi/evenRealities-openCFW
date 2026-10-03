# Independent review 6379

Disposition: **PASS_SCOPED**; `accepted:false`.

Hashes match for 0x42E1C4–0x42E1EC. GNU Thumb decoding confirms the first routine's eight-byte frame and control flow: it saves input R0 in R4, tests bit 22 with LSLS #9, and if set calls 0x42DE58 (ignoring its result). It next tests bit 23 with LSLS #8 and if set calls 0x42E1DA; otherwise it returns the shifted value R4<<8 in R0 through POP R4/PC. The child calls may not return, which remains outside this static decode.

The second routine saves R7/LR, calls 0x42E444(1) and ignores the result, then repeatedly loads 0xFFFFFFFF into R0, calls 0x416378, ignores the result, and branches back to repeat. There is no epilogue in this loop body and no fixed local status return.

No purpose, hardware/runtime, C-equivalence, or admission claim is made. No canonical files or gates changed.
