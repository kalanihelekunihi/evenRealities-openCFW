/* SPDX-License-Identifier: MIT
 * Source-defined scatter records, not executable bytes. The three supported
 * outputs are installed from source assembly, structured C data, and a zero
 * initializer; their compressed input offsets are unused. Callback
 * relocations include the Thumb bit and are relative to their own slot.
 */
.syntax unified
.section .boot_init_records,"a",%progbits
.global opencfw_boot_init_records
opencfw_boot_init_records:
    .word opencfw_boot_zero_adapter - .
    .word 0x26c6c,0x2000055c
    .word 0x74100,0x20081000
    .word 0
    .word opencfw_boot_expand_adapter - .
    .word 0 /* source-owned ITCM helper image; adapter ignores stream offset */
    .word (22 << 1),0x40
    .word opencfw_boot_expand_adapter - .
    .word 0 /* source-owned initialized SRAM; adapter ignores stream offset */
    .word (625 << 1),0x20000000
    .word opencfw_boot_expand_adapter - .
    .word 0 /* source-owned zero SRAM; adapter ignores stream offset */
    .word (48 << 1),0x20080000
.size opencfw_boot_init_records, .-opencfw_boot_init_records
.section .note.GNU-stack,"",%progbits
