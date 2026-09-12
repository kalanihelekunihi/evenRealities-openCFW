/* SPDX-License-Identifier: MIT */
/* Reviewed baud-beacon and UART bring-up leaves for the GX8002 UART boot
 * stage 1 (IRAM) image: runtime 0x100004D0 (package 0x520, 180 bytes)
 * and runtime 0x100005C4 (package 0x614, 92 bytes).
 *
 * Clean-room assembly implementing the decoded stock behavior of the two
 * H-class flows that sit between the serial leaves and the PMU rail
 * dispatchers. The 0x4D0 beacon programs the UART block control words,
 * polls the receiver line-status bit, then chains into the retained
 * second PMU dispatcher entry (0x10000EA0) with a clock id (18, or 17
 * when the block base is already the first UART); every terminal path
 * of that dispatcher pops its frame and falls into the retained
 * second-dispatcher loop with no rts (pmusecond audit), so the baud
 * quotient/remainder math and the transmit loop after the chain never
 * execute. The 0x5C4 bring-up reads the flag cell at 0x20002008: when
 * nonzero it chains into the beacon with (115200, 0), otherwise it
 * selects the UART base cell at 0x20002014 from the 0x2000200C word,
 * runs PMU fills 16/17/18 through the first dispatcher (0x10000D98,
 * likewise noreturn per the pmudisp audit), and chains into the beacon
 * with the entry arguments. Neither leaf returns.
 *
 * Assembly (rather than C) because both envelopes are dense
 * hand-scheduled 16-bit traffic with inline literal pools and end in a
 * trapping bkpt word, and the transliteration below assembles
 * byte-identical to stock (180/92 bytes, exact fill, no relocations).
 * No SDK text is reproduced and no SDK register map is used: the
 * 0x20002008/0x20002014 cells, the 0xA0100000/0xA0200000 bases, and
 * every offset, id, and constant below is a numeric immediate observed
 * in the decoded stock flow. The pinned upstream SDK checkout is not a
 * build input to this leaf.
 *
 * The cross-envelope calls target linker-assigned absolute symbols
 * (mdelay/uartcfg/traptails-leaf precedent), so the linked sections
 * carry no relocations; the reviewed dispatcher bodies are the
 * production callees and are qualified by their own batteries, and the
 * div/mod bodies past the beacon chain are qualified by the reviewed
 * divmod tranche. The retained 0x10000EA0 head executes identically on
 * both sides and is never stepped into here.
 *
 * Behavior summary (see the audit doc for the full decode):
 * 0x4D0: push r4-r7, r15; r6 = pool 0x20002014; r4 = r0;
 * [base+0x4] = 0; [base+0x10] = 3; if r1 != 0: poll [base+124] bit 0
 * until clear, [base+12] = 3, [base+8] = 79, pop; if base ==
 * 0xA0100000: r0 = 17 into 0xEA0, else r0 = 18 into 0xEA0;
 * post-chain (unreachable): clock/div baud math, TX loop; bkpt.
 * 0x5C4: push r4-r5, r15; r3 = pool 0x20002008; r5 = r0; r2 = [r3];
 * r4 = r1; if r2 != 0: (r0, r1) = (115200, 0) into the beacon; else
 * r3 = [r3+4]; r3 = (r3 != 1) ? 0xA0100000 : 0xA0200000;
 * [0x20002014] = r3; (r0, r1) = (16, 1), (17, 1), (18, 1) into 0xD98;
 * (r0, r1) = (r4, r5) into the beacon; post-chain (unreachable):
 * pop; bkpt.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-beacon-source.md): exact prefix
 * access-trace, final-RAM, and at-chain-register agreement from entry
 * to the chaining call on both sides, plus byte identity of both full
 * envelopes.
 */
.section .text.open_cfw_gx8002_uart_stage1_beacon,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_beacon
.type open_cfw_gx8002_uart_stage1_beacon,@function
open_cfw_gx8002_uart_stage1_beacon:
    /* Baud beacon (stock 0x4D0..0x57D) plus trap word and pool. */
    push r4-r7, r15
    lrw r6, 0x20002014
    movi r3, 0
    ld.w r12, (r6, 0x0)
    mov r4, r0
    st.w r3, (r12, 0x4)
    movi r3, 3
    st.w r3, (r12, 0x10)
    bez r1, .Lbeacon_cmpbase
    addi r2, r12, 124
    addi r1, r12, 12
.Lbeacon_poll:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 1
    bnez r3, .Lbeacon_poll
    movi r3, 3
    st.w r3, (r1, 0x0)
    movi r3, 79
    st.w r3, (r12, 0x8)
    pop r4-r7, r15
.Lbeacon_cmpbase:
    movih r3, 40976
    cmpne r12, r3
    bf .Lbeacon_clk17
    movi r0, 18
    bsr open_cfw_gx8002_uart_boot_stage1_ea0_entry
    mov r7, r0
.Lbeacon_divmath:
    lsli r4, r4, 4
    mov r1, r4
    mov r0, r7
    bsr open_cfw_gx8002_uart_boot_stage1_div_entry
    mov r5, r0
    mov r1, r4
    mov r0, r7
    bsr open_cfw_gx8002_uart_boot_stage1_mod_entry
    movi r7, 100
    mov r1, r4
    mult r0, r7
    bsr open_cfw_gx8002_uart_boot_stage1_div_entry
    lsli r0, r0, 4
    mov r1, r7
    bsr open_cfw_gx8002_uart_boot_stage1_div_entry
    ld.w r12, (r6, 0x0)
    addi r2, r12, 124
.Lbeacon_poll2:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 1
    bnez r3, .Lbeacon_poll2
    movi r3, 128
    st.w r3, (r12, 0xc)
    andi r0, r0, 255
    andi r3, r5, 255
    zext r5, r5, 15, 8
    st.w r3, (r12, 0x0)
    addi r1, r12, 12
    st.w r5, (r12, 0x4)
    st.w r0, (r12, 0xc0)
    br .Lbeacon_poll
.Lbeacon_clk17:
    movi r0, 17
    bsr open_cfw_gx8002_uart_boot_stage1_ea0_entry
    mov r7, r0
    br .Lbeacon_divmath
    bkpt

.section .text.open_cfw_gx8002_uart_stage1_bringup,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_bringup
.type open_cfw_gx8002_uart_stage1_bringup,@function
open_cfw_gx8002_uart_stage1_bringup:
    /* UART bring-up (stock 0x5C4..0x615) plus trap word and pools. */
    push r4-r5, r15
    lrw r3, 0x20002008
    mov r5, r0
    ld.w r2, (r3, 0x0)
    mov r4, r1
    bnez r2, .Lbringup_beacon115200
    ld.w r3, (r3, 0x4)
    cmpnei r3, 1
    movih r2, 40976
    movih r3, 40992
    inct r3, r2, 0
    lrw r2, 0x20002014
    movi r1, 1
    movi r0, 16
    st.w r3, (r2, 0x0)
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    movi r1, 1
    movi r0, 17
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    movi r1, 1
    movi r0, 18
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    mov r1, r5
    mov r0, r4
    bsr open_cfw_gx8002_uart_stage1_beacon
    pop r4-r5, r15
.Lbringup_beacon115200:
    movi r1, 0
    movi r0, 49664
    bseti r0, 16
    bsr open_cfw_gx8002_uart_stage1_beacon
    pop r4-r5, r15
    bkpt
