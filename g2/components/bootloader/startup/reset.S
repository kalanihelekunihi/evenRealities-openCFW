/* SPDX-License-Identifier: MIT
 * Reconstructed startup state at 0x43291a/0x43293c. Cortex-M55-only stack
 * limit writes; no claim that a Cortex-M4 fixture validates these operations.
 * Neither entry can return because system_entry is the terminal boot chain.
 */
.syntax unified
.thumb
.text
.global opencfw_boot_reset_entry
.thumb_func
opencfw_boot_reset_entry:
    ldr r0,=0x2007d000
    msr msplim,r0
    msr psplim,r0
    bl opencfw_boot_stack_entry
    bx lr
.global opencfw_boot_stack_entry
.thumb_func
opencfw_boot_stack_entry:
    ldr r0,=0xfef5eda5
    mov r1,r0
    push {r0,r1}
    mov r0,sp
    msr psp,r0
    nop.w
    bl opencfw_boot_fpu_init
    bl opencfw_boot_system_entry
.ltorg
.section .note.GNU-stack,"",%progbits
