/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* PGA quotient bands 4..8 use correction 5 * (band - 3). */
#define PGA_CORRECTION(band) (5 * ((band) - 3))
const uint8_t open_cfw_gx8002_pga_corrections[5] __attribute__((section(".rodata.pga_corrections"),aligned(1))) = {
    PGA_CORRECTION(4), PGA_CORRECTION(5), PGA_CORRECTION(6), PGA_CORRECTION(7), PGA_CORRECTION(8)
};
enum { STEREO, LEFT_ONLY, RIGHT_ONLY, MONO };
/* The deployed channel table has one row per register selector. */
const uint8_t open_cfw_gx8002_channel_selectors[3][4] __attribute__((section(".rodata.channel_selectors"),aligned(1))) = {
    { [RIGHT_ONLY]=1 },
    { [STEREO]=1, [RIGHT_ONLY]=1, [MONO]=1 },
    { [MONO]=1 }
};
