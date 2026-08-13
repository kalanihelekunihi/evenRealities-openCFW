/*
 * Read-only single-value probes for R1 2.2.7.0005.
 *
 * Each function requests Secure DFU only when its comparison matches; a
 * mismatch resets to the installed application. Neither function writes
 * flash, NVMC, UICR, settings, or bootloader data.
 */

    .syntax unified
    .thumb

    .section .text.r1_mbr_erased_probe, "ax", %progbits
    .global r1_mbr_erased_probe
    .type r1_mbr_erased_probe, %function
    .thumb_func
r1_mbr_erased_probe:
    ldr     r0, =0x00000ff8
    ldr     r1, [r0]
    ldr     r2, =0xffffffff
    cmp     r1, r2
    bne     1f
    movs    r0, #0xb1
    b       2f
1:
    movs    r0, #0
2:
    ldr     r1, =0x4000051c
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c
    ldr     r0, =0x05fa0004
    str     r0, [r1]
3:
    b       3b
    .ltorg
    .size r1_mbr_erased_probe, .-r1_mbr_erased_probe

    .section .text.r1_mbr_f8000_probe, "ax", %progbits
    .global r1_mbr_f8000_probe
    .type r1_mbr_f8000_probe, %function
    .thumb_func
r1_mbr_f8000_probe:
    ldr     r0, =0x00000ff8
    ldr     r1, [r0]
    ldr     r2, =0x000f8000
    cmp     r1, r2
    bne     7f
    movs    r0, #0xb1
    b       8f
7:
    movs    r0, #0
8:
    ldr     r1, =0x4000051c
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c
    ldr     r0, =0x05fa0004
    str     r0, [r1]
9:
    b       9b
    .ltorg
    .size r1_mbr_f8000_probe, .-r1_mbr_f8000_probe

    .section .text.r1_uicr_f8000_probe, "ax", %progbits
    .global r1_uicr_f8000_probe
    .type r1_uicr_f8000_probe, %function
    .thumb_func
r1_uicr_f8000_probe:
    ldr     r0, =0x10001014
    ldr     r1, [r0]
    ldr     r2, =0x000f8000
    cmp     r1, r2
    bne     4f
    movs    r0, #0xb1
    b       5f
4:
    movs    r0, #0
5:
    ldr     r1, =0x4000051c
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =0xe000ed0c
    ldr     r0, =0x05fa0004
    str     r0, [r1]
6:
    b       6b
    .ltorg
    .size r1_uicr_f8000_probe, .-r1_uicr_f8000_probe
