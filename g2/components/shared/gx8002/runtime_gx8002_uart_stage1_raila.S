/* SPDX-License-Identifier: MIT */
/* Reviewed PMU rail-sequencing leaf for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x10000860, package 0x8B0, 464 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior of rail
 * operation A: entry id/arg1 gating, one `pmu_fill_desc` call into a
 * 24-byte stack descriptor (retried with mutated arg1 on the
 * divisor arms), entry-byte gating, an m-cell bit test, an id
 * bit-table gate, a descriptor-table combined test, id-gated
 * merge/store arms, a divisor retry dispatcher, a bit-mask retry
 * check, and the shared fail tail that cycles the shift and
 * re-enters the body (no `rts`; the routine never returns).
 *
 * Assembly (rather than C) because the body keeps its whole working
 * set in high registers across the fill call and re-uses the same
 * frame pointer for the retry/fail drift machine: a C shape would
 * spill private stack traffic that the decoded-trace battery would
 * have to exclude from comparison, weakening the claim. A private
 * half-body C probe (entry gate, fill, first gates, id table, desc
 * poll; stock 0x860..0x8F2 = 194 bytes) compiles to 108 bytes, so
 * size alone would likely fit; the choice is about keeping every
 * push/pop/drift access in the compared trace, not about the
 * envelope. The probe is recorded in
 * docs/research/gx8002-uart-stage1-raila-source.md, not kept in tree.
 * No SDK text is reproduced and no SDK register map is used: every
 * address comes from the fill-provided descriptor and every constant
 * is a stock immediate (0x20002018 is the stock literal-pool word).
 *
 * Behavior summary (see the audit doc for the full decode):
 * id > 25 fails at once. arg1 == 2 goes to the bit-mask check;
 * arg1 >= 3 goes to the divisor dispatcher (id 7 shifts, id 8
 * divides, else fail); arg1 in {0,1} calls the fill. Fill failure,
 * or entry byte 6 equal to 0xFF, fails with implementation-defined
 * registers (same branches, no outcome claim). Otherwise the m-cell
 * bit (entry byte 6) must differ from arg1; ids below 23 must be in
 * {16,19,22} and pass the descriptor-table combined test, ids 23+
 * poll the desc[3] word instead. The id {7,8} and arg1 == 1 arms
 * select store sequences; every other path folds and latches. All
 * terminal paths pop the frame and either retry the fill (divisor
 * and bit-mask arms) or cycle the fail tail, which re-enters the
 * body with a cycled shift. No path returns.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-raila-source.md), not by byte
 * identity, though the transliteration keeps the stock register plan
 * so the comparison is instruction-for-instruction.
 */
.section .text.open_cfw_gx8002_uart_stage1_raila,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_raila
.type open_cfw_gx8002_uart_stage1_raila,@function
open_cfw_gx8002_uart_stage1_raila:
    /* Entry gate (stock 0x860): id in r0, arg1 in r1. */
    push r4-r5, r15
    subi r14, r14, 24
    movi r3, 25
    cmphs r3, r0
    mov r5, r0
    mov r4, r1
    bf .Lfail
    cmpnei r1, 2
    bf .Lcheck
    cmplti r1, 3
    bf .Ldisp
.Lfill:
    /* Fill call (stock 0x876). r5 is the id, kept in the
     * callee-saved register across retries; r1 repoints at the
     * current (possibly drifted) frame. */
    mov r1, r14
    mov r0, r5
    bsr open_cfw_gx8002_uart_stage1_pmu_fill_desc
    bnez r0, .Lfail
    /* Entry gate (stock 0x882): byte 6 must not be 0xFF. */
    ld.w r13, (r14, 0x0)
    movi r3, 0
    ld.bs r1, (r13, 0x6)
    subi r3, 1
    cmpne r1, r3
    bf .Lfail
    cmpnei r4, 2
    ld.w r12, (r14, 0x8)
    bf .Lfailre
.Lbitest:
    /* M-cell bit test (stock 0x89a): the cell bit selected by
     * entry byte 6 must differ from arg1. */
    ld.w r2, (r12, 0x0)
    lsr r2, r1
    andi r2, r2, 1
    cmpne r2, r4
    bf .Lpopdisp
    /* Id bit-table gate (stock 0x8a8): ids below 23 continue only
     * for ids 16, 19, 22 (bits of 0x490000); ids 23+ poll. */
    cmphsi r5, 23
    bt .Lpoll2
    movih r3, 73
    lsr r3, r5
    zext r3, r3, 0, 0
    bez r3, .Lpoll2
    /* Descriptor-table combined test (stock 0x8ba): shift bytes
     * from the 0x20002018 table fold the desc[3] word. */
    ld.w r3, (r14, 0xc)
    lrw r19, 0x20002018
    ld.w r18, (r3, 0x0)
    addi r3, r5, 1
    lsli r3, r3, 4
    addu r3, r19, r3
    ld.bs r2, (r3, 0x5)
    addi r3, r5, 2
    lsli r3, r3, 4
    addu r19, r19, r3
    lsr r2, r18, r2
    ld.bs r3, (r19, 0x5)
    lsr r18, r18, r3
    and r2, r2, r18
    nor r2, r2
    andi r2, r2, 1
    bez r2, .Lfoldrot
.Lidgate:
    /* Id {7,8} gate (stock 0x8f2). */
    subi r3, r5, 7
    cmphsi r3, 2
    ld.bs r2, (r13, 0x4)
    bf .Lstore78
    cmpnei r4, 1
    bf .Lstorearg
    /* Merge arm (stock 0x900). */
    movi r3, 1
    ld.w r18, (r12, 0x0)
    lsl r13, r3, r1
    andn r13, r18, r13
    lsl r1, r4, r1
    or r1, r13
    st.w r1, (r12, 0x0)
    ld.w r1, (r14, 0x10)
    lsl r3, r3, r2
    st.w r3, (r1, 0x0)
.Lpopdisp:
    /* Pop-and-dispatch (stock 0x91e): free the frame, restore the
     * saved registers, then run the dispatcher. r0/r1 are body
     * leftovers, not popped state. The entry arg1>=3 arm reaches
     * the dispatcher directly with the frame still live. */
    addi r14, r14, 24
    pop r4-r5, r15
.Ldisp:
    cmpnei r0, 7
    bf .Lasr
    cmpnei r0, 8
    bt .Lfail
    movi r3, 6
    divs r4, r1, r3
    br .Lfill
.Lpoll2:
    /* desc[3]-word poll (stock 0x932). */
    ld.w r3, (r14, 0xc)
    ld.w r2, (r3, 0x0)
    ld.bs r3, (r13, 0x5)
    lsr r2, r3
    nor r2, r2
    andi r2, r2, 1
    bnez r2, .Lidgate
.Lfoldrot:
    /* Rotl fold arm (stock 0x946). */
    movi r3, 0
    subi r3, 2
    ld.w r2, (r12, 0x0)
    rotl r3, r1
    and r3, r2
    lsl r1, r4, r1
    or r3, r1
    st.w r3, (r12, 0x0)
    addi r14, r14, 24
    pop r4-r5, r15
.Lcheck:
    /* Bit-mask retry check (stock 0x960): ids {0,1,2,6,9} under
     * 10 retry the fill. */
    cmphsi r0, 10
    bt .Lfail
    movi r3, 1
    lsl r3, r0
    andi r3, r3, 583
    bnez r3, .Lfill
.Lfail:
    /* Fail tail (stock 0x970): report -1, free the frame. */
    movi r0, 0
    subi r0, 1
    addi r14, r14, 24
    pop r4-r5, r15
.Lfailre:
    /* Fail re-entry (stock 0x978): cycle the shift, force arg1
     * to 1, re-enter the body test. */
    addi r1, 1
    sextb r1, r1
    movi r4, 1
    br .Lbitest
.Lstore78:
    /* Id {7,8} store arm (stock 0x980) with the 0x20002018
     * table poll sequence. */
    movi r3, 1
    ld.w r18, (r12, 0x0)
    lsl r13, r3, r1
    andn r13, r18, r13
    lsl r1, r4, r1
    or r4, r1, r13
    st.w r4, (r12, 0x0)
    ld.w r1, (r14, 0x10)
    lsl r3, r3, r2
    st.w r3, (r1, 0x0)
    ld.w r2, (r14, 0xc)
    lrw r1, 0x20002018
    ld.w r18, (r2, 0x0)
    ld.w r12, (r12, 0x0)
    ld.bs r2, (r1, 0x26)
    lsr r2, r12, r2
    andi r2, r2, 1
    bez r2, .Lpopdisp
    ld.bs r2, (r1, 0x25)
    lsr r2, r18, r2
    andi r2, r2, 1
    bez r2, .Lpopdisp
    ld.bs r13, (r1, 0x86)
    ld.bs r2, (r1, 0x85)
    lsr r13, r12, r13
    lsr r2, r18, r2
    or r13, r2
    andi r13, r13, 1
    bez r13, .Lstored5
    ld.bs r2, (r1, 0x76)
    ld.bs r1, (r1, 0x75)
    lsr r2, r12, r2
    lsr r18, r18, r1
    or r2, r2, r18
    andi r2, r2, 1
    bnez r2, .Lpopdisp
.Lstored5:
    /* Latch desc[5] (stock 0xA02). */
    ld.w r2, (r14, 0x14)
    st.w r3, (r2, 0x0)
    br .Lpopdisp
.Lasr:
    /* Shift retry arm (stock 0xA08). */
    asri r4, r1, 2
    br .Lfill
.Lstorearg:
    /* arg1 == 1 store arm (stock 0xA0C). */
    ld.w r13, (r14, 0x14)
    lsl r3, r4, r2
    st.w r3, (r13, 0x0)
    ld.w r3, (r12, 0x0)
    lsl r1, r4, r1
    andn r4, r3, r1
    or r1, r4
    st.w r1, (r12, 0x0)
    br .Lpopdisp
.size open_cfw_gx8002_uart_stage1_raila, .-open_cfw_gx8002_uart_stage1_raila
