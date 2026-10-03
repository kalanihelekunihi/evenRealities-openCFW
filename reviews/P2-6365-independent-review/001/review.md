# Independent review 6365

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and source-body hashes match for 0x42DE0E–0x42DE58. GNU Thumb decoding confirms a 16-byte save plus 16 local bytes (32-byte frame). It stages the literal and tag 505 for 0x4176CE(1, literals...), ignoring that result. It loads the literal-selected word, calls 0x41B8EC, and retains the returned mask in R5. It then calls 0x4156AC(SP, template literal, 16), ignores the result, followed by 0x42E4F4(literal word, SP, R4, 4), also ignoring the result. It restores PRIMASK from R5, sets R1 and R0 to zero, then calls 0x42E514(0,0); that final child result remains in R0. The epilogue adds 20 to SP, discarding the 16-byte local area and saved incoming R3, then pops R4/R5/PC.

This verifies call order and raw ABI only; it does not assume what the template child writes or what the callees mean. No fixed zero return, C equivalence, or admission is claimed. No canonical files or gates changed.
