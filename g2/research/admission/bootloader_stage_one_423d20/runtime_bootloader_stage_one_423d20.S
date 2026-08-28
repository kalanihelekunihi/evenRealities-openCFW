/*
 * SPDX-License-Identifier: MIT
 * Clean-room exact Cortex-M55 reconstruction of [0x00423D20,0x00423DCE).
 */

.syntax unified
.thumb
.section .text.open_cfw_bootloader_stage_one_423d20,"ax",%progbits
.p2align 1

.global open_cfw_bootloader_stage_one_423d20
.type open_cfw_bootloader_stage_one_423d20,%function
.thumb_func
open_cfw_bootloader_stage_one_423d20:
    push {r7, lr}
    movs r0, #0
    bl open_cfw_bootloader_stage_one_status_423d58
    ldr r0, .Lstage_one_register
    ldr r1, [r0]
    bics r1, r1, #0x10
    str r1, [r0]
    ldr r1, [r0]
    lsrs r1, r1, #1
    lsls r1, r1, #1
    str r1, [r0]
    movs r3, #0
    movs r2, #0
    ldr r1, .Lstage_one_register
    mov.w r0, #1000
    bl open_cfw_bootloader_delay_status_change_41d21c
    cmp r0, #0
    bne .Lstage_one_return
    bl open_cfw_bootloader_debug_disable_422468
    cmp r0, #3
    bne .Lstage_one_return
    movs r0, #0
.Lstage_one_return:
    pop {r1, pc}
.size open_cfw_bootloader_stage_one_423d20, .-open_cfw_bootloader_stage_one_423d20

.global open_cfw_bootloader_stage_one_status_423d58
.type open_cfw_bootloader_stage_one_status_423d58,%function
.thumb_func
open_cfw_bootloader_stage_one_status_423d58:
    push {r7, lr}
    bl open_cfw_bootloader_stage_one_wait_zero_423dc4
    cmp r0, #0
    beq .Lstage_one_error
    bl open_cfw_bootloader_stage_one_wait_reg80_423d7a
    cmp r0, #0
    bne .Lstage_one_delay
.Lstage_one_error:
    movs r0, #4
    b .Lstage_one_status_return
.Lstage_one_delay:
    mov.w r0, #500
    bl open_cfw_bootloader_retained_delay_41d1c0
    movs r0, #0
.Lstage_one_status_return:
    pop {r1, pc}
.size open_cfw_bootloader_stage_one_status_423d58, .-open_cfw_bootloader_stage_one_status_423d58

.global open_cfw_bootloader_stage_one_wait_reg80_423d7a
.type open_cfw_bootloader_stage_one_wait_reg80_423d7a,%function
.thumb_func
open_cfw_bootloader_stage_one_wait_reg80_423d7a:
    push {r7, lr}
    movs r3, #0
    movs.w r2, #0x00800000
    ldr r1, .Lstage_one_register
    mov.w r0, #1000
    bl open_cfw_bootloader_delay_status_change_41d21c
    cmp r0, #0
    bne .Lstage_one_reg80_false
    movs r0, #1
    b .Lstage_one_reg80_return
.Lstage_one_reg80_false:
    movs r0, #0
.Lstage_one_reg80_return:
    uxtb r0, r0
    pop {r1, pc}
.size open_cfw_bootloader_stage_one_wait_reg80_423d7a, .-open_cfw_bootloader_stage_one_wait_reg80_423d7a

    .short 0
.Lstage_one_register:
    .word 0xE0000E80

.global open_cfw_bootloader_stage_one_wait_index_423da0
.type open_cfw_bootloader_stage_one_wait_index_423da0,%function
.thumb_func
open_cfw_bootloader_stage_one_wait_index_423da0:
    push {r7, lr}
    movs r1, r0
    lsls r1, r1, #2
    adds.w r1, r1, #-0x20000000
    movs r3, #1
    movs r2, #3
    mov.w r0, #1000
    bl open_cfw_bootloader_delay_status_change_41d21c
    cmp r0, #0
    bne .Lstage_one_index_false
    movs r0, #1
    b .Lstage_one_index_return
.Lstage_one_index_false:
    movs r0, #0
.Lstage_one_index_return:
    uxtb r0, r0
    pop {r1, pc}
.size open_cfw_bootloader_stage_one_wait_index_423da0, .-open_cfw_bootloader_stage_one_wait_index_423da0

.global open_cfw_bootloader_stage_one_wait_zero_423dc4
.type open_cfw_bootloader_stage_one_wait_zero_423dc4,%function
.thumb_func
open_cfw_bootloader_stage_one_wait_zero_423dc4:
    push {r7, lr}
    movs r0, #0
    bl open_cfw_bootloader_stage_one_wait_index_423da0
    pop {r1, pc}
.size open_cfw_bootloader_stage_one_wait_zero_423dc4, .-open_cfw_bootloader_stage_one_wait_zero_423dc4
