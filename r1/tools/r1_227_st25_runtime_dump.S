/*
 * Read-only ST25DV mailbox-state payload for owned R1 2.2.7.0005 hardware.
 *
 * It returns the four-byte ST25 initialization state and the first eight bytes
 * of the NFC task object over the established EUS notification path.  The
 * initializer sets byte 3 of the first word to one only after the ST25 init
 * call succeeds; its decompiled success path then enables the mailbox and
 * configures GPO.  This payload performs no function call or ST25, flash,
 * UICR, settings, ACL, or NFC-RF write.
 */

    .syntax unified
    .thumb

    .equ ST25_INIT_STATE,             0x20006870
    .equ NFC_TASK_OBJECT,             0x20016b20
    .equ BAE8_HVX_THUMB,             0x00052969
    .equ BAE8_SERVICE,               0x20006514
    .equ SCB_AIRCR,                  0xe000ed0c
    .equ AIRCR_SYSRESETREQ,          0x05fa0004

    .section .text.r1_st25_runtime_dump, "ax", %progbits
    .global r1_st25_runtime_dump
    .type r1_st25_runtime_dump, %function
    .thumb_func
r1_st25_runtime_dump:
    sub     sp, #24
    movs    r0, #1
    str     r0, [sp]
    movs    r0, #12
    str     r0, [sp, #4]

    ldr     r4, =ST25_INIT_STATE
    ldr     r0, [r4]
    str     r0, [sp, #8]
    ldr     r4, =NFC_TASK_OBJECT
    ldrd    r0, r1, [r4]
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
    .size r1_st25_runtime_dump, .-r1_st25_runtime_dump
