/* SPDX-License-Identifier: MIT
 * Architectural source: set vector base, load MSP, branch to reset handler.
 * No validation/barriers/IRQ cleanup are present in the stock leaf. */
.syntax unified
.thumb
.section .text.opencfw_boot_vector_handoff,"ax",%progbits
.global opencfw_boot_vector_handoff
.type opencfw_boot_vector_handoff,%function
.thumb_func
opencfw_boot_vector_handoff:
    movw r1, #0xed08
    movt r1, #0xe000
    str r0, [r1]
    ldr sp, [r0]
    ldr r1, [r0, #4]
    bx r1
.size opencfw_boot_vector_handoff, .-opencfw_boot_vector_handoff

.section .note.GNU-stack,"",%progbits
