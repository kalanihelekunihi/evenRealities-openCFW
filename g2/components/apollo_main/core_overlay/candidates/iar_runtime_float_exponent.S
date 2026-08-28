/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Thumb-2 recreation of the IAR DLIB binary32 exponent helpers
 * identified in the G2 2.2.6.10 image. No proprietary IAR source was used.
 */

    .syntax unified
    .cpu cortex-m55
    .fpu fpv5-sp-d16
    .thumb

#ifndef OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION
#define OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION -1
#endif

#if OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == -1 || OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == 0
    .section .text.open_cfw_iar_frexpf, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_frexpf
    .type open_cfw_iar_frexpf, %function
    .thumb_func
open_cfw_iar_frexpf:
    mov     r3, r0
    vmov    r0, s0
    mov     r12, lr
    bl      open_cfw_iar_frexpf_bits
    str     r1, [r3]
    vmov    s0, r0
    bx      r12
    .size open_cfw_iar_frexpf, . - open_cfw_iar_frexpf
#endif

#if OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == -1 || OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == 1
    .section .text.open_cfw_iar_frexpf_bits, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_frexpf_bits
    .type open_cfw_iar_frexpf_bits, %function
    .thumb_func
open_cfw_iar_frexpf_bits:
    ubfx    r1, r0, #23, #8
    cbz     r1, .Lfrexp_subnormal
    cmp     r1, #255
    beq     .Lfrexp_special
    subs    r1, r1, #126
    sub     r0, r0, r1, lsl #23
    bx      lr
.Lfrexp_subnormal:
    cmn     r0, r0
    beq     .Lfrexp_zero
    and     r2, r0, #0x80000000
    lsls    r0, r0, #9
    clz     r1, r0
    lsls    r0, r0, r1
    adds    r1, r1, #126
    rsbs    r1, r1, #0
    orr     r0, r2, r0, lsr #8
    add     r0, r0, #0x3e800000
    bx      lr
.Lfrexp_special:
    movs    r1, #0
.Lfrexp_zero:
    bx      lr
    .size open_cfw_iar_frexpf_bits, . - open_cfw_iar_frexpf_bits
#endif

#if OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == -1 || OPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION == 2
    .section .text.open_cfw_iar_ldexpf, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_ldexpf
    .type open_cfw_iar_ldexpf, %function
    .thumb_func
open_cfw_iar_ldexpf:
    movs    r1, r0
    vmov    r0, s0
    ubfx    r2, r0, #23, #8
    bmi     .Lldexp_negative
    cbz     r2, .Lldexp_positive_subnormal
    cmp     r2, #255
    beq     .Lldexp_return
.Lldexp_add_exponent:
    adds    r2, r2, r1
    cmp     r2, #255
    bhs     .Lldexp_overflow
    add     r1, r0, r1, lsl #23
    vmov    s0, r1
    bx      lr

.Lldexp_negative:
    rsbs    r1, r1, #0
    cbz     r2, .Lldexp_negative_subnormal
    cmp     r2, #255
    beq     .Lldexp_return
    cmp     r1, r2
    bhs     .Lldexp_make_subnormal
    sub     r1, r0, r1, lsl #23
    vmov    s0, r1
    bx      lr

.Lldexp_make_subnormal:
    subs    r2, r2, #1
    subs    r1, r1, r2
    sub     r0, r0, r2, lsl #23
    vmov    s0, r0
.Lldexp_scale_subnormal:
    cmp     r1, #25
    bhi     .Lldexp_signed_zero
    rsb     r1, r1, #127
    lsls    r1, r1, #23
    vmov    s1, r1
    vmrs    r1, fpscr
    bic     r0, r1, #0x1f
    bic     r0, r0, #0x1f00
    vmsr    fpscr, r0
    vmul.f32 s0, s0, s1
    vmrs    r0, fpscr
    vmsr    fpscr, r1
    lsrs    r0, r0, #4
    bhs     .Lldexp_range
    bx      lr

.Lldexp_negative_subnormal:
    cmn     r0, r0
    bne     .Lldexp_scale_subnormal
    bx      lr
.Lldexp_signed_zero:
    and     r0, r0, #0x80000000
    vmov    s0, r0
.Lldexp_return:
    bx      lr

.Lldexp_positive_subnormal:
    cmn     r0, r0
    beq     .Lldexp_return
    cmp     r1, #127
    bhi     .Lldexp_large_positive
    adds    r1, r1, #127
    lsls    r1, r1, #23
    vmov    s1, r1
    vmul.f32 s0, s0, s1
    bx      lr
.Lldexp_large_positive:
    mov     r0, #0x7f000000
    vmov    s1, r0
    vmul.f32 s0, s0, s1
    subs    r1, r1, #127
    vmov    r0, s0
    ubfx    r2, r0, #23, #8
    b       .Lldexp_add_exponent

.Lldexp_overflow:
    lsrs    r1, r0, #23
    orr     r1, r1, #255
    lsls    r1, r1, #23
    vmov    s0, r1
.Lldexp_range:
    b.w     open_cfw_iar_range_error
    bx      lr
    .size open_cfw_iar_ldexpf, . - open_cfw_iar_ldexpf
#endif
