/* SPDX-License-Identifier: MIT
 * Reconstructed 0x432958..0x43297a, startup CPACR/FPSCR initialization.
 * CP10/CP11 full-access mask and exact FPSCR value recovered from the image.
 */
.syntax unified
.thumb
.fpu fpv4-sp-d16
.text
.global opencfw_boot_fpu_init
.thumb_func
opencfw_boot_fpu_init:
    movw r1,#0xed88
    movt r1,#0xe000
    ldr r0,[r1]
    orr r0,r0,#0x00f00000
    str r0,[r1]
    dsb sy
    isb sy
    mov r0,#0x02040000
    vmsr fpscr,r0
    bx lr
.section .note.GNU-stack,"",%progbits
