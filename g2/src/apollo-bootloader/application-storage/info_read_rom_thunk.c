/* SPDX-License-Identifier: MIT
 * Stock INFO read thunk: call the resident-ROM INFO reader. Stock returns a
 * stale register; the caller ignores the result. */
#include <stdint.h>

extern uint32_t opencfw_boot_rom48(uint32_t address, volatile uint32_t *destination,
                                   uint32_t word_count);

uint32_t opencfw_boot_info_rom_read(uint32_t address, volatile uint32_t *destination,
                                    uint32_t word_count)
{
    (void)opencfw_boot_rom48(address, destination, word_count);
    return 0u;
}
