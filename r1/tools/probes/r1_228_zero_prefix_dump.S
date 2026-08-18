/*
 * Read-only R1 2.2.8.0002 flash-zero prefix transport.
 *
 * The BAE8 HVX wrapper treats address zero as a null data pointer. Copy the
 * first 244 flash bytes to volatile upper SRAM, notify them on connection
 * handle zero, then perform the same ordinary software reset as the other ACE
 * readback probes. No NVMC, UICR, settings, or peripheral configuration write
 * occurs.
 */

    .syntax unified
    .thumb

    .equ COPY_BUFFER,       0x2003C100
    .equ BAE8_HVX_THUMB,    0x00052B6D
    .equ BAE8_CONTEXT,      0x20006514
    .equ SYSTEM_RESET,      0x00038191

    .section .text.r1_228_zero_prefix_dump, "ax", %progbits
    .global r1_228_zero_prefix_dump
    .type r1_228_zero_prefix_dump, %function
    .thumb_func
r1_228_zero_prefix_dump:
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp, #0]
    movs    r0, #244
    str     r0, [sp, #4]

    movs    r4, #0
    ldr     r5, =COPY_BUFFER
    mov     r6, r5
    movs    r7, #61
1:
    ldr     r0, [r4]
    str     r0, [r6]
    adds    r4, #4
    adds    r6, #4
    subs    r7, #1
    bne     1b

    ldr     r4, =BAE8_HVX_THUMB
    ldr     r6, =BAE8_CONTEXT
    mov     r0, r6
    mov     r1, r5
    add     r2, sp, #4
    movs    r3, #0
    blx     r4

    mov.w   r0, #0x02000000
2:
    subs    r0, #1
    bne     2b

    ldr     r0, =SYSTEM_RESET
    blx     r0
3:
    b       3b

    .size r1_228_zero_prefix_dump, . - r1_228_zero_prefix_dump
