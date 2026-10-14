/* SPDX-License-Identifier: MIT
 * Stock 0x421584..0x4215ae SWAR population count over one 32-bit clock-user
 * bitmap word. This is a source-owned scalar helper independent of MMIO.
 */
#include <stdint.h>
#include "clock_popcount_421584.h"

uint32_t opencfw_boot_clock_popcount(uint32_t bits)
{
    bits -= (bits >> 1) & UINT32_C(0x55555555);
    bits = (bits & UINT32_C(0x33333333)) + ((bits >> 2) & UINT32_C(0x33333333));
    return (((bits + (bits >> 4)) & UINT32_C(0x0f0f0f0f)) * UINT32_C(0x01010101)) >> 24;
}
