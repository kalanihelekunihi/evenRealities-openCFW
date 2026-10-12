/* Pinned ARC GNU assembler probe for native 222f 0140 at 0x3086b0. */
    .text
    .global probe_asl_two_operand
probe_asl_two_operand:
    asl r2,r5
    asl r2,r2,r5
    asl r2,r5,1
    j [blink]
