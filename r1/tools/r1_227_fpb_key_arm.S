/*
 * Arm Cortex-M4 literal comparator 6 for the live bootloader key pointer.
 *
 * A stage canary is required before FPB is enabled. Success enters genuine
 * Secure DFU; failure performs an ordinary application reset. The replacement
 * key and remap table are volatile retained SRAM only.
 */

    .syntax unified
    .thumb

    /* Seven words supplied in unused command bytes at record offset 0x04:
     * remap base, canary, FPB base, COMP6 value, GPREGRET, AIRCR, reset value. */
    .equ RECORD_CONSTANTS,       0x2001a190

    .section .text.r1_fpb_key_arm, "ax", %progbits
    .global r1_fpb_key_arm
    .type r1_fpb_key_arm, %function
    .thumb_func
r1_fpb_key_arm:
    ldr     r5, =RECORD_CONSTANTS
    ldmia   r5!, {r0-r4}
    ldr     r6, [r0, #0x80]
    cmp     r6, r1
    bne     1f

    add.w   r6, r0, #0x40
    str     r6, [r0, #0x18]
    movs    r6, #2
    str     r6, [r2]
    str     r0, [r2, #4]
    str     r3, [r2, #0x20]
    movs    r6, #3
    str     r6, [r2]
    dsb
    isb
    movs    r6, #0xb1
    b       2f

1:
    movs    r6, #0
2:
    strb    r6, [r4]
    ldmia   r5!, {r6-r7}
    dsb
    str     r7, [r6]
3:
    b       3b
    .ltorg
    .size r1_fpb_key_arm, .-r1_fpb_key_arm
