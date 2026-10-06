/* SPDX-License-Identifier: MIT */
/* Preserve the stock 0x4201ba local's exact stack position and size. */
.syntax unified
.thumb
.section .text.opencfw_provider_4201ba,"ax",%progbits
.global opencfw_provider_4201ba
.type opencfw_provider_4201ba,%function
.thumb_func
opencfw_provider_4201ba:
    push    {r7, lr}
    sub     sp, #0x28
    movs    r2, #6
    movs    r1, #0
    add     r0, sp, #0x20
    bl      opencfw_bl_clear
    add     r0, sp, #0x20
    bl      opencfw_provider_4201ba_core
    add     sp, #0x2c
    pop     {pc}
.size opencfw_provider_4201ba, .-opencfw_provider_4201ba
.section .note.GNU-stack,"",%progbits
