/* SPDX-License-Identifier: MIT */
/* GX8002 UART boot stage 1 (IRAM) vector table and trap entries.
 *
 * Clean-room assembly emitting the 64-word CK804 vector table at runtime
 * 0x10000000 (package 0x50, 256 bytes) and the two shared trap entries
 * at runtime 0x10000130/0x10000134 (package 0x180, 8 bytes). The table
 * is fully determined by three addresses, recovered from the stock
 * bytes: word 0 is the reset entry 0x10000100 (the reset prologue
 * reconstructed in runtime_gx8002_uart_boot_stage1_reset.S), words
 * 1..31 are the shared exception target 0x10000130, and words 32..63
 * are the shared IRQ target 0x10000134. Each trap is a `br` to itself
 * (an infinite wait loop); the 2-byte zero pad after each `br` is
 * assembler alignment fill (`.balign 4`), matching the stock bytes,
 * which disassemble as `bkpt` only because 0x0000 is the CK804
 * breakpoint encoding. No upstream text is used; the only external
 * input is the reset-entry address, supplied as the absolute linker
 * symbol open_cfw_gx8002_uart_stage1_reset_entry so this file stays
 * assemblable on its own. Stock is only an oracle: the linked
 * sections are byte-exact against the package envelopes. See
 * docs/research/gx8002-uart-stage1-vectors-source.md and
 * NATIONALCHIP-UART-BOOT-STAGE1-VECTORS-NOTICE.txt.
 */
.section .rodata.open_cfw_gx8002_uart_stage1_vectors,"a",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_vectors
open_cfw_gx8002_uart_stage1_vectors:
    .word open_cfw_gx8002_uart_stage1_reset_entry
    .rept 31
    .word open_cfw_gx8002_uart_stage1_exc_trap
    .endr
    .rept 32
    .word open_cfw_gx8002_uart_stage1_irq_trap
    .endr
    .size open_cfw_gx8002_uart_stage1_vectors, .-open_cfw_gx8002_uart_stage1_vectors
.section .text.open_cfw_gx8002_uart_stage1_traps,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_traps
.global open_cfw_gx8002_uart_stage1_exc_trap
.global open_cfw_gx8002_uart_stage1_irq_trap
open_cfw_gx8002_uart_stage1_traps:
open_cfw_gx8002_uart_stage1_exc_trap:
    br open_cfw_gx8002_uart_stage1_exc_trap
    .balign 4
open_cfw_gx8002_uart_stage1_irq_trap:
    br open_cfw_gx8002_uart_stage1_irq_trap
    .balign 4
.size open_cfw_gx8002_uart_stage1_traps, .-open_cfw_gx8002_uart_stage1_traps
