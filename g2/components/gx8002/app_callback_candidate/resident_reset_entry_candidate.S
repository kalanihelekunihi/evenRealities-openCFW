/* SPDX-License-Identifier: MIT
 * Native image-A SRAM reset entry 0x10023500. Stack top and CPU control
 * register sequence are architectural startup contracts, not C call ABI.
 * The system initializer and main are genuine external source requirements.
 */
    .text
    .align 2
    .global gx8002_resident_reset_entry_23500
    .type gx8002_resident_reset_entry_23500, %function
gx8002_resident_reset_entry_23500:
    lrw r0, 0x80000200
    mtcr r0, cr<0, 0>
    mfcr r1, cr<31, 0>
    bclri r1, 3
    mtcr r1, cr<31, 0>
    lrw r14, 0x2002f7fc
    bsr gx8002_resident_system_initialize_2354c
    bsr gx8002_resident_main_26314
1:  br 1b
    .size gx8002_resident_reset_entry_23500, .-gx8002_resident_reset_entry_23500

    /* Stock 0x10023640 is a branch into the exception entry at 0x100235fc. */
    .global gx8002_resident_exception_bridge_23640
    .type gx8002_resident_exception_bridge_23640, %function
gx8002_resident_exception_bridge_23640:
    br gx8002_resident_trap_235fc
    .size gx8002_resident_exception_bridge_23640, .-gx8002_resident_exception_bridge_23640
