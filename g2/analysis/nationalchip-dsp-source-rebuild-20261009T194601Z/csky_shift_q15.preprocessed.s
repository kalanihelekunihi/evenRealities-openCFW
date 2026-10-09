 .file "csky_shift_q15.S"
    .section .text.csky_shift_q15,"ax",@progbits
    .align 2
    .global csky_shift_q15
    .type csky_shift_q15, @function
csky_shift_q15:
    lsri t0, a3, 2
    andi t1, a3, 3
    blz a1, .L2
.L1:
    bez t0, .L5
.L3:
    pldbi.d t4, (a0)
    plsl.s16.s t6, t4, a1
    plsl.s16.s t7, t5, a1
    stbi.w t6, (a2)
.L4:
    stbi.w t7, (a2)
    bloop t0, .L3, .L4
.L5:
    bez t1, .L0
.L6:
    ldbi.hs t4, (a0)
    plsl.s16.s t6, t4, a1
.L7:
    stbi.h t6, (a2)
    bloop t1, .L6, .L7
    br .L0
.L2:
    neg.s32.s a1, a1
    bez t0, .L10
.L8:
    pldbi.d t4, (a0)
    pasr.s16 t6, t4, a1
    pasr.s16 t7, t5, a1
    stbi.w t6, (a2)
.L9:
    stbi.w t7, (a2)
    bloop t0, .L8, .L9
.L10:
    bez t1, .L0
.L11:
    ldbi.hs t4, (a0)
    pasr.s16 t6, t4, a1
.L12:
    stbi.h t6, (a2)
    bloop t1, .L11, .L12
.L0:
    rts
    .size csky_shift_q15, .-csky_shift_q15
