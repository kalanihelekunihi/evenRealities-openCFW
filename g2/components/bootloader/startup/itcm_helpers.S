/* SPDX-License-Identifier: MIT
 * Source instructions recovered from the24byte ITCM initializer at0x40.
 * Counter values are raw loop counts, not calibrated time units.
 */
.syntax unified
.thumb
.section .text.itcm_helpers,"ax",%progbits
.global opencfw_boot_itcm_countdown
.type opencfw_boot_itcm_countdown,%function
.thumb_func
opencfw_boot_itcm_countdown:
1: subs r0,#1
   bne 1b
   bx lr
.size opencfw_boot_itcm_countdown,.-opencfw_boot_itcm_countdown
.global opencfw_boot_itcm_noop_46
.type opencfw_boot_itcm_noop_46,%function
.thumb_func
opencfw_boot_itcm_noop_46:
   bx lr
.size opencfw_boot_itcm_noop_46,.-opencfw_boot_itcm_noop_46
.global opencfw_boot_itcm_word_copy
.type opencfw_boot_itcm_word_copy,%function
.thumb_func
opencfw_boot_itcm_word_copy:
1: ldr r3,[r0],#4
   str r3,[r1],#4
   subs r2,#1
   bne 1b
   bx lr
.size opencfw_boot_itcm_word_copy,.-opencfw_boot_itcm_word_copy
.global opencfw_boot_itcm_noop_56
.type opencfw_boot_itcm_noop_56,%function
.thumb_func
opencfw_boot_itcm_noop_56:
   bx lr
.size opencfw_boot_itcm_noop_56,.-opencfw_boot_itcm_noop_56
.section .note.GNU-stack,"",%progbits
