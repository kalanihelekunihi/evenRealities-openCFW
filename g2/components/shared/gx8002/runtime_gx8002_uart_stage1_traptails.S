/* SPDX-License-Identifier: MIT */
/* Reviewed rail-configure trap tails for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x1000046C (package 0x4BC, 56 bytes) and runtime
 * 0x100004A4 (package 0x4F4, 44 bytes).
 *
 * Clean-room assembly implementing the decoded stock behavior of the two
 * small H-class flows that feed the PMU rail dispatchers: the 0x46C
 * counter-tick setup (PMU fill id 23 through the first dispatcher,
 * counter-2 control words at the 0xA0400000 block, PMU fill id 23
 * through the second dispatcher, then a signed clock/1000000 reload
 * computation) and the 0x4A4 block clear (status reads plus 0x30/0x6C
 * clears at the 0xA0500000/0xA0600000 blocks, then PMU fills ids 20
 * and 21 through the first dispatcher). Both end in pop-then-bkpt and
 * never return: every terminal path of the called dispatchers pops its
 * frame and falls into the retained second-dispatcher loop (no rts),
 * so the first dispatcher call already leaves this code (same
 * H-class precedent as the reviewed rail/postamble/uartcfg leaves).
 *
 * Assembly (rather than C) because both envelopes are dense
 * hand-scheduled 16-bit traffic ending in a trapping bkpt word, and
 * the transliteration below assembles byte-identical to stock (56/44
 * bytes, exact fill, no padding). No SDK text is reproduced and no SDK
 * register map is used: the 0xA0400000/0xA0500000/0xA0600000 bases and
 * every offset, id, and constant below is a numeric immediate observed
 * in the decoded stock flow. The pinned upstream SDK checkout is not a
 * build input to this leaf.
 *
 * The cross-envelope dispatcher calls target linker-assigned absolute
 * symbols (mdelay/uartcfg-leaf precedent), so the linked sections
 * carry no relocations; the reviewed dispatcher bodies are the
 * production callees and are qualified by their own batteries.
 *
 * Behavior summary (see the audit doc for the full decode):
 * 0x46C: push r4-r5, r15; r4 = 0xA0400000; (r0, r1) = (23, 1) into the
 * first dispatcher; [r4+0x10] = 1 then 0 with r0 = 23; [r4+0x20] = 1;
 * r0 = 23 into the second dispatcher; r3 = 62500 rotl 4 (= 1000000);
 * r0 = r0 / r3 signed minus 1; [r4+0x24] = r0; [r4+0x28] = 0;
 * [r4+0x10] = 2; pop; bkpt.
 * 0x4A4: push r4, r15; r3 = 0xA0500000; r2 = [r3+0x40] (discarded);
 * [r3+0x30] = [r3+0x6C] = 0; r3 = 0xA0600000 with (r0, r1) = (20, 0);
 * r2 = [r3+0x40] (discarded); [r3+0x30] = [r3+0x6C] = 0; (r0, r1) =
 * (20, 0) into the first dispatcher; (r0, r1) = (21, 0) into the
 * first dispatcher; pop; bkpt.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-traptails-source.md): exact prefix
 * access-trace, final-RAM, and at-chain-register agreement from entry
 * to the first dispatcher call on both sides, plus byte identity of
 * both full envelopes.
 */
.section .text.open_cfw_gx8002_uart_stage1_railcfg,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_railcfg
.type open_cfw_gx8002_uart_stage1_railcfg,@function
open_cfw_gx8002_uart_stage1_railcfg:
    /* Counter-tick setup (stock 0x46C..0x4A2) plus trap word. */
    push r4-r5, r15
    movih r4, 0xA040
    movi r1, 1
    movi r0, 23
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    movi r5, 0
    movi r3, 1
    st.w r3, (r4, 0x10)
    movi r0, 23
    st.w r5, (r4, 0x10)
    st.w r3, (r4, 0x20)
    bsr open_cfw_gx8002_uart_boot_stage1_ea0_entry
    movi r3, 62500
    rotli r3, r3, 4
    divs r0, r0, r3
    subi r0, 1
    movi r3, 2
    st.w r0, (r4, 0x24)
    st.w r5, (r4, 0x28)
    st.w r3, (r4, 0x10)
    pop r4-r5, r15
    bkpt

.section .text.open_cfw_gx8002_uart_stage1_blkclr,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_blkclr
.type open_cfw_gx8002_uart_stage1_blkclr,@function
open_cfw_gx8002_uart_stage1_blkclr:
    /* Block clear plus rail fills (stock 0x4A4..0x4CE) plus trap word. */
    push r4, r15
    movih r3, 0xA050
    movi r4, 0
    ld.w r2, (r3, 0x40)
    st.w r4, (r3, 0x30)
    st.w r4, (r3, 0x6c)
    movih r3, 0xA060
    mov r1, r4
    ld.w r2, (r3, 0x40)
    movi r0, 20
    st.w r4, (r3, 0x30)
    st.w r4, (r3, 0x6c)
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    mov r1, r4
    movi r0, 21
    bsr open_cfw_gx8002_uart_boot_stage1_d98_entry
    pop r4, r15
    bkpt
