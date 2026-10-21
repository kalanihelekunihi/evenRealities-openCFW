/* SPDX-License-Identifier: MIT
 * Native XIP 0x10203dc8 and 0x10203fa8. The original NationalChip
 * API receives GX_AUDIO_IN_OUTPUT_PCM by value; its six words occupy
 * r1-r3 and three stack slots after the channel argument.
 */
#include <stdint.h>
#include "resident_xip_audio_output_types.h"

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const active =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027334);

static void replace_bits(volatile uint32_t *reg, uint32_t mask, uint32_t bits)
{
    *reg = (*reg & ~mask) | (bits & mask);
}

uint32_t gx8002_xip_pcm_channel_setting_10203dc8(
    uint32_t index, uint32_t left, uint32_t right,
    uint32_t size, uint32_t frames)
{
    if ((size & 127u) != 0u || ((left | right) & 7u) != 0u)
        return UINT32_MAX;
    volatile uint32_t *bank = ain + (index * 0x24u) / 4u;
    bank[0x110u / 4u] = frames;
    bank[0x114u / 4u] = left;
    bank[0x11cu / 4u] = right;
    bank[0x120u / 4u] = size;
    ain[0x104u / 4u] = 1u << (index + 11u);
    return 0u;
}

int32_t gx8002_xip_audio_output_pcm_10203fa8(
    uint32_t channel, gx8002_pcm_output pcm)
{
    if (channel == 1u) {
        if (gx8002_xip_pcm_channel_setting_10203dc8(
                0u, pcm.left_buffer, pcm.right_buffer,
                pcm.size, pcm.frame_num) != 0u)
            return -1;
        volatile uint32_t *reg = &ain[0x108u / 4u];
        replace_bits(reg, 0x3u, pcm.source);
        replace_bits(reg, 0xcu, pcm.endian << 2u);
        replace_bits(reg, 0x40u, 0x40u);
        replace_bits(reg, 0x80u, 0u);
        replace_bits(reg, 0x20u, 0x20u);
    } else if (channel == 2u) {
        if (gx8002_xip_pcm_channel_setting_10203dc8(
                1u, pcm.left_buffer, pcm.right_buffer,
                pcm.size, pcm.frame_num) != 0u)
            return -1;
        volatile uint32_t *reg = &ain[0x108u / 4u];
        replace_bits(reg, 0x300u, pcm.source << 8u);
        replace_bits(reg, 0xc00u, pcm.endian << 10u);
        replace_bits(reg, 0x4000u, 0x4000u);
        replace_bits(reg, 0x8000u, 0u);
        replace_bits(reg, 0x2000u, 0x2000u);
    } else {
        return -1;
    }
    *active = *active | channel;
    return 0;
}
