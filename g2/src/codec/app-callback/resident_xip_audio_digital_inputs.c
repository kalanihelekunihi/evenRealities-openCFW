/* SPDX-License-Identifier: MIT
 * Native digital audio input setup 0x10203e7c/0x10203ec8.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_resident_delay_ms_2598c(uint32_t);

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const audio_channels =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027330);

static void replace_bits(uint32_t word, uint32_t mask, uint32_t bits)
{
    ain[word] = (ain[word] & ~mask) | (bits & mask);
}

uint32_t gx8002_xip_audio_input_pdm_10203e7c(uint32_t mode)
{
    gx8002_resident_platform_gate_25080(8u, 1u);
    replace_bits(0x28u / 4u, UINT32_C(0xfc00), 0u);
    replace_bits(0x2cu / 4u, UINT32_C(0xfc00), 0u);
    replace_bits(0u, UINT32_C(0x200), (mode & 1u) << 9u);
    replace_bits(0u, UINT32_C(0x4000), UINT32_C(0x4000));
    *audio_channels |= 2u;
    gx8002_resident_delay_ms_2598c(10u);
    return 0u;
}

void gx8002_xip_audio_input_i2s_10203ec8(
    uint32_t a, uint32_t b, uint32_t c, uint32_t d,
    uint32_t e, uint32_t f)
{
    gx8002_resident_platform_gate_25080(2u, 1u);
    replace_bits(1u, UINT32_C(0xf0), (a & 15u) << 4u);
    replace_bits(1u, UINT32_C(0x700), (b & 7u) << 8u);
    replace_bits(1u, UINT32_C(0x10000), (c & 1u) << 16u);
    replace_bits(1u, UINT32_C(0xc0000), (d & 3u) << 18u);
    replace_bits(1u, UINT32_C(0x600000), (e & 3u) << 21u);
    replace_bits(1u, UINT32_C(0x20000), (b > 2u ? 1u : 0u) << 17u);
    replace_bits(1u, UINT32_C(0x800), (f & 1u) << 11u);
    replace_bits(1u, UINT32_C(0x100000), 0u);
    replace_bits(1u, UINT32_C(0x4), 0u);
    replace_bits(1u, UINT32_C(0x8), 0u);
    replace_bits(1u, UINT32_C(0x40000000), UINT32_C(0x40000000));
    *audio_channels |= 4u;
}
