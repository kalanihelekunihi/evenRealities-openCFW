 .file "csky_rfft_q15.S"
    .section .text.csky_split_rfft_q15,"ax",@progbits
    .align 2
    .global csky_split_rfft_q15
    .type csky_split_rfft_q15, @function
csky_split_rfft_q15:
    push l0, l1, l2, l3
    ld.w t9, (sp, 0x10)
    lsli t9, t9, 2
    addu a2, a2, t9
    bgeni l3, 15
    addi t0, a0, 4
    lsli t1, a1, 2
    subi t1, t1, 4
    addu t1, t1, a0
    addi t2, a3, 4
    subi t7, a1, 1
    bez t7, .L0
.L1:
    ldbi.w t4, (t0)
    ldbir.w t5, (a2), t9
    ld.w t6, (t1, 0x0)
    psub.16 l2, l3, t5
    pabs.s16.s t8, l2
    pkg l2, t8, 0, l2, 16
    mulcs.s16 l0, t4, t5
    mulcsx.s16 l1, t6, l2
    mulaca.s16.s l0, t6, l2
    mulacax.s16.s l1, t4, t5
    subi t1, t1, 4
    pkghh l0, l0, l1
.L2:
    stbi.w l0, (t2)
    bloop t7, .L1, .L2
.L0:
    ld.hs t0, (a0, 0x0)
    ld.hs t1, (a0, 0x2)
    movi t2, 0
    subh.s32 t3, t0, t1
    lsli t4, a1, 2
    addu t4, t4, a3
    st.h t3, (t4, 0x0)
    st.h t2, (t4, 0x2)
    addh.s32 t3, t0, t1
    st.h t3, (a3, 0x0)
    st.h t2, (a3, 0x2)
    pop l0, l1, l2, l3
    .size csky_split_rfft_q15, .-csky_split_rfft_q15
    .section .text.csky_split_rifft_q15,"ax",@progbits
    .align 2
    .global csky_split_rifft_q15
    .type csky_split_rifft_q15, @function
csky_split_rifft_q15:
    push l0
    ld.w t9, (sp, 0x4)
    lsli t9, t9, 2
    lsli t0, a1, 2
    addu t0, t0, a0
    bgeni l0, 15
    bez a1, .L10
.L11:
    ldbi.w t1, (a0)
    ld.w t2, (t0)
    ldbir.w t4, (a2), t9
    psub.16 t8, l0, t4
    pabs.s16.s t3, t8
    pkg t3, t3, 0, t8, 16
    mulcs.s16 t6, t2, t3
    mulcax.s16.s t7, t2, t3
    mulaca.s16.s t6, t1, t4
    pneg.s16.s t7, t7
    mulacsx.s16.s t7, t4, t1
    subi t0, t0, 4
    pkghh t6, t6, t7
.L12:
    stbi.w t6, (a3)
    bloop a1, .L11, .L12
.L10:
    pop l0
    .size csky_split_rifft_q15, .-csky_split_rifft_q15
