/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Isolated, non-production Clang-assembly adaptation of the interrupt-mask
 * pair from:
 *
 *   FreeRTOS-Kernel V10.5.1
 *   commit def7d2df2b0506d3d249334974f51e427c17a41c
 *   portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s, lines 156-169
 *
 * The official G2 Apollo-main image owns the contiguous range
 * [0x005FA0A4, 0x005FA0C8):
 *
 *   ulSetInterruptMask  [0x005FA0A4, 0x005FA0BA), 22 bytes
 *   vClearInterruptMask [0x005FA0BA, 0x005FA0C8), 14 bytes
 *
 * The only recovered configuration input is the shifted BASEPRI value
 * configMAX_SYSCALL_INTERRUPT_PRIORITY = 0x30.  Keep this pair in privileged
 * Cortex-M55 code.  It is deliberately not registered by either production
 * overlay.
 */

    .syntax unified
    .cpu cortex-m55
    .thumb

    .section .text, "ax", %progbits
    .p2align 1

    .global ulSetInterruptMask
    .type ulSetInterruptMask, %function
    .thumb_func
ulSetInterruptMask:
    mrs     r0, basepri
    mov.w   r1, #0x30
    msr     basepri, r1
    dsb     sy
    isb     sy
    bx      lr
    .size ulSetInterruptMask, . - ulSetInterruptMask

    .global vClearInterruptMask
    .type vClearInterruptMask, %function
    .thumb_func
vClearInterruptMask:
    msr     basepri, r0
    dsb     sy
    isb     sy
    bx      lr
    .size vClearInterruptMask, . - vClearInterruptMask

    .section .note.GNU-stack, "", %progbits
