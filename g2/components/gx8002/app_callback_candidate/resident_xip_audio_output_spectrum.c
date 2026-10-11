/* SPDX-License-Identifier: MIT
 * Native XIP 0x1020412c..0x10204221. The register's spectrum-source
 * field is written before validation; the PCM lower result is ignored
 * by the native body. The six-word call ABI is channel plus the five
 * GX_AUDIO_IN_OUTPUT_SPECTRUM words.
 */
#include <stdint.h>
#include "resident_xip_audio_output_types.h"

extern uint32_t gx8002_xip_pcm_channel_setting_10203dc8(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const active =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027334);

static void replace_bits(volatile uint32_t *reg, uint32_t mask, uint32_t bits)
{
    *reg = (*reg & ~mask) | (bits & mask);
}

int32_t gx8002_xip_audio_output_spectrum_1020412c(
    uint32_t channel, gx8002_spectrum_output output)
{
    volatile uint32_t *reg = &ain[0x108u / 4u];
    replace_bits(reg, 0x70000u, output.source << 16u);
    if ((output.size & 127u) != 0u || (output.buffer & 7u) != 0u)
        return -1;
    if (channel == 1u) {
        (void)gx8002_xip_pcm_channel_setting_10203dc8(
            0u, output.buffer, 0u, output.size, output.frame_num * 2u);
        replace_bits(reg, 0x3u, 3u);
        replace_bits(reg, 0xcu, output.endian << 2u);
        replace_bits(reg, 0x40u, 0x40u);
        replace_bits(reg, 0x80u, (output.buffer & 1u) << 7u);
        replace_bits(reg, 0x20u, 0x20u);
    } else if (channel == 2u) {
        (void)gx8002_xip_pcm_channel_setting_10203dc8(
            1u, output.buffer, 0u, output.size, output.frame_num * 2u);
        replace_bits(reg, 0x300u, 0x300u);
        replace_bits(reg, 0xc00u, output.endian << 10u);
        replace_bits(reg, 0x4000u, 0x4000u);
        replace_bits(reg, 0x8000u, (output.buffer & 1u) << 15u);
        replace_bits(reg, 0x2000u, 0x2000u);
    } else {
        return -1;
    }
    *active = *active | channel;
    return 0;
}
