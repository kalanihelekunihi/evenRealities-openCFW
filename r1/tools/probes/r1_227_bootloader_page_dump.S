/*
 * Read-only one-page bootloader extraction payload for owned R1 2.2.7.0005.
 *
 * The guarded host patches BOOTLOADER_START to one aligned page in
 * 0x000f8000...0x000fd000.  The payload streams exactly 0x1000 bytes using
 * 244-byte EUS notifications; the receiver truncates the final notification.
 * It performs no flash, NVMC, UICR, settings, ACL, or bootloader write.
 */

    .syntax unified
    .thumb

    .equ BOOTLOADER_START,      0xdeadbeef
    .equ PAGE_SIZE,             0x1000
    .equ CHUNK_SIZE,            244
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SYSTEM_RESET_THUMB,    0x00038191

    .section .text.r1_bootloader_page_dump, "ax", %progbits
    .global r1_bootloader_page_dump
    .type r1_bootloader_page_dump, %function
    .thumb_func
r1_bootloader_page_dump:
    sub     sp, #8
    movs    r0, #1
    str     r0, [sp]     /* fifth argument: EUS ...13 lane */
    ldr     r4, =BOOTLOADER_START
    add.w   r5, r4, #PAGE_SIZE
    ldr     r6, =BAE8_HVX_THUMB
    ldr     r7, =BAE8_SERVICE

1:
    movs    r0, #CHUNK_SIZE
    str     r0, [sp, #4]
    mov     r0, r7
    mov     r1, r4
    add     r2, sp, #4
    movs    r3, #1
    ands    r3, r5       /* end-address bit 0 retains selected handle */
    blx     r6
    cmp     r0, #0
    beq     2f
    cmp     r0, #19      /* queue full: retry while SoftDevice drains HVNs */
    beq     1b
    lsls    r3, r5, #31
    bmi     4f           /* handle 1 also rejected */
    adds    r5, #1       /* retry this chunk on handle 1 */
    b       1b

2:
    add.w   r4, r4, #CHUNK_SIZE
    cmp     r4, r5
    blo     1b

    mov.w   r0, #0x02000000
3:
    subs    r0, #1
    bne     3b

4:
    ldr     r0, =SYSTEM_RESET_THUMB
    blx     r0           /* verified 2.2.7.0005 __NVIC_SystemReset; no return */
    .ltorg
    .size r1_bootloader_page_dump, .-r1_bootloader_page_dump
