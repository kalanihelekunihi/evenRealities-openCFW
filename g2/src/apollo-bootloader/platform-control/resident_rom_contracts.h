/* SPDX-License-Identifier: MIT
 * Resident ROM entry contracts outside the OTA flash image. Thumb addresses
 * and observed call shapes only; no ROM behavior is synthesized here.
 */
#ifndef OPENCFW_BOOT_RESIDENT_ROM_CONTRACTS_H
#define OPENCFW_BOOT_RESIDENT_ROM_CONTRACTS_H
#include <stdint.h>

enum {
    OPENCFW_BOOT_ROM_INFO_READ_THUMB = 0x00000049u,
    OPENCFW_BOOT_ROM_DELAY_CYCLES_THUMB = 0x00000041u,
    OPENCFW_BOOT_ROM_MRAM_PROGRAM_THUMB = 0x0200ff21u
};

/* Five arguments are recovered at the 0x42e8a4 flash bridge. */
extern uint32_t opencfw_boot_rom_mram_program(uint32_t key,
    uint32_t operation, const void *source, uint32_t word_offset,
    uint32_t words);

/* `delay_math.S` passes a cycle count in R0 and discards the ROM return. */
extern void opencfw_boot_rom_delay_cycles(uint32_t cycles);

/* The info-read thunk forwards ambient registers without a recovered C ABI.
 * Keep opencfw_boot_rom48 declared only by the assembly callsite. */
#endif
