# Independent review 6375

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet/source hashes match for 0x42E048–0x42E104. GNU Thumb decoding confirms this closes the 88-byte frame from 0x42DE58. On the main path it emits diagnostics tagged 558 and 559 using separate fresh reads of the word at the global pointer's offset 20, plus the next word at offset 24. It then calls 0x42DDF2 (ignored), freshly loads offset 20, calls 0x42DC90, and if that indirect transfer returns, branches back to the request at 0x42DE9E.

The alternate path at 0x42E092 compares fresh SP16 message data with a fresh global offset-20 pointer. Mismatch goes to the request loop. Match stores 0x00438000 at record+20, freshly dereferences the stored pointer, and tests bit 29 via LSLS #2; clear returns to the request loop. If set, it emits diagnostics tagged 567 and 568, calls 0x42DDF2, then 0x42DC90 with the freshly loaded pointer. A return from the transfer call branches back to the request loop. As in the main path, diagnostics and setup-child results are ignored.

At 0x42E0FE, the request-child nonzero path discards 56 local bytes and restores R4–R10/PC from the 88-byte frame while leaving the child result in R0. This is the observed return path; other continuation paths are outside the extent. Because 0x42DC90 changes SP from its input buffer, ordinary stack restoration after a hypothetical return is not established. No physical transfer, hardware, child-purpose, C-equivalence, or admission claim is made; no canonical files or gates changed.
