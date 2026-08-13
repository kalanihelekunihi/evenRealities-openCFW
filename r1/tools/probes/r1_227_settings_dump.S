/*
 * Read-only DFU settings extraction payload for owned R1 2.2.7.0005 hardware.
 *
 * Streams the backup settings page at 0x000fe000 and primary settings page at
 * 0x000ff000 as consecutive 244-byte EUS notifications. The receiver retains
 * exactly 0x2000 bytes and discards the tail of the final notification. This
 * performs no flash, NVMC, UICR, settings, or bootloader write.
 */

    .syntax unified
    .thumb

#ifndef SETTINGS_START
    .equ SETTINGS_START,        0x000fe000
#endif
#ifndef SETTINGS_END
    .equ SETTINGS_END,          0x00100000
#endif
    .equ CHUNK_SIZE,            244
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_settings_dump, "ax", %progbits
    .global r1_settings_dump
    .type r1_settings_dump, %function
    .thumb_func
r1_settings_dump:
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp]
    ldr     r4, =SETTINGS_START
    add.w   r5, r4, #(SETTINGS_END - SETTINGS_START)
    ldr     r6, =BAE8_HVX_THUMB
    ldr     r7, =BAE8_SERVICE

1:
    movs    r0, #CHUNK_SIZE
    str     r0, [sp, #4]
    mov     r0, r7
    mov     r1, r4
    add     r2, sp, #4
    movs    r3, #1
    blx     r6
    cmp     r0, #0
    beq     2f
    cmp     r0, #19
    beq     1b
    b       4f

2:
    add.w   r4, r4, #CHUNK_SIZE
    cmp     r4, r5
    blo     1b

    mov.w   r0, #0x02000000
3:
    subs    r0, #1
    bne     3b

4:
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
5:
    b       5b
    .ltorg
    .size r1_settings_dump, .-r1_settings_dump
