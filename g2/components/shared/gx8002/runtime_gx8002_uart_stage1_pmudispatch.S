/* SPDX-License-Identifier: MIT */
/* Reviewed PMU rail-dispatch leaf for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x10000D98, package 0xDE8, 264 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * first PMU dispatcher: a jump-table fill-id map (ids 7,8->2;
 * 17,18->16; 20,21->19; 23,24->22; every other id, in range or out,
 * passes through unchanged), a first `pmu_fill_desc` call into a
 * 24-byte stack descriptor with descriptor-bit gating, a second
 * `pmu_fill_desc` call with the original id, a jump-table status-bit
 * map, a check arm, and pop-and-fall-through handoff into the retained
 * second dispatcher at 0x10000EA0 (a genuine external boundary, same
 * precedent as the reviewed reset entry's chain-load into retained
 * stage two). The routine never returns.
 *
 * Assembly (rather than C) because every probed C shape for this body
 * compiles to at least 298 bytes against the 264-byte stock envelope
 * (branch transliteration of nine bit arms plus five fill arms; the
 * stock hand assembly dispatches through two retained jump tables
 * with 2-byte bseti/ori arms, which GCC -Os cannot reproduce densely;
 * see docs/research/gx8002-uart-stage1-tickdiv-source.md section 7
 * and docs/research/gx8002-uart-stage1-pmudisp-source.md). No SDK
 * text is reproduced and no SDK register map is used: every address
 * the leaf touches arrives through the descriptor filled by the
 * reviewed `pmu_fill_desc` leaf or through the two retained table
 * base addresses below, and every other constant is a numeric
 * immediate observed in the decoded stock flow. The pinned upstream
 * SDK checkout is not a build input to this leaf.
 *
 * The two jump tables stay retained stock (compiler layout, not
 * derivable behavior): only their base addresses appear here,
 * materialized with movih/ori (the assembler places literal pools
 * only at the section end, so an `lrw` pool cannot sit inline as in
 * stock). Table contents are never reproduced. The one unreachable
 * stock padding halfword after the first indirect jump is omitted to
 * hold the envelope; both sides never fall through that jump.
 *
 * Behavior summary (see the audit doc for the full decode): fill the
 * mapped id; on fill failure skip to the second fill. Otherwise, when
 * the entry's signed byte 6 is not -1, test the descriptor-selected
 * bit: fills below 10 with (fill<<1)&579 nonzero take the extended
 * test, which checks the low bit of (b6+1)>>(cell&31) (the stock
 * three-operand shifts execute with reversed operand order, proven
 * by the stock traces themselves). A set result stores
 * (1u << entry[4]) to the fifth descriptor word when the selector is
 * nonzero; every other outcome stores it to the fourth word. Fill
 * the original id; on failure take
 * the tail walk. Otherwise compute (1u << entry[5]), fold in the
 * status bit selected by the second table (or the check arm, which
 * clears id bit 2 and fails on id 1 or a zero bit), store it to the
 * fifth word when the selector is nonzero (fourth word when zero),
 * pop the frame, and fall into the retained 0x10000EA0 dispatcher.
 * The zero-selector tail pops the frame and re-enters the bit arms
 * with caller registers, walking the caller stack 40 bytes per pass
 * until a nonzero selector word is observed; the battery maps a tall
 * caller window so every such pass is exactly compared.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-pmudisp-source.md), not by byte
 * identity, though the transliteration keeps the stock register plan
 * so the comparison is instruction-for-instruction.
 */
.section .text.open_cfw_gx8002_uart_stage1_pmu_dispatch,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_pmu_dispatch
.type open_cfw_gx8002_uart_stage1_pmu_dispatch,@function
open_cfw_gx8002_uart_stage1_pmu_dispatch:
    /* Entry (stock 0xD98): frame + first-table guard. r4 keeps the
     * entry id and r6 the entry selector across both fill calls
     * (callee-saved); r5 carries the mapped fill id. */
    push r4-r6, r15
    subi r14, r14, 24
    subi r3, r0, 7
    cmphsi r3, 18
    mov r4, r0
    mov r6, r1
    bt .Lpass
    /* First-table dispatch (stock 0xDA6). The table base is retained
     * stock layout: only the address is referenced here. Stock loads
     * it through an inline literal pool; the assembler places pools
     * only at the section end, so the reviewed form materializes the
     * same address with movih/ori in the same six bytes. */
    movih r2, 0x1000
    ori r2, r2, 0x1e60
    ldr.w r3, (r2, r3 << 2)
    jmp r3
    /* No trap padding: stock keeps one unreachable halfword after
     * this unconditional indirect jump; the reviewed form omits it
     * (both sides never fall through the jump, so the padding is
     * unobservable) to hold the 264-byte envelope. */
.Lfill2_arm:
    /* First-table arm for ids 7,8 (stock 0xDB4): fill id 2. */
    movi r5, 2
.Lfill1:
    mov r1, r14
    mov r0, r5
    bsr open_cfw_gx8002_uart_stage1_pmu_fill_desc
    bnez r0, .Lfill2
    /* Entry byte 6 gate (stock 0xDC2). Stock materializes -1 in r3
     * and compares; the reviewed form folds the test to (b6+1)==0,
     * which holds exactly when the sign-extended byte is -1, in two
     * fewer bytes. */
    ld.w r1, (r14, 0x0)
    ld.bs r2, (r1, 0x6)
    addi r3, r2, 1
    bez r3, .Lfill2
    /* Low-fill mask test (stock 0xDD0): fills below 10 whose
     * doubled value meets the 579 mask take the extended test. The
     * stock three-operand shift executes reversed (see the verifier
     * and audit doc), so this tests (fill<<1)&579, not (1<<fill). */
    cmphsi r5, 10
    bt .Lalt
    movi r3, 1
    lsl r5, r3, r5
    andi r5, r5, 579
    bez r5, .Lalt
    /* Extended bit test (stock 0xDE2): the reversed three-operand
     * shift computes (b6+1)>>(cell&31); a set low bit stores to the
     * fifth word. */
    ld.w r3, (r14, 0x8)
    addi r0, r2, 1
    ld.w r3, (r3, 0x0)
    lsr r0, r3, r0
    andi r0, r0, 1
    bez r0, .Lplain
.Lstore4:
    ld.bs r1, (r1, 0x4)
    ld.w r2, (r14, 0x10)
    movi r3, 1
    lsl r3, r1
    st.w r3, (r2, 0x0)
.Lfill2:
    mov r1, r14
    mov r0, r4
    bsr open_cfw_gx8002_uart_stage1_pmu_fill_desc
    bnez r0, .Ltailwalk
    /* Status bit from entry byte 5 (stock 0xE0C). */
    ld.w r3, (r14, 0x0)
    ld.bs r2, (r3, 0x5)
    movi r3, 1
    lsl r3, r2
    /* Second-table guard (stock 0xE16): out-of-range ids take the
     * check arm. */
    subi r2, r4, 6
    cmphsi r2, 19
    bt .Lcheck
    /* Second-table dispatch (stock 0xE1C): same movih/ori form for
     * the retained table base. */
    movih r1, 0x1000
    ori r1, r1, 0x1ea8
    ldr.w r2, (r1, r2 << 2)
    jmp r2
.Lfill22_arm:
    /* First-table arm for ids 23,24 (stock 0xE28). */
    movi r5, 22
    br .Lfill1
.Lfill19_arm:
    /* First-table arm for ids 20,21 (stock 0xE2C). */
    movi r5, 19
    br .Lfill1
.Lfill16_arm:
    /* First-table arm for ids 17,18 (stock 0xE30). */
    movi r5, 16
    br .Lfill1
.Lalt:
    /* Alternate bit test (stock 0xE34): bit b6 of the desc[2]
     * target. The extended-test miss joins the shift below with the
     * cell still loaded (no re-read). A clear bit, or a zero
     * selector, stores to the fourth word. */
    ld.w r3, (r14, 0x8)
    ld.w r3, (r3, 0x0)
.Lplain:
    lsr r3, r2
    andi r3, r3, 1
    bez r3, .Lstore4
    bez r6, .Lstore4
    ld.bs r1, (r1, 0x4)
    ld.w r2, (r14, 0x14)
    movi r3, 1
    lsl r3, r1
    st.w r3, (r2, 0x0)
    br .Lfill2
.Lpass:
    /* First-table passthrough (stock 0xE54). */
    mov r5, r4
    br .Lfill1
    /* Second-table bit arms (stock 0xE58..0xE8A). Each folds one
     * status bit into r3 and joins the store gate. */
.Lbit15_arm:
    ori r3, r3, 32768
.Lstore_gate:
    bnez r6, .Lstore5_live
    ld.w r2, (r14, 0x10)
    st.w r3, (r2, 0x0)
.Ltailwalk:
    /* Tail walk (stock 0xE64): pop the frame and re-enter the bit
     * arms with caller registers. Each pass consumes 40 bytes of
     * caller stack; the first re-entry takes the 1<<19 arm below,
     * later passes take whatever arm the popped r3 selects through
     * the store gate. */
    addi r14, r14, 24
    pop r4-r6, r15
.Lbit19_arm:
    bseti r3, 19
    br .Lstore_gate
.Lbit18_arm:
    bseti r3, 18
    br .Lstore_gate
.Lbit20_arm:
    bseti r3, 20
    br .Lstore_gate
.Lbit13_arm:
    ori r3, r3, 8192
    br .Lstore_gate
.Lbit17_arm:
    bseti r3, 17
    br .Lstore_gate
.Lbit16_arm:
    bseti r3, 16
    br .Lstore_gate
.Lbit3_arm:
    ori r3, r3, 8
    br .Lstore_gate
.Lbit21_arm:
    bseti r3, 21
    br .Lstore_gate
.Lcheck:
    /* Check arm (stock 0xE8C): clear id bit 2, fail on id 1 or a
     * zero status bit. */
    bclri r4, 2
    cmpnei r4, 1
    bf .Ltailwalk
    bez r3, .Ltailwalk
    br .Lstore_gate
.Lstore5_live:
    /* Live store (stock 0xE98): nonzero selector stores the status
     * word to the fifth descriptor word, pops the frame, and falls
     * into the retained second dispatcher. */
    ld.w r2, (r14, 0x14)
    st.w r3, (r2, 0x0)
    addi r14, r14, 24
    pop r4-r6, r15
    /* Fall through to retained 0x10000EA0 (no rts). */
