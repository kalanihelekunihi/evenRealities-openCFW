/* Disable FPB key substitution and clear all retained key material from SRAM. */

    .syntax unified
    .thumb

    .equ FPB_BASE,               0xe0002000
    .equ FPB_CTRL_KEY,           0x00000002
    .equ FPB_REMAP_TABLE,        0x2003c000
    .equ RETAINED_KEY,           0x2003c040
    .equ POWER_GPREGRET,         0x4000051c
    .equ SCB_AIRCR,              0xe000ed0c
    .equ AIRCR_SYSRESETREQ,      0x05fa0004

    .section .text.r1_fpb_key_cleanup, "ax", %progbits
    .global r1_fpb_key_cleanup
    .type r1_fpb_key_cleanup, %function
    .thumb_func
r1_fpb_key_cleanup:
    ldr     r4, =FPB_BASE
    movs    r1, #FPB_CTRL_KEY
    str     r1, [r4]
    movs    r0, #0
    str     r0, [r4, #0x20]

    ldr     r1, =FPB_REMAP_TABLE
    movs    r2, #0x21            /* eight table words + 64-byte key + canary */
1:
    str     r0, [r1], #4
    subs    r2, #1
    bne     1b

    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
2:
    b       2b
    .ltorg
    .size r1_fpb_key_cleanup, .-r1_fpb_key_cleanup
