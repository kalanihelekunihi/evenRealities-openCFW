/* SPDX-License-Identifier: MIT */
/* Derived from NationalChip lvp_kws arch/cpu/csky/ck804/spl_start.S at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. See NATIONALCHIP-SPL-STARTUP-NOTICE.txt.
 * This is the image-A flash-resident BINH stage-one block's reset chain: it
 * runs first, out of codec MCU IRAM at power-on (flash 0x0 copied to
 * 0x10000000 by the mask ROM), before the already-reconstructed stage-two
 * entry (open_cfw_gx8002_reset_entry, runtime_gx8002_reset_entry.S) runs.
 * Source symbols replace configuration/link addresses; stock is only an
 * oracle. spl_board_init_r is a genuine external call boundary: its content
 * is not reconstructed here and remains retained stock at its own address.
 */
.section .text.open_cfw_gx8002_spl_reset_entry,"ax",@progbits
.balign 4
.global open_cfw_gx8002_spl_reset_entry
.type open_cfw_gx8002_spl_reset_entry,@function
open_cfw_gx8002_spl_reset_entry:
    lrw r0, 0x80000200
    mtcr r0, psr
    mfcr r1, cr<31,0>
    bclri r1, 3
    mtcr r1, cr<31,0>
    lrw r0, open_cfw_gx8002_spl_vectors
    mtcr r0, vbr
    lrw r0, open_cfw_gx8002_spl_initial_stack
    mov sp, r0
    bsr open_cfw_gx8002_spl_board_init_r
    bsr open_cfw_gx8002_reset_entry
.size open_cfw_gx8002_spl_reset_entry, .-open_cfw_gx8002_spl_reset_entry

/* Every non-reset vector in the SPL vector table (open_cfw_gx8002_spl_vectors,
 * see runtime_gx8002_image_a_stage1_header.c) targets this trap loop. */
.section .text.open_cfw_gx8002_spl_default_handler,"ax",@progbits
.balign 4
.global open_cfw_gx8002_spl_default_handler
.type open_cfw_gx8002_spl_default_handler,@function
open_cfw_gx8002_spl_default_handler:
    br open_cfw_gx8002_spl_default_handler
.size open_cfw_gx8002_spl_default_handler, .-open_cfw_gx8002_spl_default_handler

/* The public spl_start.S also defines spl_clear_bss as a bare "rts": the SPL
 * stage never actually calls it (spl_board_init_r/reset_entry own real BSS
 * clearing), so this stub reconstructs the unreachable placeholder byte-exactly
 * without claiming any BSS-clearing behavior for it. */
.section .text.open_cfw_gx8002_spl_clear_bss,"ax",@progbits
.balign 4
.global open_cfw_gx8002_spl_clear_bss
.type open_cfw_gx8002_spl_clear_bss,@function
open_cfw_gx8002_spl_clear_bss:
    rts
.size open_cfw_gx8002_spl_clear_bss, .-open_cfw_gx8002_spl_clear_bss
