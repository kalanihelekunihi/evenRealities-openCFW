/* SPDX-License-Identifier: MIT
 * Main 0x491102 delegates the requested microseconds to 0x4807a0.
 * The NOR polling caller does not use the wrapper's incidental R0 value.
 */
#include <stdint.h>

extern void audio_delay_us_selected(uint32_t microseconds); /* 0x4807a0 */

void g2_norflash_delay_us_491102(uint32_t microseconds)
{
    audio_delay_us_selected(microseconds);
}
