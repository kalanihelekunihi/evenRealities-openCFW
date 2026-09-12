/* SPDX-License-Identifier: MIT */
/* Reviewed UART announce leaf for the GX8002 UART boot stage 1 (IRAM)
 * image: runtime 0x1000065C (package 0x6AC, 124 bytes).
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * H-class flow that sits between the polled-UART receive leaf
 * (get_char at 0x10000640, serial tranche) and the boot handshake
 * (0x100006D8, still retained). The leaf reads the UART block base
 * from the base cell at 0x20002014, raises the rail-control word at
 * [base+0xA8], then chains into the retained rail-program entry at
 * 0x10001BF8 with the entry arguments plus a rail-select id (4 when
 * the base differs from the first UART, 6 when it already matches).
 * The rail-program entry runs straight-line push/movs into the
 * reviewed first PMU dispatcher (0x10000D98, noreturn per the
 * pmudisp audit), so the first chaining call already leaves this
 * envelope: the polled "ready" transmit loop, the reviewed
 * rail-postamble call (0x10001D9C), and the pop-return after it
 * never execute and are admitted by byte identity.
 *
 * Assembly (rather than C) because the envelope is dense
 * hand-scheduled 16-bit traffic with an inline literal pool, and the
 * transliteration below assembles byte-identical to stock (124
 * bytes, exact fill, no relocations), so there is nothing for C to
 * approximate. No SDK text is reproduced and no SDK register map is
 * used: the 0x20002014 cell, the 0xA0100000 base, and every offset,
 * id, and constant below is a numeric immediate observed in the
 * decoded stock flow. The pinned upstream SDK checkout is not a
 * build input to this leaf.
 *
 * The cross-envelope calls target linker-assigned absolute symbols
 * (uartcfg/traptails-leaf precedent), so the linked section carries
 * no relocations; the retained rail-program head executes
 * identically on both sides and is never stepped into here, and the
 * reviewed postamble body is qualified by its own battery.
 *
 * Behavior summary (see the audit doc for the full decode):
 * 0x65C: push r4, r15; r4 = pool 0x20002014; r3 = 0xA0100000;
 * r12 = [r4]; [r12+0xA8] = 1; r3 = (r12 != 0xA0100000) ? 4 : 6;
 * (r0, r1, r2, r3) = (entry r0, r12, entry r1, select) into 0x1BF8;
 * post-chain (unreachable): re-read base, poll [base+20] bit 6
 * until set, transmit "ready" (114, 101, 97, 100, 121), call the
 * rail postamble, return 0 via pop r4, r15.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-announce-source.md): exact
 * prefix access-trace, final-RAM, and at-chain-register agreement
 * from entry to the chaining call on both sides, plus byte identity
 * of the full envelope.
 */
.section .text.open_cfw_gx8002_uart_stage1_announce,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_announce
.type open_cfw_gx8002_uart_stage1_announce,@function
open_cfw_gx8002_uart_stage1_announce:
    /* UART announce (stock 0x65C..0x6D3) plus literal pool. */
    push r4, r15
    lrw r4, 0x20002014
    movih r3, 40976
    ld.w r12, (r4, 0x0)
    cmpne r12, r3
    movi r3, 1
    st.w r3, (r12, 0xa8)
    movi r2, 4
    movi r3, 6
    inct r3, r2, 0
    mov r2, r1
    mov r1, r12
    bsr open_cfw_gx8002_uart_boot_stage1_1bf8_entry
    ld.w r1, (r4, 0x0)
    addi r3, r1, 20
.Lannounce_tx0:
    ld.w r2, (r3, 0x0)
    andi r2, r2, 64
    bez r2, .Lannounce_tx0
    movi r2, 114
    st.w r2, (r1, 0x0)
.Lannounce_tx1:
    ld.w r2, (r3, 0x0)
    andi r2, r2, 64
    bez r2, .Lannounce_tx1
    movi r2, 101
    st.w r2, (r1, 0x0)
.Lannounce_tx2:
    ld.w r2, (r3, 0x0)
    andi r2, r2, 64
    bez r2, .Lannounce_tx2
    movi r2, 97
    st.w r2, (r1, 0x0)
.Lannounce_tx3:
    ld.w r2, (r3, 0x0)
    andi r2, r2, 64
    bez r2, .Lannounce_tx3
    movi r2, 100
    st.w r2, (r1, 0x0)
.Lannounce_tx4:
    ld.w r2, (r3, 0x0)
    andi r2, r2, 64
    bez r2, .Lannounce_tx4
    movi r3, 121
    st.w r3, (r1, 0x0)
    bsr open_cfw_gx8002_uart_boot_stage1_1d9c_entry
    movi r0, 0
    pop r4, r15
    /* The assembler emits its literal pool (0x20002014) here,
     * matching the stock pool word at 0x100006D4. No explicit
     * .word: a label pool would take the address-load
     * indirection form. There is no trap word in this envelope:
     * the pool directly follows the pop. */
.size open_cfw_gx8002_uart_stage1_announce, .-open_cfw_gx8002_uart_stage1_announce
