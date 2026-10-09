 .file "csky_fill_q15.S"
    .section .text.csky_fill_q15,"ax",@progbits
    .align 2
    .global csky_fill_q15
    .type csky_fill_q15, @function
csky_fill_q15:
    lsri a3, a2, 2
    bez a3, .L0
    dup.16 a0, a0, 0
.L1:
    stbi.w a0, (a1)
.L2:
    stbi.w a0, (a1)
    bloop a3, .L1, .L2
.L0:
    andi a3, a2, 3
    bez a3, .L3
.L4:
    stbi.h a0, (a1)
    bloop a3, .L4, .L4
.L3:
    rts
    .size csky_fill_q15, .-csky_fill_q15
