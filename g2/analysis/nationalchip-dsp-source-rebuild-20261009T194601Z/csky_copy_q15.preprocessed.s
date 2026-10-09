 .file "csky_copy_q15.S"
    .section .text.csky_copy_q15,"ax",@progbits
    .align 2
    .global csky_copy_q15
    .type csky_copy_q15, @function
csky_copy_q15:
    lsri a3, a2, 2
    bez a3, .L0
.L1:
    pldbi.d t0, (a0)
    stbi.w t0, (a1)
.L2:
    stbi.w t1, (a1)
    bloop a3, .L1, .L2
.L0:
    andi a3, a2, 3
    bez a3, .L3
.L4:
    ldbi.h t0, (a0)
.L5:
    stbi.h t0, (a1)
    bloop a3, .L4, .L5
.L3:
    rts
    .size csky_copy_q15, .-csky_copy_q15
