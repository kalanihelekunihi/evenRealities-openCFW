/*
 * Read-only live bootloader extraction payload for owned R1 2.2.7.0005 hardware.
 *
 * The BAE8 HVX wrapper streams consecutive 244-byte values directly from
 * 0x000f8000 upward. This bypasses the higher-level phone/glasses role map but
 * still requires the live link context and the EUS CCCD to be enabled. The receiver concatenates the first
 * 0x6000 bytes and discards the final notification's bytes beyond 0x000fe000.
 * It performs no flash, NVMC, UICR, settings, or bootloader write.
 */

    .syntax unified
    .thumb

    .equ BOOTLOADER_START,      0x000f8000
    .equ BOOTLOADER_END,        0x000fe000
    .equ CHUNK_SIZE,            244
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_bootloader_dump, "ax", %progbits
    .global r1_bootloader_dump
    .type r1_bootloader_dump, %function
    .thumb_func
r1_bootloader_dump:
    /* Fifth HVX-wrapper argument: nonzero selects the EUS ...13 lane. */
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp]
    ldr     r4, =BOOTLOADER_START
    add.w   r5, r4, #(BOOTLOADER_END - BOOTLOADER_START)
    ldr     r6, =BAE8_HVX_THUMB
    ldr     r7, =BAE8_SERVICE

1:
    movs    r0, #CHUNK_SIZE
    str     r0, [sp, #4]
    mov     r0, r7
    mov     r1, r4
    add     r2, sp, #4
    movs    r3, #0       /* isolated phone link; targeted live reads confirmed handle 0 */
    blx     r6
    cmp     r0, #0
    beq     2f
    cmp     r0, #19      /* NRF_ERROR_RESOURCES: retry after HVN completion */
    beq     1b
    b       4f

2:
    add.w   r4, r4, #CHUNK_SIZE
    cmp     r4, r5
    blo     1b

    /* Leave time for the final four queued notifications to reach the phone. */
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
    .size r1_bootloader_dump, .-r1_bootloader_dump
