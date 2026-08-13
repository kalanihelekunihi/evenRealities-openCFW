/*
 * Non-persistent R1 2.2.7.0005 code-execution proof.
 *
 * This payload writes Nordic's BOOTLOADER_DFU_START marker to POWER.GPREGRET
 * and requests a system reset. It performs no flash or UICR writes.
 */

    .syntax unified
    .thumb
    .section .text.r1_dfu_proof, "ax", %progbits
    .global r1_dfu_proof
    .type r1_dfu_proof, %function
    .thumb_func
r1_dfu_proof:
    ldr     r1, =0x4000051c      /* NRF_POWER->GPREGRET */
    movs    r0, #0xb1            /* BOOTLOADER_DFU_START */
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c      /* SCB->AIRCR */
    ldr     r0, =0x05fa0004      /* VECTKEY | SYSRESETREQ */
    str     r0, [r1]
1:
    b       1b
    .ltorg
    .size r1_dfu_proof, .-r1_dfu_proof
