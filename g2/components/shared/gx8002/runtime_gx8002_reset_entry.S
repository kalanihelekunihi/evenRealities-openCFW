/* SPDX-License-Identifier: MIT */
/* Derived from NationalChip lvp_kws arch/cpu/csky/ck804/start.S at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. See NATIONALCHIP-STARTUP-NOTICE.txt.
 * Source symbols replace configuration/link addresses; stock is only an oracle.
 * The return loop is the original __exit behavior if main returns. */
.section .text.open_cfw_gx8002_reset_entry,"ax",@progbits
.balign 4
.global open_cfw_gx8002_reset_entry
.type open_cfw_gx8002_reset_entry,@function
open_cfw_gx8002_reset_entry:
    lrw r0, 0x80000200
    mtcr r0, psr
    mfcr r1, cr<31,0>
    bclri r1, 3
    mtcr r1, cr<31,0>
    lrw r3, open_cfw_gx8002_initial_stack
    mov sp, r3
    bsr open_cfw_gx8002_system_initialize
    bsr open_cfw_gx8002_main
.Lreturned_main:
    br .Lreturned_main
.size open_cfw_gx8002_reset_entry, .-open_cfw_gx8002_reset_entry
