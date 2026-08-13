/*
 * Read-only APPROTECT runtime-state payload for owned R1 2.2.7.0005
 * hardware.  It reports the two FICR revision words used by Nordic erratum
 * 249 followed by APPROTECT DISABLE.  No configuration or flash register is
 * written.
 */

    .syntax unified
    .thumb

    .equ FICR_REVISION,          0x10000130
    .equ APPROTECT_FORCE,       0x40000550
    .equ BAE8_HVX_THUMB,        0x00052969
    .equ BAE8_SERVICE,          0x20006514
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_approtect_runtime_dump, "ax", %progbits
    .global r1_approtect_runtime_dump
    .type r1_approtect_runtime_dump, %function
    .thumb_func
r1_approtect_runtime_dump:
    sub     sp, #24
    movs    r0, #1
    str     r0, [sp]
    movs    r0, #12
    str     r0, [sp, #4]

    ldr     r4, =FICR_REVISION
    ldmia   r4!, {r0, r1}
    strd    r0, r1, [sp, #8]
    ldr     r4, =APPROTECT_FORCE
    ldr     r0, [r4, #8]
    str     r0, [sp, #16]

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
    .size r1_approtect_runtime_dump, .-r1_approtect_runtime_dump
