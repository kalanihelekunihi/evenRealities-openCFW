/* SPDX-License-Identifier: MIT. Stock41b8e0 reads PRIMASK then enables IRQs. */
.syntax unified
.thumb
.text
.global opencfw_bl_irq_guard_initialize
.type opencfw_bl_irq_guard_initialize,%function
.thumb_func
opencfw_bl_irq_guard_initialize:
    mrs r0, primask
    cpsie i
    bx lr
.size opencfw_bl_irq_guard_initialize, .-opencfw_bl_irq_guard_initialize

.section .note.GNU-stack,"",%progbits
