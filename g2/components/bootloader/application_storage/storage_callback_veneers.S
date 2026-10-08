/* SPDX-License-Identifier: MIT
 * Four-byte Thumb veneers at the callback pointers published in the locked
 * descriptor. Each jumps to independently compiled readable C source.
 */
.syntax unified
.thumb

.section .text.storage_read,"ax",%progbits
.global opencfw_boot_storage_read
.type opencfw_boot_storage_read,%function
.thumb_func
opencfw_boot_storage_read:
    b.w opencfw_boot_storage_read_impl
.size opencfw_boot_storage_read, .-opencfw_boot_storage_read

.section .text.storage_program,"ax",%progbits
.global opencfw_boot_storage_program
.type opencfw_boot_storage_program,%function
.thumb_func
opencfw_boot_storage_program:
    b.w opencfw_boot_storage_program_impl
.size opencfw_boot_storage_program, .-opencfw_boot_storage_program

.section .text.storage_erase,"ax",%progbits
.global opencfw_boot_storage_erase_validate
.type opencfw_boot_storage_erase_validate,%function
.thumb_func
opencfw_boot_storage_erase_validate:
    b.w opencfw_boot_storage_erase_validate_impl
.size opencfw_boot_storage_erase_validate, .-opencfw_boot_storage_erase_validate
