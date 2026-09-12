/* SPDX-License-Identifier: MIT */
/* Reviewed rail postamble leaf for the GX8002 UART boot stage 1 (IRAM)
 * image: runtime 0x10001D9C, package 0x1DEC, 60 bytes (56 bytes of code
 * plus the 4-byte literal pool word).
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * small postamble that runs after the rail-programming flow: set status
 * bits 0 and 8 of the control word at [base+0x3A0] (base read from the
 * pointer cell 0x20002274), poll bit 0 of the status word at
 * [base+0x2C0] until set, clear the two control bits again, publish id
 * 25 with selector 0 (stores of 0 to [base+0x398]), and call the first
 * PMU dispatcher (0x10000D98, the reviewed uart-stage1-pmudisp leaf)
 * with r0=25, r1=0. The dispatcher never returns: it hands off into
 * the retained second dispatcher at 0x10000EA0 (a genuine external
 * boundary, same precedent as the reviewed reset entry's chain-load
 * into retained stage two and the pmudispatch leaf's handoff). The
 * routine never returns.
 *
 * The leaf takes no register inputs: r0/r1 are set explicitly and r6
 * passes through untouched to the dispatcher (its entry selector).
 * The base pointer, the two control/status cells, and the dispatcher
 * inputs are the only RAM inputs.
 *
 * Assembly (rather than C) because the 60-byte stock envelope holds a
 * hand-written push/bsr/pop shape with an inline literal pool that GCC
 * -Os cannot reproduce densely (the same reason the pmudispatch leaf
 * is assembly; see docs/research/gx8002-uart-stage1-pmudisp-source.md).
 * No SDK text is reproduced and no SDK register map is used: the only
 * absolute address in the body is the numeric pointer-cell constant
 * 0x20002274 observed in the decoded stock flow, loaded with `lrw`
 * through the assembler's own end-of-section literal pool (the same
 * numeric-lrw precedent as the reviewed stage-1 reset entry, which
 * keeps code plus literal pool inside its envelope). The pinned
 * upstream SDK checkout is not a build input to this leaf.
 *
 * The assembled section is byte-identical to the stock envelope
 * (asserted by the verifier): every encoding, including the 32-bit
 * `bez` poll-loop branch and the pool word placement, matches. The
 * unreachable tail after the envelope (the pool word is inside; the
 * dead `rts` at 0x10001DD8 and padding stay retained stock) is never
 * executed on either side because the dispatcher does not return.
 *
 * Behavior summary (see the audit doc for the full decode): see above.
 * The single-pass poll shape is pinned by the battery; a clear poll
 * bit spins both sides on the same three instructions (byte-identical
 * code), so no separate multi-pass case is needed. The battery sweeps
 * entry r0/r1 garbage to prove they are not inputs.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-postamble-source.md), not by byte
 * identity alone, though the transliteration keeps the stock register
 * plan and encoding so the comparison is instruction-for-instruction.
 */
.section .text.open_cfw_gx8002_uart_stage1_postamble,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_postamble
.type open_cfw_gx8002_uart_stage1_postamble,@function
open_cfw_gx8002_uart_stage1_postamble:
    /* Entry (stock 0x1D9C): no frame, just the return-address push.
     * The dispatcher call below never returns, so no frame is needed. */
    push r15
    /* Publish bits (stock 0x1D9E): base pointer, set control bits. */
    lrw r3, 0x20002274
    ld.w r2, (r3, 0x0)
    ld.w r3, (r2, 0x3a0)
    ori r3, r3, 257
    st.w r3, (r2, 0x3a0)
    /* Poll (stock 0x1DAE): spin on status bit 0. */
.Lpoll:
    ld.w r3, (r2, 0x2c0)
    andi r3, r3, 1
    bez r3, .Lpoll
    /* Release and publish (stock 0x1DBA): clear the control bits,
     * publish id 25 with selector 0. */
    ld.w r3, (r2, 0x3a0)
    bclri r3, 0
    bclri r3, 8
    movi r1, 0
    st.w r3, (r2, 0x3a0)
    movi r0, 25
    st.w r1, (r2, 0x398)
    /* Dispatch (stock 0x1DCE): noreturn call into the reviewed first
     * PMU dispatcher; on the stock side the stock dispatcher body
     * runs instead. Both hand off into retained 0x10000EA0. */
    bsr open_cfw_gx8002_uart_stage1_pmu_dispatch
    pop r15
    /* The assembler emits its literal pool (0x20002274) here, matching
     * the stock pool word at 0x10001DD4. No explicit .word: a label
     * pool would take the address-load indirection form. */
.size open_cfw_gx8002_uart_stage1_postamble, .-open_cfw_gx8002_uart_stage1_postamble
