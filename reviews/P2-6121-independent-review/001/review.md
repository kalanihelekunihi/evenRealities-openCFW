# Independent review 6121

**Result:** PASS_SCOPED.

The packet and dependency hashes match, all bytes equal the locked image, and GNU Thumb disassembly confirms the 46-byte extent [0x42a04a, 0x42a078) as 17 instructions. The frame saves R7/LR; the result of 0x41b8ec is written to SP0. A fresh byte read dispatches value 2 to 0x428378; otherwise a second fresh byte read dispatches value 7 to 0x428a94. Both paths converge on 0x41ccd6. The code then reloads SP0 into R0, writes it to PRIMASK, and POPs that same saved value into R0 while restoring PC/SP. Input R0 is not explicitly forwarded to the first call.

**Limits:** This verifies instruction flow and register/mask operations, not child meanings, architectural/hardware effects, or a caller ownership contract. Static review only; no execution rerun. Private evidence remains `accepted:false`; no C/admission change.
