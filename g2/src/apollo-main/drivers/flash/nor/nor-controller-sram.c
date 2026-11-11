/* SPDX-License-Identifier: MIT
 * Main NOR controller handle is a fixed SRAM word, not an allocated C global.
 * The locked 0x470d80 and 0x4709d0 literal loads both resolve to 0x20074544.
 * Startup ownership and initialization of that SRAM word remain open.
 */
#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4, "Apollo controller handle width");

/* sim15: stock 0x20074544 is past the 17752-byte stock .data init image
 * (.waves/init_20000000.bin), i.e. zero-initialized .bss, so an own zeroed
 * word is equivalent; the raw address aliased an unrelated object here. */
/* g2_norflash_controller_handle_20074544: stock 0x20074544 is one cell; defined as an alias of audio_uart_font_flash_device (Fix 31). */
extern uint32_t g2_norflash_controller_handle_20074544;
