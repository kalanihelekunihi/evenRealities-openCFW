/* SPDX-License-Identifier: MIT
 * Native 0x42bf54 gate. The return ABI deliberately restores ambient r5
 * into r1 (push r5-r7/lr, pop r1-r3/pc), and the temperature child receives
 * -40.0f in VFP s0 with the saved-register stack as its output area.
 * These effects cannot be expressed by an ordinary C uint32_t signature.
 */
.syntax unified
.thumb
.fpu fpv5-sp-d16
.section .text.opencfw_boot_hardware_readiness_gate,"ax",%progbits
.global opencfw_boot_hardware_readiness_gate
.type opencfw_boot_hardware_readiness_gate,%function
.thumb_func
opencfw_boot_hardware_readiness_gate:
    push {r5,r6,r7,lr}
    ldr r0, =0x40021008
    ldr r0, [r0]
    cmp r0, #0
    bne .Lunavailable
    ldr r0, =0x40021010
    ldr r0, [r0]
    cmp r0, #0
    bne .Lunavailable
    movs r0, #29
    bl opencfw_bl_mspi_mode_enter
    cmp r0, #0
    bne .Lunavailable
    mov r0, sp
    vldr s0, .Lminus_forty
    bl opencfw_boot_startup_temperature
    cmp r0, #0
    bne .Lunavailable
    movs r3, #0
    movs r2, #1
    ldr r1, =0x400083e0
    movw r0, #2500
    bl opencfw_boot_control_delay_status_change
    cmp r0, #0
    beq .Ldone
    movs r0, #4
    b .Lreturn
.Lunavailable:
    movs r0, #1
    b .Lreturn
.Ldone:
    movs r0, #0
.Lreturn:
    pop {r1,r2,r3,pc}
    .balign 4
.Lminus_forty:
    .word 0xc2200000
.size opencfw_boot_hardware_readiness_gate, .-opencfw_boot_hardware_readiness_gate
