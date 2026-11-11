/* SPDX-License-Identifier: MIT
 * Thumb-typed absolute resident-ROM entry symbols. These are external ROM
 * dependencies, not firmware bodies or retained executable bytes. The ARM C
 * compiler emits this file-scope symbol declaration for the final link only.
 */
__asm__(
    ".syntax unified\n"
    ".thumb\n"
    ".global opencfw_boot_rom48\n"
    ".type opencfw_boot_rom48, %function\n"
    ".thumb_set opencfw_boot_rom48, 0x00000049\n"
    ".global opencfw_boot_rom_delay_cycles\n"
    ".type opencfw_boot_rom_delay_cycles, %function\n"
    ".thumb_set opencfw_boot_rom_delay_cycles, 0x00000041\n"
    ".global opencfw_boot_rom_mram_program\n"
    ".type opencfw_boot_rom_mram_program, %function\n"
    ".thumb_set opencfw_boot_rom_mram_program, 0x0200ff21\n");
