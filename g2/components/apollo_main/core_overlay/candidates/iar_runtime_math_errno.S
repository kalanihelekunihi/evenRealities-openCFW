/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room Thumb-2 recreation of the compact IAR DLIB math/errno boundary
 * authenticated in the G2 2.2.6.10 Apollo-main image. The exact EWARM release
 * is deliberately not claimed. The behavior and hard-float ABI are recovered
 * from the bounded stock functions and their complete ingress topology.
 */

    .syntax unified
    .cpu cortex-m55
    .fpu fpv5-sp-d16
    .thumb

#ifndef OPEN_CFW_IAR_MATH_ERRNO_SELECTION
#define OPEN_CFW_IAR_MATH_ERRNO_SELECTION -1
#endif

    .macro OPEN_CFW_SET_ERRNO error_number
    /* Preserve the same result-bearing core registers as the stock helpers. */
    push    {r0, r1, r2, r3, lr}
    sub     sp, sp, #4
    movw    r1, #0x4f14
    movt    r1, #0x2007
    movs    r2, #\error_number
    str     r2, [r1]
    add     sp, sp, #4
    pop     {r0, r1, r2, r3, pc}
    .endm

#if OPEN_CFW_IAR_MATH_ERRNO_SELECTION == -1 || OPEN_CFW_IAR_MATH_ERRNO_SELECTION == 0
    .section .text.open_cfw_iar_sqrtf, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_sqrtf
    .type open_cfw_iar_sqrtf, %function
    .thumb_func
open_cfw_iar_sqrtf:
    vcmpe.f32 s0, #0
    vmrs    APSR_nzcv, FPSCR
    bmi     .Lsqrtf_domain
    vsqrt.f32 s0, s0
    bx      lr
.Lsqrtf_domain:
    mvn     r12, #0x80000000
    vmov    s0, r12
    b.w     open_cfw_iar_domain_error
    .size open_cfw_iar_sqrtf, . - open_cfw_iar_sqrtf
#endif

#if OPEN_CFW_IAR_MATH_ERRNO_SELECTION == -1 || OPEN_CFW_IAR_MATH_ERRNO_SELECTION == 1
    .section .text.open_cfw_iar_domain_error, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_domain_error
    .type open_cfw_iar_domain_error, %function
    .thumb_func
open_cfw_iar_domain_error:
    OPEN_CFW_SET_ERRNO 33
    .size open_cfw_iar_domain_error, . - open_cfw_iar_domain_error
#endif

#if OPEN_CFW_IAR_MATH_ERRNO_SELECTION == -1 || OPEN_CFW_IAR_MATH_ERRNO_SELECTION == 2
    .section .text.open_cfw_iar_range_error, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_range_error
    .type open_cfw_iar_range_error, %function
    .thumb_func
open_cfw_iar_range_error:
    OPEN_CFW_SET_ERRNO 34
    .size open_cfw_iar_range_error, . - open_cfw_iar_range_error
#endif

#if OPEN_CFW_IAR_MATH_ERRNO_SELECTION == -1 || OPEN_CFW_IAR_MATH_ERRNO_SELECTION == 3
    .section .text.open_cfw_iar_errno_address, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_errno_address
    .type open_cfw_iar_errno_address, %function
    .thumb_func
open_cfw_iar_errno_address:
    movw    r0, #0x4f14
    movt    r0, #0x2007
    bx      lr
    .size open_cfw_iar_errno_address, . - open_cfw_iar_errno_address
#endif
