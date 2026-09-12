/* SPDX-License-Identifier: MIT */
/* Reviewed PMU rail-sequencing leaf for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x10000A30, package 0xA80, 350 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior of rail
 * operation B: one `pmu_fill_desc` call into a 24-byte stack
 * descriptor, entry-word gating, a selector poll, a rail/status bit
 * body with MMIO store sequences, and the shared pop-and-update loop
 * (no `rts`; the routine never returns).
 *
 * Assembly (rather than C) because every probed C shape for this body
 * compiles to at least 470 bytes against the 350-byte stock envelope
 * (plain -Os and -Oz both give 474; -fno-tree-loop-optimize hurts;
 * 22-variant probe, floor 470): the stock hand assembly uses 2-byte
 * branch/single-operand idioms and keeps a dozen values in high
 * registers across the fill call, which GCC -Os cannot reproduce
 * densely. The abandoned C draft is recorded in
 * docs/research/gx8002-uart-stage1-railb-source.md, not kept in tree.
 * No SDK text is reproduced and no SDK register map is used: every
 * address comes from the fill-provided descriptor and every constant
 * is a stock immediate.
 *
 * Behavior summary (see the audit doc for the full decode):
 * fill(id, desc); on fill failure, null entry words, or a selector
 * match the first pass ends in the loop with implementation-defined
 * registers (same branches, no outcome claim). Otherwise entry byte 0
 * extends desc[1] into a selector address; when arg1's low 16 bits
 * differ from the masked selector word the body runs: desc[3] bit
 * (entry byte 4) arms desc[5], an id-gated rotl tail may fold the
 * desc[2] cell, a clear/set sequence rewrites the selector word, and
 * a set desc[2] cell bit (entry byte 6) with a gated id latches
 * desc[4]. Every path ends in the pop-and-update loop at .Lloop.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-railb-source.md), not by byte
 * identity, though the transliteration keeps the stock register plan
 * so the comparison is instruction-for-instruction.
 */
.section .text.open_cfw_gx8002_uart_stage1_railb,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_railb
.type open_cfw_gx8002_uart_stage1_railb,@function
open_cfw_gx8002_uart_stage1_railb:
    /* Entry (stock 0xA30): frame + fill. r4/r5 survive the fill
     * (callee-saved); everything else is reloaded after it. */
    push r4-r5, r15
    subi r14, r14, 24
    mov r5, r1
    mov r1, r14
    mov r4, r0
    bsr open_cfw_gx8002_uart_stage1_pmu_fill_desc
    bnez r0, .Lloop
    /* Entry gating (stock 0xA42). */
    ld.w r12, (r14, 0x0)
    ld.w r3, (r12, 0x8)
    bez r3, .Lloop
    ld.b r2, (r3, 0x0)
    bez r2, .Lloop
    /* Selector poll (stock 0xA54). r19 keeps narrowed arg1 for the
     * later merge; a match skips to the loop. */
    ld.b r18, (r3, 0x1)
    ld.h r13, (r3, 0x2)
    ld.w r3, (r14, 0x4)
    addu r3, r2
    zexth r19, r5
    ld.w r3, (r3, 0x0)
    lsr r3, r3, r18
    and r3, r13
    cmpnei r3, 0
    inct r3, r3, 1
    cmpne r19, r3
    bf .Lloop
    /* Bit-length poll over the entry mask (stock 0xA78). */
    bez r13, .Lmask0
    mov r3, r0
.Lpoll:
    addi r3, 1
    lsr r1, r13, r3
    bnez r1, .Lpoll
.Lbody:
    /* Status bytes and cell address (stock 0xA88). */
    ld.bs r21, (r12, 0x4)
    addu r3, r18, r3
    addi r25, r3, 1
    ld.bs r22, (r12, 0x6)
    ld.w r23, (r14, 0x8)
    blz r21, .Lnoarm2
    /* desc[3]-bit arm of desc[5] (stock 0xAA0). */
    ld.w r1, (r14, 0xc)
    ld.w r20, (r1, 0x0)
    lsr r20, r20, r21
    andi r20, r20, 1
    bez r20, .Lnoarm
    ld.w r12, (r14, 0x14)
    movi r1, 1
    lsl r1, r1, r21
    st.w r1, (r12, 0x0)
.Lnoarm:
    /* desc[2]-cell status bit (stock 0xAC0). */
    ld.w r12, (r23, 0x0)
    lsr r12, r12, r22
    andi r12, r12, 1
    bez r12, .Lstores
    /* Id-gated rotl fold of the cell (stock 0xAD0). */
    cmpnei r4, 6
    bf .Lrotl
    movi r1, 9
    cmphs r1, r4
    bf .Lrotl
.Lstores:
    /* Selector clear/set sequence (stock 0xADA). */
    ld.w r1, (r14, 0x4)
    addu r2, r1
    movi r1, 1
    ld.w r24, (r2, 0x0)
    lsl r1, r1, r25
    andn r24, r24, r1
    st.w r24, (r2, 0x0)
    ld.w r24, (r2, 0x0)
    or r1, r1, r24
    st.w r1, (r2, 0x0)
    ld.w r24, (r2, 0x0)
    lsl r1, r13, r18
    andn r1, r24, r1
    zexth r5, r5
    st.w r1, (r2, 0x0)
    ld.w r1, (r2, 0x0)
    bez r5, .Lmerge0
    subi r0, r19, 1
    lsl r0, r0, r18
.Lmerge0:
    or r0, r1
    st.w r0, (r2, 0x0)
    movi r1, 1
    ld.w r0, (r2, 0x0)
    lsl r3, r1, r3
    andn r1, r0, r3
    st.w r1, (r2, 0x0)
    ld.w r1, (r2, 0x0)
    or r3, r1
    st.w r3, (r2, 0x0)
    /* Gate to the first check (stock 0xB30). */
    bez r12, .Lcheck
    cmpnei r4, 6
    bf .Lfold
    movi r3, 9
    cmphs r3, r4
    bf .Lfold
.Lcheck:
    bez r20, .Lloop
    /* First-pass latch of desc[4] (stock 0xB42). */
    ld.w r2, (r14, 0x10)
    movi r3, 1
    lsl r21, r3, r21
    st.w r21, (r2, 0x0)
.Lloop:
    /* Pop-and-update loop (stock 0xB4E): free the frame, restore the
     * saved registers, fold one status bit into the desc[2] cell,
     * re-check, latch, repeat. No exit. */
    addi r14, r14, 24
    pop r4-r5, r15
.Lfold:
    movi r3, 1
    ld.w r2, (r23, 0x0)
    lsl r22, r3, r22
    andn r3, r2, r22
    or r22, r22, r3
    st.w r22, (r23, 0x0)
    br .Lcheck
.Lrotl:
    /* Rotl fold tail (stock 0xB6A); rejoins the store sequence. */
    movi r24, 0
    subi r24, r24, 2
    ld.w r1, (r23, 0x0)
    rotl r24, r24, r22
    and r24, r24, r1
    st.w r24, (r23, 0x0)
    br .Lstores
.Lnoarm2:
    /* Negative entry byte 4: no arm possible (stock 0xB84). */
    movi r20, 0
    br .Lnoarm
.Lmask0:
    /* Zero entry mask: bit length is zero (stock 0xB8A). */
    mov r3, r13
    br .Lbody
    /* NOTE: the blz above targets .Lnoarm2; both out-of-line tails
     * sit here to keep the fallthrough hot path dense, exactly as
     * stock does. */
.size open_cfw_gx8002_uart_stage1_railb, .-open_cfw_gx8002_uart_stage1_railb
