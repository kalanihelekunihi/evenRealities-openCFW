/*
 * Volatile FPB-retention probe for owned R1 2.2.7.0005 hardware.
 *
 * The comparator deliberately targets 0x00100000, outside the nRF52840 flash
 * address space, so it cannot affect any normal MBR, bootloader, SoftDevice, or
 * application instruction fetch.  The remap word and FPB registers are staged,
 * then an ordinary AIRCR soft reset is requested with GPREGRET cleared.  A
 * separate read-and-cleanup payload records whether Debug and RAM survived the
 * reset as specified by the nRF52840 reset table.
 *
 * No flash, NVMC, UICR, settings, ACL, or bootloader word is written.
 */

    .syntax unified
    .thumb

    .equ FPB_BASE,               0xe0002000
    .equ FPB_CTRL_KEY,           0x00000002
    .equ FPB_CTRL_ENABLE,        0x00000003
    /* Above the application's initial MSP (0x2003bed0), so neither the
     * bootloader nor the application's scatter loader clears the probe. */
    .equ FPB_REMAP_TABLE,        0x2003c000
    .equ FPB_UNREACHABLE_COMP0,  0x00100001
    .equ FPB_CANARY_WORD,        0x46504252
    .equ POWER_GPREGRET,         0x4000051c
    .equ SCB_AIRCR,              0xe000ed0c
    .equ AIRCR_SYSRESETREQ,      0x05fa0004

    .section .text.r1_fpb_retention_arm, "ax", %progbits
    .global r1_fpb_retention_arm
    .type r1_fpb_retention_arm, %function
    .thumb_func
r1_fpb_retention_arm:
    ldr     r0, =FPB_REMAP_TABLE
    ldr     r1, =FPB_CANARY_WORD
    str     r1, [r0]

    ldr     r2, =FPB_BASE
    movs    r1, #FPB_CTRL_KEY
    str     r1, [r2]
    str     r0, [r2, #4]
    ldr     r1, =FPB_UNREACHABLE_COMP0
    str     r1, [r2, #8]
    movs    r1, #FPB_CTRL_ENABLE
    str     r1, [r2]
    dsb
    isb

    ldr     r0, =POWER_GPREGRET
    movs    r1, #0
    strb    r1, [r0]
    dsb

    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
1:
    b       1b
    .ltorg
    .size r1_fpb_retention_arm, .-r1_fpb_retention_arm
