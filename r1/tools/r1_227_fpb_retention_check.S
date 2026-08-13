/*
 * Volatile FPB-retention predicate and cleanup for owned R1 2.2.7.0005.
 *
 * After r1_fpb_retention_arm has soft-reset through the MBR/bootloader and the
 * stock application is running again, this payload checks FP_CTRL.ENABLE,
 * FP_REMAP, FP_COMP0, and the SRAM canary.  An exact match requests stock DFU
 * through GPREGRET=0xB1; a mismatch requests an ordinary application reset.
 * Before either reset it disables FPB globally, disables comparator 0, and
 * clears the canary.
 *
 * No flash, NVMC, UICR, settings, ACL, or bootloader word is written.
 */

    .syntax unified
    .thumb

    .equ FPB_BASE,               0xe0002000
    .equ FPB_CTRL_KEY,           0x00000002
    /* Above the application's initial MSP (0x2003bed0), so neither the
     * bootloader nor the application's scatter loader clears the probe. */
    .equ FPB_REMAP_TABLE,        0x2003c000
    .equ FPB_UNREACHABLE_COMP0,  0x00100001
    .equ FPB_CANARY_WORD,        0x46504252
    .equ POWER_GPREGRET,         0x4000051c
    .equ SCB_AIRCR,              0xe000ed0c
    .equ AIRCR_SYSRESETREQ,      0x05fa0004

    .section .text.r1_fpb_retention_check, "ax", %progbits
    .global r1_fpb_retention_check
    .type r1_fpb_retention_check, %function
    .thumb_func
r1_fpb_retention_check:
    ldr     r4, =FPB_BASE
    movs    r0, #0
    ldr     r1, [r4]
    lsls    r1, r1, #31
    bpl     1f
    ldr     r1, [r4, #4]
    ldr     r2, =FPB_REMAP_TABLE
    cmp     r1, r2
    bne     1f
    ldr     r1, [r4, #8]
    lsls    r1, r1, #31
    bpl     1f
    ldr     r1, [r2]
    ldr     r3, =FPB_CANARY_WORD
    cmp     r1, r3
    bne     1f
    movs    r0, #0xb1

1:
    movs    r1, #FPB_CTRL_KEY
    str     r1, [r4]
    movs    r1, #0
    str     r1, [r4, #8]

    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
2:
    b       2b
    .ltorg
    .size r1_fpb_retention_check, .-r1_fpb_retention_check
