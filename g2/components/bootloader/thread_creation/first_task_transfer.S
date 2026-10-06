/* SPDX-License-Identifier: MIT. Independent assembly for stock41b2e0. */
.syntax unified
.thumb
.text
.global opencfw_boot_first_task_transfer
.type opencfw_boot_first_task_transfer,%function
.thumb_func
opencfw_boot_first_task_transfer:
    ldr r0, =0xe000ed08
    ldr r0, [r0]
    ldr r0, [r0]
    msr msp, r0
    cpsie i
    cpsie f
    dsb sy
    isb sy
    svc #2
    /* Stock falls through into BASEPRI helper41b2f8 after SVC. */
    b opencfw_bl_mask_interrupts
.size opencfw_boot_first_task_transfer, .-opencfw_boot_first_task_transfer
