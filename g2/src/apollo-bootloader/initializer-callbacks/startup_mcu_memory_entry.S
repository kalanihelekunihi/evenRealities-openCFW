/* SPDX-License-Identifier: MIT
 * Stock 0x41bbd0 receives a descriptor pointer in R0 and an ambient R1.
 * The core explicitly carries R1 into its high return word. No data stub. */
.syntax unified
.thumb
.section .text.opencfw_boot_startup_mcu_memory,"ax",%progbits
.global opencfw_boot_startup_mcu_memory
.type opencfw_boot_startup_mcu_memory,%function
.thumb_func
opencfw_boot_startup_mcu_memory:
    b.w opencfw_boot_startup_mcu_memory_core
.size opencfw_boot_startup_mcu_memory,.-opencfw_boot_startup_mcu_memory
.section .note.GNU-stack,"",%progbits
