/* SPDX-License-Identifier: MIT
 * Exact source form of stock 0x41d28a: push {r7,lr}; bl 0x48; pop {r0,pc}.
 * The resident ROM routine itself remains an external implementation.
 */
.syntax unified
.thumb
.section .text.info_read_rom_thunk,"ax",%progbits
.global opencfw_boot_info_rom_read
.type opencfw_boot_info_rom_read,%function
.thumb_func
opencfw_boot_info_rom_read:
    push {r7, lr}
    bl opencfw_boot_rom48
    pop {r0, pc}
.size opencfw_boot_info_rom_read, .-opencfw_boot_info_rom_read
.section .note.GNU-stack,"",%progbits
