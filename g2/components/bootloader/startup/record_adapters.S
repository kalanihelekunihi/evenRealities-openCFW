/* SPDX-License-Identifier: MIT
 * Source adapters preserve the stock callback locations and implicit R9
 * static base, passing it explicitly to the reconstructed C helpers.
 */
.syntax unified
.thumb
.section .boot_expand_adapter,"ax",%progbits
.global opencfw_boot_expand_adapter
.thumb_func
opencfw_boot_expand_adapter:
    mov r1,r9
    b.w opencfw_boot_expand_locked_data_record
.section .boot_zero_adapter,"ax",%progbits
.global opencfw_boot_zero_adapter
.thumb_func
opencfw_boot_zero_adapter:
    mov r1,r9
    b.w opencfw_boot_zero_table
.section .note.GNU-stack,"",%progbits
