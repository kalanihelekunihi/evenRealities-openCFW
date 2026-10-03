# Independent review 6421

Disposition: **PASS_SCOPED**; `accepted:false`.

Packet hashes and EA68..EAF6 source bytes match. GNU Thumb decoding confirms the 16-byte frame and an initial descriptor+4 word load before the null check on the descriptor pointer. Thus the packet correctly preserves that read/fault ordering rather than suggesting the null guard protects it. The subsequent first descriptor word is masked with 0x01FFFFFF and compared with the pinned literal; null or mismatch returns status 2. After a match, the descriptor is used without an additional bounds check, and its freshly read byte 0 must equal 2 or the routine returns 6.

The child call is 4222F0(4, 15). A nonzero child result is returned directly through the epilogue without publishing the register word. On zero, the routine freshly reloads descriptor bytes after the child and assembles the fields in R5: byte0 low 3 bits into bits 24..26, byte1 bit0 into bit20, byte2 bit0 into bit19, byte3 low3 into bits16..18, constant bit12, byte4 bit0 into bit4, byte5 bit0 into bit3, and byte6 bit0 into bit2. It clears bit0 with LSR/LSL, stores the full word to the literal-backed address, and returns zero. The POP restores R1 from the saved incoming R3.

This is static control-flow and register-field evidence only. No descriptor-purpose, fault-runtime, child-semantics, or admission claim is made; canonical files and gates are unchanged.
