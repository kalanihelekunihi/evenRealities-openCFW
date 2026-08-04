/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Clang-syntax, sectionized adaptation of the remaining port leaves from:
 *
 *   FreeRTOS-Kernel V10.5.1
 *   commit def7d2df2b0506d3d249334974f51e427c17a41c
 *   portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s
 *
 * The authenticated G2 configuration selects the non-MPU, non-TrustZone
 * context path with floating-point context enabled:
 *
 *   configENABLE_MPU = 0
 *   configENABLE_TRUSTZONE = 0
 *   configENABLE_FPU = 1
 *   configMAX_SYSCALL_INTERRUPT_PRIORITY = 0x30
 *
 * ulSetInterruptMask and vClearInterruptMask are intentionally absent. They
 * already live in runtime_freertos_interrupt_mask.S and are installed in place.
 *
 * Each function is independently sectionized for in-place installation. The
 * narrow LDR literals carry explicit R_ARM_THM_PC8 relocations to two undefined
 * linker symbols naming the authenticated shared stock-pool words:
 *
 *   open_cfw_freertos_px_current_tcb_literal = 0x005FA134
 *   open_cfw_freertos_vtor_literal           = 0x005FA138
 *
 * Their stored values remain 0x20074A20 (pxCurrentTCB) and 0xE000ED08
 * (SCB_VTOR). No section owns a local literal pool or alignment tail, so each
 * source section is exactly the corresponding fixed stock function span.
 */

    .syntax unified
    .cpu cortex-m55
    .fpu fpv5-sp-d16
    .thumb

    .extern open_cfw_freertos_px_current_tcb_literal
    .extern open_cfw_freertos_vtor_literal
    .extern vTaskSwitchContext
    .extern vPortSVCHandler_C

    .section .text.vRestoreContextOfFirstTask, "ax", %progbits
    .p2align 1
    .global vRestoreContextOfFirstTask
    .type vRestoreContextOfFirstTask, %function
    .thumb_func
vRestoreContextOfFirstTask:
    .reloc  ., R_ARM_THM_PC8, open_cfw_freertos_px_current_tcb_literal
    .inst.n 0x4a00             /* ldr r2, [pc, #0]; linker supplies imm8 */
    ldr     r1, [r2]
    ldr     r0, [r1]
    ldmia   r0!, {r1-r2}
    msr     psplim, r1
    movs    r1, #2
    msr     control, r1
    adds    r0, #32
    msr     psp, r0
    isb     sy
    mov.w   r0, #0
    msr     basepri, r0
    bx      r2
    .size vRestoreContextOfFirstTask, . - vRestoreContextOfFirstTask

    .section .text.vRaisePrivilege, "ax", %progbits
    .p2align 1
    .global vRaisePrivilege
    .type vRaisePrivilege, %function
    .thumb_func
vRaisePrivilege:
    mrs     r0, control
    bic     r0, r0, #1
    msr     control, r0
    bx      lr
    .size vRaisePrivilege, . - vRaisePrivilege

    .section .text.vStartFirstTask, "ax", %progbits
    .p2align 1
    .global vStartFirstTask
    .type vStartFirstTask, %function
    .thumb_func
vStartFirstTask:
    .reloc  ., R_ARM_THM_PC8, open_cfw_freertos_vtor_literal
    .inst.n 0x4800             /* ldr r0, [pc, #0]; linker supplies imm8 */
    ldr     r0, [r0]
    ldr     r0, [r0]
    msr     msp, r0
    cpsie   i
    cpsie   f
    dsb     sy
    isb     sy
    svc     #2
    .size vStartFirstTask, . - vStartFirstTask

    .section .text.PendSV_Handler, "ax", %progbits
    .p2align 1
    .global PendSV_Handler
    .type PendSV_Handler, %function
    .thumb_func
PendSV_Handler:
    mrs     r0, psp
    tst     lr, #0x10
    it      eq
    vstmdbeq r0!, {s16-s31}
    mrs     r2, psplim
    mov     r3, lr
    stmdb   r0!, {r2-r11}

    .reloc  ., R_ARM_THM_PC8, open_cfw_freertos_px_current_tcb_literal
    .inst.n 0x4a00             /* ldr r2, [pc, #0]; linker supplies imm8 */
    ldr     r1, [r2]
    str     r0, [r1]

    mov.w   r0, #0x30
    msr     basepri, r0
    dsb     sy
    isb     sy
    bl      vTaskSwitchContext
    mov.w   r0, #0
    msr     basepri, r0

    .reloc  ., R_ARM_THM_PC8, open_cfw_freertos_px_current_tcb_literal
    .inst.n 0x4a00             /* ldr r2, [pc, #0]; linker supplies imm8 */
    ldr     r1, [r2]
    ldr     r0, [r1]
    ldmia   r0!, {r2-r11}

    tst     r3, #0x10
    it      eq
    vldmiaeq r0!, {s16-s31}

    msr     psplim, r2
    msr     psp, r0
    bx      r3
    .size PendSV_Handler, . - PendSV_Handler

    .section .text.SVC_Handler, "ax", %progbits
    .p2align 1
    .global SVC_Handler
    .type SVC_Handler, %function
    .thumb_func
SVC_Handler:
    tst     lr, #4
    ite     eq
    mrseq   r0, msp
    mrsne   r0, psp
    b       vPortSVCHandler_C
    .size SVC_Handler, . - SVC_Handler

    .section .note.GNU-stack, "", %progbits
