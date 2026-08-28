/*
 * SPDX-License-Identifier: MIT
 * Clean-room exact Cortex-M55 reconstruction of [0x00423DD0,0x00423E40).
 */

.syntax unified
.thumb
.section .text.open_cfw_bootloader_stage_two_423dd0,"ax",%progbits
.p2align 1

.global open_cfw_bootloader_stage_two_status_423dd0
.type open_cfw_bootloader_stage_two_status_423dd0,%function
.thumb_func
open_cfw_bootloader_stage_two_status_423dd0:
    push {r2, r3, r4, lr}
    bl open_cfw_bootloader_critical_save_41b8ec
    str r0, [sp]
    ldr r1, .Lstage_two_counter
    ldrb r0, [r1]
    cmp r0, #0
    beq .Lstage_two_counter_read
    ldrb r0, [r1]
    subs r0, r0, #1
    strb r0, [r1]
.Lstage_two_counter_read:
    ldrb r0, [r1]
    cmp r0, #0
    beq .Lstage_two_disable
    movs r4, #3
    b .Lstage_two_restore
.Lstage_two_disable:
    movs r0, #0
    ldr r1, .Lstage_two_guard
    strb r0, [r1]
    bl open_cfw_bootloader_debug_disable_422468
    movs r4, r0
    cmp r4, #3
    bne .Lstage_two_restore
    movs r4, #0
.Lstage_two_restore:
    ldr r0, [sp]
    msr primask, r0
    movs r0, r4
    pop {r1, r2, r4, pc}
.size open_cfw_bootloader_stage_two_status_423dd0, .-open_cfw_bootloader_stage_two_status_423dd0

.Lstage_two_guard:
    .word 0x200271C2
.Lstage_two_counter:
    .word 0x200271C3

.section .text.open_cfw_bootloader_stage_two_mode_flags_423e14,"ax",%progbits
.p2align 1

.global open_cfw_bootloader_stage_two_mode_flags_423e14
.type open_cfw_bootloader_stage_two_mode_flags_423e14,%function
.thumb_func
open_cfw_bootloader_stage_two_mode_flags_423e14:
    ldr.w r2, [r0, #0x838]
    cmp r2, #1
    beq .Lstage_two_mode_one
    cmp r2, #2
    beq .Lstage_two_mode_two
    b .Lstage_two_mode_default
.Lstage_two_mode_one:
    orr r1, r1, #0x4000
    orrs r1, r1, #0xA0
    movs r2, #2
    str.w r2, [r0, #0x838]
    b .Lstage_two_mode_return
.Lstage_two_mode_two:
    mov.w r1, #0x4000
    b .Lstage_two_mode_return
.Lstage_two_mode_default:
    orrs r1, r1, #0x4080
.Lstage_two_mode_return:
    movs r0, r1
    bx lr
.size open_cfw_bootloader_stage_two_mode_flags_423e14, .-open_cfw_bootloader_stage_two_mode_flags_423e14
