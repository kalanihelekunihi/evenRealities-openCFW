/*
 * Read-only R1 2.2.7.0005 boot-configuration probe.
 *
 * The payload checks that MBR_BOOTLOADER_ADDR at 0x00000ff8 is erased and
 * UICR NRFFW[0] at 0x10001014 contains 0x000f8000. A match requests normal
 * Secure DFU using GPREGRET 0xb1; a mismatch clears GPREGRET. Both paths reset.
 * It performs no flash, NVMC, UICR, settings, or bootloader write.
 */

    .syntax unified
    .thumb
    .section .text.r1_boot_config_probe, "ax", %progbits
    .global r1_boot_config_probe
    .type r1_boot_config_probe, %function
    .thumb_func
r1_boot_config_probe:
    ldr     r0, =0x00000ff8      /* MBR_BOOTLOADER_ADDR */
    ldr     r1, [r0]
    ldr     r2, =0xffffffff
    cmp     r1, r2
    bne     1f

    ldr     r0, =0x10001014      /* UICR->NRFFW[0] */
    ldr     r1, [r0]
    ldr     r2, =0x000f8000
    cmp     r1, r2
    bne     1f

    movs    r0, #0xb1           /* matching configuration: enter DFU */
    b       2f
1:
    movs    r0, #0              /* mismatch: boot the installed application */
2:
    ldr     r1, =0x4000051c      /* NRF_POWER->GPREGRET */
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c      /* SCB->AIRCR */
    ldr     r0, =0x05fa0004      /* VECTKEY | SYSRESETREQ */
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_boot_config_probe, .-r1_boot_config_probe
