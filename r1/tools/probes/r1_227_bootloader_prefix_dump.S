/*
 * Read-only, single-notification bootloader prefix probe for owned R1
 * 2.2.7.0005 hardware.
 *
 * This is deliberately bounded to the first 244 bytes at 0x000f8000.  It
 * exercises the same BAE8 EUS notification route as the full extractor but
 * cannot fill the SoftDevice HVN queue.  It performs no flash, NVMC, UICR,
 * settings, ACL, or bootloader write.
 */

    .syntax unified
    .thumb

    /* Patched by the guarded generator within 0xF8000...0xFDF0C. */
    .equ BOOTLOADER_START,      0xdeadbeef
    .equ CHUNK_SIZE,            244
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_bootloader_prefix_dump, "ax", %progbits
    .global r1_bootloader_prefix_dump
    .type r1_bootloader_prefix_dump, %function
    .thumb_func
r1_bootloader_prefix_dump:
    /* Fifth HVX-wrapper argument: nonzero selects the EUS ...13 lane. */
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp]
    movs    r0, #CHUNK_SIZE
    str     r0, [sp, #4]
    ldr     r4, =BAE8_HVX_THUMB
    ldr     r5, =BAE8_SERVICE
    ldr     r6, =BOOTLOADER_START
    movs    r7, #0       /* phone is normally the first live connection */
1:
    mov     r0, r5
    mov     r1, r6
    add     r2, sp, #4
    mov     r3, r7
    blx     r4
    cmp     r0, #0
    beq     2f
    cmp     r7, #0
    bne     4f
    movs    r7, #1       /* fallback when another peripheral owns handle 0 */
    b       1b

2:
    /* Leave ample time for the sole notification to reach CoreBluetooth. */
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
    .size r1_bootloader_prefix_dump, .-r1_bootloader_prefix_dump
