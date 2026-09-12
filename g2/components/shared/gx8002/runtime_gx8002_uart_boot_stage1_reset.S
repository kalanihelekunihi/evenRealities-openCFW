/* SPDX-License-Identifier: MIT */
/* Derived from NationalChip lvp_kws arch/cpu/csky/ck804/spl_start.S at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. See
 * NATIONALCHIP-UART-BOOT-STAGE1-RESET-NOTICE.txt.
 * This is the UART boot stage 1 (IRAM) reset entry: the mask-ROM copy of
 * the UART boot header runs here at 0x10000100 after loading stage one to
 * 0x10000000. It uses the same upstream spl_reset_handler shape as the
 * image-A SPL reconstruction (runtime_gx8002_spl_reset_entry.S) with the
 * UART-boot recovered configuration: the vector base is the stage-1 table
 * at IRAM base, the stack is 0x200027fc, the first call is the stage-1
 * init routine, and the second call chain-loads the stage-2 code entry at
 * 0x10002900 (stage-two load address 0x10002800 plus its 256-byte vector
 * table). Upstream jbsr is adapted to bsr to match the stock encoding.
 * Source symbols replace configuration/link addresses; stock is only an
 * oracle. The init and stage-2 targets are genuine external call
 * boundaries: their contents are not reconstructed here and remain
 * retained stock at their own addresses.
 */
.section .text.open_cfw_gx8002_uart_boot_stage1_reset,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_boot_stage1_reset
.type open_cfw_gx8002_uart_boot_stage1_reset,@function
open_cfw_gx8002_uart_boot_stage1_reset:
    lrw r0, 0x80000200
    mtcr r0, psr
    mfcr r1, cr<31,0>
    bclri r1, 3
    mtcr r1, cr<31,0>
    lrw r0, open_cfw_gx8002_uart_stage1_vectors
    mtcr r0, vbr
    lrw r0, open_cfw_gx8002_uart_stage1_initial_stack
    mov sp, r0
    bsr open_cfw_gx8002_uart_stage1_init
    bsr open_cfw_gx8002_uart_stage2_entry
.size open_cfw_gx8002_uart_boot_stage1_reset, .-open_cfw_gx8002_uart_boot_stage1_reset
