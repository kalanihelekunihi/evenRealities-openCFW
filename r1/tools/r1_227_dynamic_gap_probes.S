/*
 * Runtime-addressed read/write/erase probes for the inactive flash gap.
 *
 * The 0xdeadbeef literal is patched by the host only after constraining it to a
 * 4 KiB-aligned page in 0x000c6000...0x000d3000. The first function is read
 * only. The write function refuses non-erased first words. The erase function
 * is the paired cleanup and is used only after a verified marker write.
 */

    .syntax unified
    .thumb
    .equ TARGET_PLACEHOLDER,    0xdeadbeef
    .equ TEST_MARKER,           0x31535752
    .equ NVMC_CONFIG_THUMB,     0x0007d2a1
    .equ NVMC_ERASEPAGE,        0x4001e508
    .equ POWER_GPREGRET,        0x4000051c
    .equ SCB_AIRCR,             0xe000ed0c
    .equ AIRCR_SYSRESETREQ,     0x05fa0004

    .section .text.r1_dynamic_erased_probe, "ax", %progbits
    .global r1_dynamic_erased_probe
    .type r1_dynamic_erased_probe, %function
    .thumb_func
r1_dynamic_erased_probe:
    ldr     r0, 4f
    ldr     r1, [r0]
    ldr     r2, =0xffffffff
    cmp     r1, r2
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
    .balign 4
4:
    .word   TARGET_PLACEHOLDER
    .ltorg
    .size r1_dynamic_erased_probe, .-r1_dynamic_erased_probe

    .section .text.r1_dynamic_write_probe, "ax", %progbits
    .global r1_dynamic_write_probe
    .type r1_dynamic_write_probe, %function
    .thumb_func
r1_dynamic_write_probe:
    ldr     r4, 8f
    ldr     r0, [r4]
    ldr     r1, =0xffffffff
    cmp     r0, r1
    bne     5f
    svc     #0x11
    ldr     r5, =NVMC_CONFIG_THUMB
    movs    r0, #1
    blx     r5
    ldr     r6, =TEST_MARKER
    str     r6, [r4]
    ldr     r0, [r4]
    cmp     r0, r6
    bne     5f
    movs    r0, #0xb1
    b       6f
5:
    movs    r0, #0
6:
    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
7:
    b       7b
    .balign 4
8:
    .word   TARGET_PLACEHOLDER
    .ltorg
    .size r1_dynamic_write_probe, .-r1_dynamic_write_probe

    .section .text.r1_dynamic_erase_probe, "ax", %progbits
    .global r1_dynamic_erase_probe
    .type r1_dynamic_erase_probe, %function
    .thumb_func
r1_dynamic_erase_probe:
    ldr     r4, 12f
    svc     #0x11
    ldr     r5, =NVMC_CONFIG_THUMB
    movs    r0, #2
    blx     r5
    ldr     r1, =NVMC_ERASEPAGE
    str     r4, [r1]
    movs    r0, #0
    blx     r5
    ldr     r0, [r4]
    ldr     r1, =0xffffffff
    cmp     r0, r1
    bne     9f
    movs    r0, #0xb1
    b       10f
9:
    movs    r0, #0
10:
    ldr     r1, =POWER_GPREGRET
    strb    r0, [r1]
    dsb     sy
    ldr     r1, =SCB_AIRCR
    ldr     r0, =AIRCR_SYSRESETREQ
    str     r0, [r1]
11:
    b       11b
    .balign 4
12:
    .word   TARGET_PLACEHOLDER
    .ltorg
    .size r1_dynamic_erase_probe, .-r1_dynamic_erase_probe
