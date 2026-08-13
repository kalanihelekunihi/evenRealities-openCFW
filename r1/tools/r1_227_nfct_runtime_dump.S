/*
 * Read-only NFCT runtime-state payload for owned R1 2.2.7.0005 hardware.
 * It reports whether the linked Nordic NFCT driver is actually enabled at
 * runtime.  It returns INTENSET, PACKETPTR, and MAXLEN; a zero interrupt mask
 * and unconfigured DMA pair establish that the peripheral is not an active
 * receive path.  No NFCT task, interrupt, configuration, flash, or UICR
 * register is written.
 */

    .syntax unified
    .thumb

    .equ NFCT_BASE,              0x40005000
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_nfct_runtime_dump, "ax", %progbits
    .global r1_nfct_runtime_dump
    .type r1_nfct_runtime_dump, %function
    .thumb_func
r1_nfct_runtime_dump:
    sub     sp, #24
    movs    r0, #1
    str     r0, [sp]
    movs    r0, #12
    str     r0, [sp, #4]

    ldr     r4, =NFCT_BASE
    ldr.w   r0, [r4, #0x304]
    str     r0, [sp, #8]
    add.w   r4, r4, #0x500
    ldrd    r0, r1, [r4, #0x10]
    strd    r0, r1, [sp, #12]

    ldr     r6, =BAE8_HVX_THUMB
1:
    ldr     r0, =BAE8_SERVICE
    add     r1, sp, #8
    add     r2, sp, #4
    movs    r3, #1
    blx     r6
    cmp     r0, #19
    beq     1b

    mov.w   r0, #0x02000000
2:
    subs    r0, #1
    bne     2b

    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_nfct_runtime_dump, .-r1_nfct_runtime_dump
