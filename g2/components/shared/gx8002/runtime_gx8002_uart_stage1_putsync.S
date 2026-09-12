/* SPDX-License-Identifier: MIT */
/* Reviewed blocking UART transmit-then-wait leaf for the GX8002 UART boot
 * stage 1 (IRAM) image: runtime 0x100005a0, package 0x5f0, 36 bytes
 * (32 bytes of code plus the 4-byte base-cell literal pool).
 *
 * Clean-room assembly implementing the decoded stock behavior, identified
 * against the pinned NationalChip grus SDK `arch/soc/grus/spl/spl_uart.c`
 * `serial_put_sync` at commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5
 * (no per-file license header; used under the SDK repo-level MIT LICENSE;
 * no SDK text reproduced and the GPL SDK headers are not used): poll the
 * line-status register (block offset 0x14) for transmitter-empty (bit 6),
 * write the word to the transmit register (block offset 0x0), then poll
 * transmitter-empty again before returning. The UART block base comes from
 * the stage-1 data word at 0x20002014, read once up front.
 *
 * Assembly (rather than C) because every probed C shape for this two-loop
 * body compiles to 38 bytes against the 36-byte stock envelope: the
 * allocator spills the first-loop status load into a high register (4-byte
 * `ld.w`) while the stock (older NationalChip) toolchain keeps it in a
 * low register (2-byte `ld.w`). The sequence below is verified by
 * decoded-target execution comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-serial-source.md), not by byte identity,
 * though it additionally assembles byte-identically to the stock envelope.
 */
.section .text.open_cfw_gx8002_uart_stage1_put_sync,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_put_sync
.type open_cfw_gx8002_uart_stage1_put_sync,@function
open_cfw_gx8002_uart_stage1_put_sync:
    lrw r3, 0x20002014
    ld.w r1, (r3, 0x0)
    addi r2, r1, 20
1:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 64
    bez r3, 1b
    st.w r0, (r1, 0x0)
2:
    ld.w r3, (r2, 0x0)
    andi r3, r3, 64
    bez r3, 2b
    rts
.size open_cfw_gx8002_uart_stage1_put_sync, .-open_cfw_gx8002_uart_stage1_put_sync
