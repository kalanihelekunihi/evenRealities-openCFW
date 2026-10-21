/* SPDX-License-Identifier: MIT
 * Main NOR controller handle is a fixed SRAM word, not an allocated C global.
 * The locked 0x470d80 and 0x4709d0 literal loads both resolve to 0x20074544.
 * Startup ownership and initialization of that SRAM word remain open.
 */
#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4, "Apollo controller handle width");

__asm__(".global g2_norflash_controller_handle_20074544\n"
        ".set g2_norflash_controller_handle_20074544, 0x20074544\n");
