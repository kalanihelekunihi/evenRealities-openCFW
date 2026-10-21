/* SPDX-License-Identifier: MIT
 * Stock 0x41fadc saves caller R7 and returns it through pop {r0,pc}.
 */
.syntax unified
.thumb
.section .text.opencfw_publish_mspi_mode,"ax",%progbits
.global opencfw_publish_mspi_mode
.type opencfw_publish_mspi_mode,%function
.thumb_func
opencfw_publish_mspi_mode:
    push {r7, lr}
    bl opencfw_bl_mspi_mode_publish_core
    pop {r0, pc}
.size opencfw_publish_mspi_mode, .-opencfw_publish_mspi_mode
.section .note.GNU-stack,"",%progbits
