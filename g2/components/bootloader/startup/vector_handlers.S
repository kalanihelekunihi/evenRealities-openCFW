/* SPDX-License-Identifier: MIT
 * Locked first-vector handlers: 0x417c2e, 0x416026, 0x432938 and
 * SysTick 0x41b428. The three loops are real nonreturning stock behavior.
 * SysTick runs in privileged exception mode; its BASEPRI mask is restored.
 */
.syntax unified
.thumb
.text
.global opencfw_boot_nmi_loop
.thumb_func
opencfw_boot_nmi_loop:
1:  b 1b
.global opencfw_boot_fault_loop
.thumb_func
opencfw_boot_fault_loop:
2:  b 2b
.global opencfw_boot_reserved_loop
.thumb_func
opencfw_boot_reserved_loop:
3:  b 3b
.global opencfw_boot_systick_entry
.thumb_func
opencfw_boot_systick_entry:
    push {r4,lr}
    mrs r4,basepri
    movs r0,#48
    msr basepri,r0
    dsb sy
    isb sy
    bl opencfw_bl_tick_increment
    cbz r0,4f
    ldr r1,=0xe000ed04
    ldr r0,=0x10000000
    str r0,[r1]
4:  msr basepri,r4
    dsb sy
    isb sy
    pop {r4,pc}
.section .note.GNU-stack,"",%progbits
