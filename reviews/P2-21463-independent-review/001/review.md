# Independent review — P2-21463

Status: partial; accepted: false.

Fresh replay passed for the exact 152-byte span, and regenerated instructions/references match the candidate. The wrapper at 0x484A7E saves a 16-byte frame, calls 4D4892 then 4D489E with the recorded shared arguments/live registers, and POP {R0,R4,R5,PC} returns saved entry R3. The zero halfword at 0x484A96 is inter-function padding.

The following routine opens a 32-byte frame and independently rereads the object flag byte before each of the three field-copy decisions. Each path stages a word at SP0 and calls 439BE4 with destination +48, +51, then +54 and length 3. The first two helper choices and their arguments match the recorded branches. On the third field, the clear-bit branch reaches 441094 with R0 still zero from the LSLS-by-31 flag shift; the set-bit branch loads the separate literal and calls 44104C. The mapped prefix ends with the third copy call; the frame remains open.

Helper effects beyond observed live register state and the following continuation remain unresolved. Review remains partial/unaccepted.
