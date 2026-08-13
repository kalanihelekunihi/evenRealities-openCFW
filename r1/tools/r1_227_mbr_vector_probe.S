/*
 * Non-destructive R1 2.2.7.0005 MBR reachability probe.
 *
 * Application-context ACE invokes SD_MBR_COMMAND_VECTOR_TABLE_BASE_SET with
 * address 0x00100000, exactly outside the nRF52840's 1 MiB flash. The S140
 * 7.2.0 MBR must reject it with NRF_ERROR_INVALID_ADDR (0x10) before writing
 * its parameter page or resetting. A matching result requests normal Secure
 * DFU through GPREGRET; any other return resets to the installed application.
 *
 * This payload does not pass a valid vector address and contains no NVMC,
 * UICR, settings, application, or bootloader write.
 */

    .syntax unified
    .thumb
    .section .text.r1_mbr_vector_invalid_probe, "ax", %progbits
    .global r1_mbr_vector_invalid_probe
    .type r1_mbr_vector_invalid_probe, %function
    .thumb_func
r1_mbr_vector_invalid_probe:
    sub     sp, #8
    movs    r0, #4              /* SD_MBR_COMMAND_VECTOR_TABLE_BASE_SET */
    str     r0, [sp]
    ldr     r0, =0x00100000     /* first address outside 1 MiB flash */
    str     r0, [sp, #4]
    mov     r0, sp
    svc     #0x18               /* SD_MBR_COMMAND */
    cmp     r0, #0x10           /* NRF_ERROR_INVALID_ADDR */
    bne     1f
    movs    r0, #0xb1           /* expected rejection: enter DFU */
    b       2f
1:
    movs    r0, #0              /* unexpected result: boot application */
2:
    add     sp, #8
    ldr     r1, =0x4000051c     /* NRF_POWER->GPREGRET */
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c     /* SCB->AIRCR */
    ldr     r0, =0x05fa0004     /* VECTKEY | SYSRESETREQ */
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_mbr_vector_invalid_probe, .-r1_mbr_vector_invalid_probe
