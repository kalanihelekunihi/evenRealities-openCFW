 .file "csky_abs_max_q15.S"
    .section .text.csky_abs_max_q15,"ax",@progbits
    .align 2
    .global csky_abs_max_q15
    .type csky_abs_max_q15, @function
csky_abs_max_q15:
    lsri a3, a2, 2
    andi a2, a2, 3
    movi t5, 0
    bez a3, .L2
.L4:
    pldbi.d t2, (a0)
    pabs.s16.s t2, t2
    pmax.u16 t5, t5, t2
    pabs.s16.s t3, t3
.L5:
    pmax.u16 t5, t5, t3
    bloop a3, .L4, .L5
.L2:
    bez a2, .L0
.L3:
    ldbi.h t2, (a0)
    pabs.s16.s t2, t2
.L1:
    pmax.u16 t5, t5, t2
    bloop a2, .L3, .L1
.L0:
    dup.16 t2, t5, 0
    dup.16 t3, t5, 1
    pmax.u16 t5, t2, t3
    stbi.h t5, (a1)
    rts
    .size csky_abs_max_q15, .-csky_abs_max_q15
