/* SPDX-License-Identifier: MIT
 * Stock 0x41b954 saves R1 and restores it at its shared return. */
.syntax unified
.thumb
.section .text.opencfw_boot_control_transition,"ax",%progbits
.global opencfw_boot_control_transition
.type opencfw_boot_control_transition,%function
.thumb_func
opencfw_boot_control_transition:
    b.w opencfw_boot_control_transition_core
.size opencfw_boot_control_transition,.-opencfw_boot_control_transition
.section .note.GNU-stack,"",%progbits
