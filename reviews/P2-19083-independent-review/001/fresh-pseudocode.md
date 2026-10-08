# Four-call wrapper and context predicate 0x46916C..0x4691BC

Partial/unaccepted; 80 instruction bytes, two complete functions.

0x46916C: PUSH R4/R5/R6/LR (16 bytes); R4=original R0, R5=original R1, R6=original R2. In order call 0x44122A, 0x441238, 0x44120E, 0x44121C. Before each call explicitly reload R2=R6, R1=R5, R0=R4. R3 remains live and may differ after every child. First three R0 results discarded by reload; final child R0 survives POP R4/R5/R6/PC. No conditions, child contracts, or assumed common fourth argument.

0x46919E: PUSH R7/LR (8 bytes); call 0x46B44C with live incoming arguments. FULL result zero returns R0=0 without memory read. Nonzero result reads unsigned byte at [result+21]. Byte zero produces R0=0, nonzero produces R0=1, followed by explicit UXTB R0. Shared POP R1/PC consumes 8 bytes and puts saved original R7 into R1. This is a bool predicate over one fresh child pointer and one byte, not an established context accessor contract. No C, freeze, or runtime proof.
