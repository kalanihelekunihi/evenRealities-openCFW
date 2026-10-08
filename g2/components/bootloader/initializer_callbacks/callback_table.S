/* SPDX-License-Identifier: MIT
 * Source-defined callback records for the locked 0x433440 table.
 * The callback order and priorities are reconstructed data; the pointers are
 * relocations to source functions, never copied stock code addresses.
 */
.syntax unified
.section .boot_initializer_callbacks,"a",%progbits
.balign 4
.global opencfw_boot_initializer_callback_records
.type opencfw_boot_initializer_callback_records,%object
opencfw_boot_initializer_callback_records:
    .word opencfw_boot_init_callback_platform_sequence
    .word 1
    .word opencfw_boot_init_callback_services
    .word 1
    .word opencfw_boot_init_callback_redirect
    .word 25
    .word opencfw_boot_allocator_init
    .word 26
.size opencfw_boot_initializer_callback_records, .-opencfw_boot_initializer_callback_records

/* Source-defined 4x16-byte platform-context config records. Values are the
 * authenticated scalar data consumed through pointers in scatter RAM; this is
 * data, not copied executable content. */
.section .boot_context_config,"a",%progbits
.balign 4
.global opencfw_boot_context_config_records
.type opencfw_boot_context_config_records,%object
opencfw_boot_context_config_records:
    .word 0x19,0x1a,0x4200,0x4200
    .word 0x22,0x23,0x4200,0x4200
    .word 0x2f,0x30,0x4200,0x4200
    .word 0x16,0x17,0x4200,0x4200
.size opencfw_boot_context_config_records, .-opencfw_boot_context_config_records
.section .note.GNU-stack,"",%progbits
