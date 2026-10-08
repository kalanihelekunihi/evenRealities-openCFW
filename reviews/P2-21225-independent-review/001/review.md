# P2-21225 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481F6A..0x481FD6 (108 bytes); instruction and literal-reference outputs match. The code multiplies the exponent by 30103 with 32-bit wrapping before signed division by the literal divisor. It computes the seven-minus-estimate scale and branches to separate 48262C calls depending on its sign; the nonpositive path negates the scale modulo 2^32, passes the absolute original pair, then calls 4D4326. Both paths retain the recorded returned pair. The digit budget uses estimate+10 only for lowercase `f`, otherwise 6, then adds precision and clamps only the signed upper bound at 20. There is no lower clamp. SP132 receives byte 48 and R6 loads SP133 before the signed budget branch. Floating helper semantics and later rounding/digit emission remain unresolved.
