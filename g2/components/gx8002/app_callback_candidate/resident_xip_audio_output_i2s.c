/* SPDX-License-Identifier: MIT
 * Native XIP 0x10204228..0x102042cf. Seven-word I2S descriptor is
 * passed by value; the clock gate call occurs before input validation.
 */
#include <stdint.h>
#include "resident_xip_audio_output_types.h"

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const active =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027334);

static void replace_bits(volatile uint32_t *reg, uint32_t mask, uint32_t bits)
{
    *reg = (*reg & ~mask) | (bits & mask);
}

int32_t gx8002_xip_audio_output_i2s_10204228(gx8002_i2s_output output)
{
    const uint32_t *v = output.word;
    gx8002_resident_platform_gate_25080(2u, 1u);
    if (v[3] >= 2u || v[1] >= 3u || v[0] == 8u)
        return -1;
    volatile uint32_t *reg = &ain[8u / 4u];
    replace_bits(reg, 0x3u, v[0]);
    replace_bits(reg, 0xcu, v[1] << 2u);
    replace_bits(reg, 0x10u, v[2] << 4u);
    replace_bits(reg, 0x20u, v[3] << 5u);
    replace_bits(reg, 0xc0u, v[4] << 6u);
    replace_bits(reg, 0xf00u, v[5] << 8u);
    replace_bits(reg, 0xf000u, v[6] << 12u);
    replace_bits(reg, 0x80000000u, 0u);
    replace_bits(reg, 0x40000000u, 0x40000000u);
    *active = *active | 8u;
    replace_bits(reg, 0x10000u, 0x10000u);
    return 0;
}
