/* Read-only erased-word probes for candidate pages outside the active image. */

    .syntax unified
    .thumb

    .macro erased_probe name, address
    .section .text.\name, "ax", %progbits
    .global \name
    .type \name, %function
    .thumb_func
\name:
    ldr     r0, =\address
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
    .size \name, .-\name
    .endm

    erased_probe r1_c6000_erased_probe, 0x000c6000
    erased_probe r1_d3000_erased_probe, 0x000d3000
