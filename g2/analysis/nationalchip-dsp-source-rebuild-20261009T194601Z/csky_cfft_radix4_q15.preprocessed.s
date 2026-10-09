 .file "csky_cfft_radix4_q15.S"
    .section .text.csky_radix4_butterfly_q15,"ax",@progbits
    .align 2
    .global csky_radix4_butterfly_q15
    .type csky_radix4_butterfly_q15, @function
csky_radix4_butterfly_q15:
    push l0, l1, l2, l3, l4, l5, l6, l7, l8, l9
    subi sp, sp, 0x8
    lsri t9, a1, 2
    mov t8, t9
    mov t0, a0
    addu t1, t0, a1
    addu t2, t1, a1
    addu t3, t2, a1
    movi l8, 0
.L0:
    ld.w l0, (t0, 0x0)
    ld.w l1, (t1, 0x0)
    ld.w l2, (t2, 0x0)
    ld.w l3, (t3, 0x0)
    pasri.s16 l0, l0, 2
    pasri.s16 l1, l1, 2
    pasri.s16 l2, l2, 2
    pasri.s16 l3, l3, 2
    padd.s16.s l4, l0, l2
    psub.s16.s l2, l0, l2
    padd.s16.s l7, l1, l3
    paddh.s16 l5, l4, l7
    lsli l9, l8, 3
    addu l9, a2, l9
    stbi.w l5, (t0)
    ld.w l6, (l9, 0x0)
    psub.s16.s l5, l4, l7
    mulca.s16.s t4, l6, l5
    mulcsx.s16 t5, l6, l5
    psub.s16.s l7, l1, l3
    pkghh t4, t4, t5
    pasx.s16.s l5, l2, l7
    psax.s16.s l2, l2, l7
    lsli l9, l8, 2
    addu l9, a2, l9
    stbi.w t4, (t1)
    ld.w l6, (l9, 0x0)
    mulca.s16.s t4, l6, l2
    mulcsx.s16 t5, l6, l2
    movi l9, 12
    mult l9, l8, l9
    addu l9, a2, l9
    pkghh t4, t4, t5
    stbi.w t4, (t2)
    ld.w l6, (l9, 0x0)
    mulca.s16.s t4, l6, l5
    mulcsx.s16 t5, l6, l5
    addu l8, l8, a3
    pkghh t4, t4, t5
.L1:
    stbi.w t4, (t3)
    bloop t8, .L0, .L1
    lsli a3, a3, 2
    st.w a0, (sp, 0x0)
    asri t8, a1, 2
.L11:
    cmphsi t8, 5
    bf .L10
    mov t7, t9
    asri t9, t9, 2
    movi l8, 0
    st.w l8, (sp, 0x4)
    movi t6, 0
.L3:
    cmplt t6, t9
    bf .L2
    ld.w l8, (sp, 0x4)
    movi l9, 4
    mult l3, l9, l8
    addu l9, l3, a2
    ld.w l0, (l9, 0x0)
    addu l9, l9, l3
    ld.w l1, (l9, 0x0)
    addu l9, l9, l3
    ld.w l2, (l9, 0x0)
    addu l8, l8, a3
    st.w l8, (sp, 0x4)
    ld.w a0, (sp, 0x0)
    lsli t1, t6, 2
    addu t3, t1, a0
    lsli t2, t9, 2
    addu t4, t3, t2
    addu t5, t4, t2
    addu t2, t5, t2
    mov t0, t6
.L5:
    cmplt t0, a1
    bf .L4
    ld.w l3, (t3, 0x0)
    ld.w l4, (t5, 0x0)
    padd.s16.s l5, l3, l4
    psub.s16.s l6, l3, l4
    ld.w a0, (t4, 0x0)
    ld.w l7, (t2, 0x0)
    padd.s16.s l3, a0, l7
    paddh.s16 t1, l5, l3
    pasri.s16 t1, t1, 1
    st.w t1, (t3, 0x0)
    lsli l9, t7, 2
    addu t3, t3, l9
    psubh.s16 l5, l5, l3
    mulca.s16.s t1, l1, l5
    mulcsx.s16 l8, l1, l5
    pkghh t1, t1, l8
    st.w t1, (t4, 0x0)
    addu t4, t4, l9
    psub.s16.s l3, a0, l7
    pasxh.s16 l5, l6, l3
    psaxh.s16 l6, l6, l3
    mulca.s16.s t1, l0, l6
    mulcsx.s16 l8, l0, l6
    pkghh t1, t1, l8
    st.w t1, (t5, 0x0)
    addu t5, t5, l9
    mulca.s16.s t1, l2, l5
    mulcsx.s16 l8, l2, l5
    pkghh t1, t1, l8
    st.w t1, (t2, 0x0)
    addu t2, t2, l9
    addu t0, t0, t7
    br .L5
.L4:
    addi t6, t6, 1
    br .L3
.L2:
    lsli a3, a3, 2
    asri t8, t8, 2
    br .L11
.L10:
    ld.w a0, (sp, 0x0)
    lsri a1, a1, 2
    mov a2, a0
.L12:
    pldbi.d l0, (a0)
    pldbi.d l2, (a0)
    padd.s16.s l4, l0, l2
    padd.s16.s l5, l1, l3
    paddh.s16 t0, l4, l5
    psubh.s16 t1, l4, l5
    stbi.w t0, (a2)
    stbi.w t1, (a2)
    psub.s16.s l4, l0, l2
    psub.s16.s l5, l1, l3
    psaxh.s16 t0, l4, l5
    pasxh.s16 t1, l4, l5
    stbi.w t0, (a2)
.L13:
    stbi.w t1, (a2)
    bloop a1, .L12, .L13
    addi sp, sp, 0x8
    pop l0, l1, l2, l3, l4, l5, l6, l7, l8, l9
    .size csky_radix4_butterfly_q15, .-csky_radix4_butterfly_q15
    .section .text.csky_radix4_butterfly_inverse_q15,"ax",@progbits
    .align 2
    .global csky_radix4_butterfly_inverse_q15
    .type csky_radix4_butterfly_inverse_q15, @function
csky_radix4_butterfly_inverse_q15:
    push l0, l1, l2, l3, l4, l5, l6, l7, l8, l9
    subi sp, sp, 0x8
    lsri t9, a1, 2
    mov t8, t9
    mov t0, a0
    addu t1, t0, a1
    addu t2, t1, a1
    addu t3, t2, a1
    movi l8, 0
.L20:
    ld.w l0, (t0, 0x0)
    ld.w l1, (t1, 0x0)
    ld.w l2, (t2, 0x0)
    ld.w l3, (t3, 0x0)
    pasri.s16 l0, l0, 2
    pasri.s16 l1, l1, 2
    pasri.s16 l2, l2, 2
    pasri.s16 l3, l3, 2
    padd.s16.s l4, l0, l2
    psub.s16.s l2, l0, l2
    padd.s16.s l7, l1, l3
    paddh.s16 l5, l4, l7
    stbi.w l5, (t0)
    psub.s16.s l5, l4, l7
    lsli l9, l8, 3
    addu l9, a2, l9
    ld.w l6, (l9, 0x0)
    mulcs.s16 t4, l6, l5
    mulcax.s16.s t5, l6, l5
    pkghh t4, t4, t5
    stbi.w t4, (t1)
    psub.s16.s l7, l1, l3
    psax.s16.s l5, l2, l7
    pasx.s16.s l2, l2, l7
    lsli l9, l8, 2
    addu l9, a2, l9
    ld.w l6, (l9, 0x0)
    mulcs.s16 t4, l6, l2
    mulcax.s16.s t5, l6, l2
    pkghh t4, t4, t5
    stbi.w t4, (t2)
    movi l9, 12
    mult l9, l8, l9
    addu l9, a2, l9
    ld.w l6, (l9, 0x0)
    mulcs.s16 t4, l6, l5
    mulcax.s16.s t5, l6, l5
    pkghh t4, t4, t5
    stbi.w t4, (t3)
.L21:
    addu l8, l8, a3
    bloop t8, .L20, .L21
    lsli a3, a3, 2
    st.w a0, (sp, 0x0)
    asri t8, a1, 2
.L211:
    cmphsi t8, 5
    bf .L210
    mov t7, t9
    asri t9, t9, 2
    movi l8, 0
    st.w l8, (sp, 0x4)
    movi t6, 0
.L23:
    cmplt t6, t9
    bf .L22
    ld.w l8, (sp, 0x4)
    movi l9, 4
    mult l3, l9, l8
    addu l9, l3, a2
    ld.w l0, (l9, 0x0)
    addu l9, l9, l3
    ld.w l1, (l9, 0x0)
    addu l9, l9, l3
    ld.w l2, (l9, 0x0)
    addu l8, l8, a3
    st.w l8, (sp, 0x4)
    ld.w a0, (sp, 0x0)
    lsli t1, t6, 2
    addu t3, t1, a0
    lsli t2, t9, 2
    addu t4, t3, t2
    addu t5, t4, t2
    addu t2, t5, t2
    mov t0, t6
.L25:
    cmplt t0, a1
    bf .L24
    ld.w l3, (t3, 0x0)
    ld.w l4, (t5, 0x0)
    padd.s16.s l5, l3, l4
    psub.s16.s l6, l3, l4
    ld.w a0, (t4, 0x0)
    ld.w l7, (t2, 0x0)
    padd.s16.s l3, a0, l7
    paddh.s16 t1, l5, l3
    pasri.s16 t1, t1, 1
    st.w t1, (t3, 0x0)
    lsli l9, t7, 2
    addu t3, t3, l9
    psubh.s16 l5, l5, l3
    mulcs.s16 t1, l1, l5
    mulcax.s16.s l8, l1, l5
    pkghh t1, t1, l8
    st.w t1, (t4, 0x0)
    addu t4, t4, l9
    psub.s16.s l3, a0, l7
    psaxh.s16 l5, l6, l3
    pasxh.s16 l6, l6, l3
    mulcs.s16 t1, l0, l6
    mulcax.s16.s l8, l0, l6
    pkghh t1, t1, l8
    st.w t1, (t5, 0x0)
    addu t5, t5, l9
    mulcs.s16 t1, l2, l5
    mulcax.s16.s l8, l2, l5
    pkghh t1, t1, l8
    st.w t1, (t2, 0x0)
    addu t2, t2, l9
    addu t0, t0, t7
    br .L25
.L24:
    addi t6, t6, 1
    br .L23
.L22:
    lsli a3, a3, 2
    asri t8, t8, 2
    br .L211
.L210:
    ld.w a0, (sp, 0x0)
    lsri a1, a1, 2
    mov a2, a0
.L212:
    pldbi.d l0, (a0)
    pldbi.d l2, (a0)
    padd.s16.s l4, l0, l2
    padd.s16.s l5, l1, l3
    paddh.s16 t0, l4, l5
    psubh.s16 t1, l4, l5
    stbi.w t0, (a2)
    stbi.w t1, (a2)
    psub.s16.s l4, l0, l2
    psub.s16.s l5, l1, l3
    pasxh.s16 t0, l4, l5
    psaxh.s16 t1, l4, l5
    stbi.w t0, (a2)
.L213:
    stbi.w t1, (a2)
    bloop a1, .L212, .L213
    addi sp, sp, 0x8
    pop l0, l1, l2, l3, l4, l5, l6, l7, l8, l9
    .size csky_radix4_butterfly_inverse_q15, .-csky_radix4_butterfly_inverse_q15
