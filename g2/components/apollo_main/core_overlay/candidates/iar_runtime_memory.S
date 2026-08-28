/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Thumb-2 replacements for the void-EABI memory providers in the
 * authenticated G2 2.2.6.10 Apollo-main image.  These are intentionally not
 * exported as ISO C memcpy/memmove: the stock providers advance r0 and their
 * callers do not consume a destination return value.
 *
 * The public memcpy and memmove entries accept arbitrary byte alignment.  A
 * source is byte-aligned before any word load. Equal alignments use 16-byte
 * bursts; differing destination alignments scatter each aligned source word
 * through byte/halfword stores. The aligned entry remains independent because
 * 597 stock calls target the interior IAR entry at 0x00439C04 directly.
 */

    .syntax unified
    .cpu cortex-m55
    .thumb

#ifndef OPEN_CFW_IAR_MEMORY_SELECTION
#define OPEN_CFW_IAR_MEMORY_SELECTION -1
#endif

    .macro OPEN_CFW_FORWARD_COPY prefix
    cmp     r2, #0
    beq     .L\prefix\()_return
.L\prefix\()_align_source:
    tst     r1, #3
    beq     .L\prefix\()_classify_destination
    ldrb    r3, [r1], #1
    strb    r3, [r0], #1
    subs    r2, r2, #1
    beq     .L\prefix\()_return
    b       .L\prefix\()_align_source
.L\prefix\()_classify_destination:
    tst     r0, #3
    beq     .L\prefix\()_words
    tst     r0, #1
    bne     .L\prefix\()_scatter_odd

    /* Aligned word load to halfword-aligned destination. */
    subs    r2, r2, #4
    blo     .L\prefix\()_restore_scatter_half_count
.L\prefix\()_scatter_half:
    ldr     r3, [r1], #4
    strh    r3, [r0], #2
    lsrs    r3, r3, #16
    subs    r2, r2, #4
    strh    r3, [r0], #2
    bhs     .L\prefix\()_scatter_half
.L\prefix\()_restore_scatter_half_count:
    adds    r2, r2, #4
    b       .L\prefix\()_byte_check

    /* Aligned word load to odd destination. */
.L\prefix\()_scatter_odd:
    subs    r2, r2, #4
    blo     .L\prefix\()_restore_scatter_odd_count
.L\prefix\()_scatter_odd_loop:
    ldr     r3, [r1], #4
    strb    r3, [r0], #1
    lsrs    r3, r3, #8
    strh    r3, [r0], #2
    lsrs    r3, r3, #16
    subs    r2, r2, #4
    strb    r3, [r0], #1
    bhs     .L\prefix\()_scatter_odd_loop
.L\prefix\()_restore_scatter_odd_count:
    adds    r2, r2, #4
    b       .L\prefix\()_byte_check

.L\prefix\()_words:
    subs    r2, r2, #16
    blo     .L\prefix\()_restore_burst_count
    push    {r4, r5}
.L\prefix\()_burst:
    ldmia   r1!, {r3-r5, r12}
    subs    r2, r2, #16
    stmia   r0!, {r3-r5, r12}
    bhs     .L\prefix\()_burst
    pop     {r4, r5}
.L\prefix\()_restore_burst_count:
    adds    r2, r2, #16
    cmp     r2, #4
    blo     .L\prefix\()_byte_check
.L\prefix\()_word_tail:
    ldr     r3, [r1], #4
    str     r3, [r0], #4
    subs    r2, r2, #4
    cmp     r2, #4
    bhs     .L\prefix\()_word_tail
.L\prefix\()_byte_check:
    cmp     r2, #0
    beq     .L\prefix\()_return
.L\prefix\()_bytes:
    ldrb    r3, [r1], #1
    strb    r3, [r0], #1
    subs    r2, r2, #1
    bne     .L\prefix\()_bytes
.L\prefix\()_return:
    bx      lr
    .endm

#if OPEN_CFW_IAR_MEMORY_SELECTION == -1 || OPEN_CFW_IAR_MEMORY_SELECTION == 0
    .section .text.open_cfw_iar_memcpy_void, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_memcpy_void
    .type open_cfw_iar_memcpy_void, %function
    .thumb_func
open_cfw_iar_memcpy_void:
    OPEN_CFW_FORWARD_COPY memcpy
    .size open_cfw_iar_memcpy_void, . - open_cfw_iar_memcpy_void
#endif

#if OPEN_CFW_IAR_MEMORY_SELECTION == -1 || OPEN_CFW_IAR_MEMORY_SELECTION == 1
    .section .text.open_cfw_iar_memcpy_aligned_void, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_memcpy_aligned_void
    .type open_cfw_iar_memcpy_aligned_void, %function
    .thumb_func
open_cfw_iar_memcpy_aligned_void:
    /* Retain byte-safe behavior even if a future caller violates alignment. */
    OPEN_CFW_FORWARD_COPY memcpy_aligned
    .size open_cfw_iar_memcpy_aligned_void, . - open_cfw_iar_memcpy_aligned_void
#endif

#if OPEN_CFW_IAR_MEMORY_SELECTION == -1 || OPEN_CFW_IAR_MEMORY_SELECTION == 2
    .section .text.open_cfw_iar_memmove_void, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_memmove_void
    .type open_cfw_iar_memmove_void, %function
    .thumb_func
open_cfw_iar_memmove_void:
    cmp     r2, #0
    beq     .Lmemmove_return
    cmp     r0, r1
    bls     .Lmemmove_forward
    sub     r3, r0, r1
    cmp     r3, r2
    bhs     .Lmemmove_forward

    /* source < destination < source + count: copy backward. */
    add     r0, r0, r2
    add     r1, r1, r2
.Lmemmove_backward_align_source:
    tst     r1, #3
    beq     .Lmemmove_backward_classify_destination
    ldrb    r3, [r1, #-1]!
    strb    r3, [r0, #-1]!
    subs    r2, r2, #1
    beq     .Lmemmove_return
    b       .Lmemmove_backward_align_source
.Lmemmove_backward_classify_destination:
    tst     r0, #3
    beq     .Lmemmove_backward_words
    tst     r0, #1
    bne     .Lmemmove_backward_scatter_odd

    /* Aligned backward word load to halfword-aligned destination. */
    subs    r2, r2, #4
    blo     .Lmemmove_restore_scatter_half_count
.Lmemmove_backward_scatter_half:
    ldr     r3, [r1, #-4]!
    strh    r3, [r0, #-4]!
    lsrs    r3, r3, #16
    subs    r2, r2, #4
    strh    r3, [r0, #2]
    bhs     .Lmemmove_backward_scatter_half
.Lmemmove_restore_scatter_half_count:
    adds    r2, r2, #4
    b       .Lmemmove_backward_byte_check

    /* Aligned backward word load to odd destination. */
.Lmemmove_backward_scatter_odd:
    subs    r2, r2, #4
    blo     .Lmemmove_restore_scatter_odd_count
.Lmemmove_backward_scatter_odd_loop:
    ldr     r3, [r1, #-4]!
    strb    r3, [r0, #-4]!
    lsrs    r3, r3, #8
    strh    r3, [r0, #1]
    lsrs    r3, r3, #16
    subs    r2, r2, #4
    strb    r3, [r0, #3]
    bhs     .Lmemmove_backward_scatter_odd_loop
.Lmemmove_restore_scatter_odd_count:
    adds    r2, r2, #4
    b       .Lmemmove_backward_byte_check

.Lmemmove_backward_words:
    subs    r2, r2, #16
    blo     .Lmemmove_restore_burst_count
    push    {r4, r5}
.Lmemmove_backward_burst:
    ldmdb   r1!, {r3-r5, r12}
    subs    r2, r2, #16
    stmdb   r0!, {r3-r5, r12}
    bhs     .Lmemmove_backward_burst
    pop     {r4, r5}
.Lmemmove_restore_burst_count:
    adds    r2, r2, #16
    cmp     r2, #4
    blo     .Lmemmove_backward_byte_check
.Lmemmove_backward_word_tail:
    ldr     r3, [r1, #-4]!
    str     r3, [r0, #-4]!
    subs    r2, r2, #4
    cmp     r2, #4
    bhs     .Lmemmove_backward_word_tail
.Lmemmove_backward_byte_check:
    cmp     r2, #0
    beq     .Lmemmove_return
.Lmemmove_backward_bytes:
    ldrb    r3, [r1, #-1]!
    strb    r3, [r0, #-1]!
    subs    r2, r2, #1
    bne     .Lmemmove_backward_bytes
    b       .Lmemmove_return

.Lmemmove_forward:
    OPEN_CFW_FORWARD_COPY memmove_forward
.Lmemmove_return:
    bx      lr
    .size open_cfw_iar_memmove_void, . - open_cfw_iar_memmove_void
#endif

    .section .note.GNU-stack, "", %progbits
