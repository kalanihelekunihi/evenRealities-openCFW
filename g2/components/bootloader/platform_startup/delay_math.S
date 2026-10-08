/* SPDX-License-Identifier: MIT
 * Reconstructed stock41d1c0: float conversion/scaling and ROM-cycle wrapper.
 * Literal250.0/96.0 and peripheral bits[4:3] are source-defined operands.
 * The resident ROM body at Thumb41 is not present in the OTA artifact.
 */
.syntax unified
.thumb
.fpu fpv4-sp-d16
.section .text.opencfw_boot_delay_us_math,"ax",%progbits
.global opencfw_boot_delay_us_math
.thumb_func
opencfw_boot_delay_us_math:
    push {r7,lr}
    vmov s0,r0
    vcvt.f32.u32 s0,s0
    vcvt.u32.f32 s0,s0,#5
    vmov r0,s0
    movw r1,#0x1000
    movt r1,#0x4002
    ldr r1,[r1]
    ubfx r1,r1,#3,#2
    cmp r1,#2
    beq 1f
    movs r1,#15
    b 2f
1:  vmov s0,r0
    vcvt.f32.u32 s0,s0
    vldr s1,scale_numerator
    vmul.f32 s0,s0,s1
    vldr s1,scale_denominator
    vdiv.f32 s0,s0,s1
    vcvt.u32.f32 s0,s0
    vmov r0,s0
    movs r1,#24
2:  cmp r1,r0
    bhs 3f
    subs r0,r0,r1
    bl opencfw_boot_rom_delay_cycles
3:  pop {r0,pc}
.balign 4
scale_numerator: .float 250.0
scale_denominator: .float 96.0
.section .note.GNU-stack,"",%progbits
