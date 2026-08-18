/*
 * Read-only final-page transport for R1 2.2.8.0002.
 *
 * Sixteen 244-byte notifications cover 3904 bytes and one final 192-byte
 * notification stops exactly at the nRF52840 one-MiB flash boundary. The
 * ordinary page probe intentionally truncates a 244-byte final chunk, which
 * would fault here because its last 52 bytes are outside mapped flash.
 * No NVMC, UICR, settings, or peripheral configuration write occurs.
 */

    .syntax unified
    .thumb

    .equ PAGE_START,        0x000FF000
    .equ FLASH_END,         0x00100000
    .equ CHUNK_SIZE,        244
    .equ BAE8_HVX_THUMB,    0x00052B6D
    .equ BAE8_CONTEXT,      0x20006514
    .equ SYSTEM_RESET,      0x00038191

    .section .text.r1_228_last_flash_page_dump, "ax", %progbits
    .global r1_228_last_flash_page_dump
    .type r1_228_last_flash_page_dump, %function
    .thumb_func
r1_228_last_flash_page_dump:
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp, #0]
    ldr     r4, =PAGE_START
    ldr     r5, =FLASH_END
    ldr     r6, =BAE8_HVX_THUMB
    ldr     r7, =BAE8_CONTEXT

1:
    subs    r0, r5, r4
    cmp     r0, #CHUNK_SIZE
    bls     2f
    movs    r0, #CHUNK_SIZE
2:
    str     r0, [sp, #4]
    mov     r0, r7
    mov     r1, r4
    add     r2, sp, #4
    movs    r3, #0
    blx     r6
    cmp     r0, #0
    beq     3f
    cmp     r0, #19
    beq     1b
    b       5f

3:
    add.w   r4, r4, #CHUNK_SIZE
    cmp     r4, r5
    blo     1b

    mov.w   r0, #0x02000000
4:
    subs    r0, #1
    bne     4b

5:
    ldr     r0, =SYSTEM_RESET
    blx     r0
6:
    b       6b

    .size r1_228_last_flash_page_dump, . - r1_228_last_flash_page_dump
