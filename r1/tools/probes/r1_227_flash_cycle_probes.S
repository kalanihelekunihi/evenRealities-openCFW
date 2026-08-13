/*
 * Bounded flash-write and cleanup probes for owned R1 2.2.7.0005 hardware.
 *
 * The write probe refuses to touch 0x000c6000 unless its first word is erased,
 * disables the SoftDevice, writes one marker word, verifies it, and resets.
 * The erase probe is intended to run only after that positive result; it erases
 * the same page, verifies the first word returned to 0xffffffff, and resets.
 * Success enters signed DFU using GPREGRET 0xb1; failure boots the application.
 * Neither function addresses UICR, bootloader/settings flash, or active app flash.
 */

    .syntax unified
    .thumb

    .equ TEST_PAGE,             0x000c6000
    .equ TEST_MARKER,           0x31535752  /* little-endian "RWS1" */
    .equ NVMC_CONFIG_THUMB,     0x0007d2a1
    .equ NVMC_ERASEPAGE,        0x4001e508
    .equ POWER_GPREGRET,        0x4000051c
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_flash_write_probe, "ax", %progbits
    .global r1_flash_write_probe
    .type r1_flash_write_probe, %function
    .thumb_func
r1_flash_write_probe:
    ldr     r4, =TEST_PAGE
    ldr     r0, [r4]
    ldr     r1, =0xffffffff
    cmp     r0, r1
    bne     1f                  /* fail closed if the page is not erased */

    svc     #0x11               /* sd_softdevice_disable */
    ldr     r5, =NVMC_CONFIG_THUMB
    movs    r0, #1              /* NVMC WEN */
    blx     r5
    ldr     r6, =TEST_MARKER
    str     r6, [r4]
    ldr     r0, [r4]
    cmp     r0, r6
    bne     1f
    movs    r0, #0xb1
    b       2f
1:
    movs    r0, #0
2:
    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_flash_write_probe, .-r1_flash_write_probe

    .section .text.r1_flash_erase_probe, "ax", %progbits
    .global r1_flash_erase_probe
    .type r1_flash_erase_probe, %function
    .thumb_func
r1_flash_erase_probe:
    ldr     r4, =TEST_PAGE
    svc     #0x11               /* sd_softdevice_disable */
    ldr     r5, =NVMC_CONFIG_THUMB
    movs    r0, #2              /* NVMC EEN */
    blx     r5
    ldr     r1, =NVMC_ERASEPAGE
    str     r4, [r1]
    movs    r0, #0              /* fetching helper stalls until erase completes */
    blx     r5                  /* restore NVMC REN and poll READY */
    ldr     r0, [r4]
    ldr     r1, =0xffffffff
    cmp     r0, r1
    bne     4f
    movs    r0, #0xb1
    b       5f
4:
    movs    r0, #0
5:
    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
6:
    b       6b
    .ltorg
    .size r1_flash_erase_probe, .-r1_flash_erase_probe
