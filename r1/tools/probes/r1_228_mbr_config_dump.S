/*
 * Read-only R1 2.2.8.0002 MBR configuration-word transport.
 *
 * Retail bootloader initialization may program MBR_BOOTLOADER_ADDR at 0xFF8
 * and MBR_PARAM_PAGE_ADDR at 0xFFC after the official S140 image is installed.
 * Copy those eight live bytes to volatile upper SRAM before notifying them so
 * a mixed-provenance recovery image can patch the two device-specific words.
 * No NVMC, UICR, settings, or peripheral configuration write occurs.
 */

    .syntax unified
    .thumb

    .equ MBR_CONFIG,        0x00000FF8
    .equ COPY_BUFFER,       0x2003C100
    .equ BAE8_HVX_THUMB,    0x00052B6D
    .equ BAE8_CONTEXT,      0x20006514
    .equ SYSTEM_RESET,      0x00038191

    .section .text.r1_228_mbr_config_dump, "ax", %progbits
    .global r1_228_mbr_config_dump
    .type r1_228_mbr_config_dump, %function
    .thumb_func
r1_228_mbr_config_dump:
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp, #0]
    movs    r0, #8
    str     r0, [sp, #4]

    ldr     r4, =MBR_CONFIG
    ldr     r5, =COPY_BUFFER
    ldmia   r4!, {r0, r1}
    stmia   r5!, {r0, r1}
    subs    r5, #8

    ldr     r4, =BAE8_HVX_THUMB
    ldr     r6, =BAE8_CONTEXT
    mov     r0, r6
    mov     r1, r5
    add     r2, sp, #4
    movs    r3, #0
    blx     r4

    mov.w   r0, #0x02000000
1:
    subs    r0, #1
    bne     1b

    ldr     r0, =SYSTEM_RESET
    blx     r0
2:
    b       2b

    .size r1_228_mbr_config_dump, . - r1_228_mbr_config_dump
