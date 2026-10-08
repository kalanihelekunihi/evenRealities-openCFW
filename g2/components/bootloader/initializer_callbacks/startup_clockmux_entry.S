/* SPDX-License-Identifier: MIT
 * Source ABI adapter for locked 0x41acb2: capture ambient carries and
 * reproduce the stock entry/return register rotation. No opcode payload. */
.syntax unified
.thumb
.section .text.opencfw_boot_clockmux_entry,"ax",%progbits
.global opencfw_boot_clockmux_entry
.type opencfw_boot_clockmux_entry,%function
.thumb_func
opencfw_boot_clockmux_entry:
    push {r1,r2,r3,r4,r5,lr}
    sub sp,sp,#16
    str r1,[sp,#0]
    str r2,[sp,#4]
    str r5,[sp,#8]
    mov r0,sp
    bl am_hal_pwrctrl_low_power_init_clockmux_fragment
    ldr r0,[sp,#0]
    str r0,[sp,#16]
    ldr r0,[sp,#4]
    str r0,[sp,#20]
    add sp,sp,#16
    pop {r0,r1,r2,r4,r5,pc}
.size opencfw_boot_clockmux_entry,.-opencfw_boot_clockmux_entry

.section .note.GNU-stack,"",%progbits
