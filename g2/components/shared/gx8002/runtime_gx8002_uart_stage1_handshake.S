/* SPDX-License-Identifier: MIT */
/* Reviewed UART handshake leaf for the GX8002 UART boot stage 1 (IRAM)
 * image: runtime 0x100006D8 (package 0x728, 168 bytes).
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * H-class flow that sits between the UART announce leaf (0x1000065C,
 * announce tranche) and the PMU fill-desc leaf (0x10000780, pmufill
 * tranche). The leaf first runs the rail-configure tail (0x1000046C,
 * traptails tranche) and two PMU bit reads (0x100003A4/0x100003B0,
 * pmubits tranche); a set bit selects the UART bring-up call
 * (0x100005C4, beacon tranche) with (r0, r1) = (1, 0), otherwise
 * with (0, [0x20002010]). It then transmits "GET" (71, 69, 84)
 * through TX-empty-polled stores and waits for an RX byte matching
 * the expected sequence: 'O' (79) first, then the bytes of the
 * retained table at 0x10001E5C ("OK", pool 0x4B4F). A mismatch
 * advances the sequence and retries the transmit; a full match, or
 * a zero expected byte before any match, pops the frame into the
 * trapping bkpt word. A set RX-ready flag with a zero retry budget
 * instead calls the millisecond-delay leaf (0x100003FC, mdelay
 * tranche) and retries.
 *
 * The rail-configure tail is H-class (its first dispatcher call
 * already leaves its envelope and the dispatcher cascade never
 * returns, per the traptails/pmudisp/pmusecond audits), so the
 * first chaining call already leaves this envelope: the PMU bit
 * reads, the bring-up calls, the "GET"/"OK" exchange, the delay
 * call, and the pop-trap tail never execute on working hardware
 * and are admitted by byte identity.
 *
 * Assembly (rather than C) because the envelope is dense
 * hand-scheduled 16-bit traffic with a literal pool and a trapping
 * bkpt word, and the transliteration below assembles byte-identical
 * to stock (168 bytes, exact fill, no relocations), so there is
 * nothing for C to approximate. No SDK text is reproduced and no
 * SDK register map is used: the 0x20002010/0x20002014 cells, the
 * 0x10001E5C table address, and every offset and constant below is
 * a numeric immediate observed in the decoded stock flow. The
 * pinned upstream SDK checkout is not a build input to this leaf.
 *
 * The cross-envelope calls target linker-assigned absolute symbols
 * (uartcfg/traptails-leaf precedent), so the linked section carries
 * no relocations; the rail-configure/dispatcher cascade past the
 * chaining branch is qualified by the reviewed traptails (288
 * cases), pmudispatch (8,370 cases), and pmusecond (2,688 cases)
 * batteries and is never stepped into here.
 *
 * Behavior summary (see the audit doc for the full decode):
 * 0x6D8: push r4-r9, r15; (r0, r1) unchanged into 0x46C;
 * post-chain (unreachable): (r0) into 0x3A4, 1-gated; (r0) into
 * 0x3B0, 1-gated; (0/1, 0/[0x20002010]) into 0x5C4; TX "GET" via
 * [base+20] bit-6 polls; RX match against 'O' then [0x10001E5C+r8];
 * r0 = 1 into 0x3FC on empty-budget retries; pop r4-r9, r15; bkpt.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-handshake-source.md): exact
 * prefix access-trace, final-RAM, and at-chain-register agreement
 * from entry to the chaining call on both sides, plus byte identity
 * of the full envelope.
 */
.section .text.open_cfw_gx8002_uart_stage1_handshake,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_handshake
.type open_cfw_gx8002_uart_stage1_handshake,@function
open_cfw_gx8002_uart_stage1_handshake:
    /* UART handshake (stock 0x6D8..0x773) plus literal pool. */
    push r4-r9, r15
    bsr open_cfw_gx8002_uart_boot_stage1_46c_entry
    bsr open_cfw_gx8002_uart_boot_stage1_3a4_entry
    cmpnei r0, 1
    bf .Lhandshake_alt
    bsr open_cfw_gx8002_uart_boot_stage1_3b0_entry
    cmpnei r0, 1
    bf .Lhandshake_alt
    movi r1, 0
    movi r0, 1
    bsr open_cfw_gx8002_uart_boot_stage1_5c4_entry
    br .Lhandshake_get
.Lhandshake_alt:
    lrw r3, 0x20002010
    movi r0, 0
    ld.w r1, (r3, 0x0)
    bsr open_cfw_gx8002_uart_boot_stage1_5c4_entry
.Lhandshake_get:
    movi r7, 79
    movi r8, 0
    lrw r6, 0x20002014
    movi r5, 71
    movi r4, 69
    lrw r9, 0x10001e5c
.Lhandshake_tx0:
    ld.w r1, (r6, 0x0)
    addi r2, r1, 20
.Lhandshake_poll0:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 64
    bez r3, .Lhandshake_poll0
    st.w r5, (r1, 0x0)
.Lhandshake_tx1:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 64
    bez r3, .Lhandshake_tx1
    st.w r4, (r1, 0x0)
.Lhandshake_tx2:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 64
    bez r3, .Lhandshake_tx2
    movi r3, 84
    st.w r3, (r1, 0x0)
.Lhandshake_rx:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 1
    bnez r3, .Lhandshake_got
    bez r7, .Lhandshake_trap
    movi r0, 1
    bsr open_cfw_gx8002_uart_boot_stage1_3fc_entry
    br .Lhandshake_tx0
.Lhandshake_got:
    ld.w r3, (r1, 0x0)
    zextb r3, r3
    cmpne r3, r7
    bf .Lhandshake_next
    movi r7, 79
    movi r8, 0
    br .Lhandshake_rx
.Lhandshake_next:
    addi r8, r8, 1
    ldr.b r7, (r9, r8 << 0)
    bnez r7, .Lhandshake_rx
.Lhandshake_trap:
    pop r4-r9, r15
    bkpt
    /* The assembler emits its literal pool (0x20002010, 0x20002014,
     * 0x10001E5C) here, matching the stock pool words at
     * 0x10000774..0x1000077F. No explicit .word: a label pool would
     * take the address-load indirection form. */
.size open_cfw_gx8002_uart_stage1_handshake, .-open_cfw_gx8002_uart_stage1_handshake
