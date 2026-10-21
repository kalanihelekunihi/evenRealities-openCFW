/* SPDX-License-Identifier: MIT
 * Native 0x422590 pushes r7/lr and pops r1/pc: r1 is the saved ambient r7
 * after the handler returns. The C core owns pointer/literal/handler logic.
 */
.syntax unified
.thumb
.section .text.opencfw_boot_constraint_dispatch,"ax",%progbits
.global opencfw_boot_constraint_dispatch
.type opencfw_boot_constraint_dispatch,%function
.thumb_func
opencfw_boot_constraint_dispatch:
    push {r7,lr}
    bl opencfw_boot_constraint_dispatch_core
    pop {r1,pc}
.size opencfw_boot_constraint_dispatch, .-opencfw_boot_constraint_dispatch
