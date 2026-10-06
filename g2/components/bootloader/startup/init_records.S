/* SPDX-License-Identifier: MIT
 * Source-defined scatter records, not executable bytes. Stream addresses and
 * lengths are the locked valid initializer inputs; compression is still a
 * verifier fixture, not yet reconstructed from source. Callback relocations
 * include the Thumb bit and are relative to their own slot.
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
    .word 0x434461 - .
    .word (22 << 1),0x40
    .word opencfw_boot_expand_adapter - .
    .word 0x4341c0 - .
    .word (625 << 1),0x20000000
    .word opencfw_boot_expand_adapter - .
    .word 0x434431 - .
    .word (48 << 1),0x20080000
.size opencfw_boot_init_records, .-opencfw_boot_init_records
.section .note.GNU-stack,"",%progbits
