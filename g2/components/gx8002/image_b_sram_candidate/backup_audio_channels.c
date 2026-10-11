/* SPDX-License-Identifier: MIT
 * Image-B audio channel controls, native 0x100058bc and 0x10005920.
 * C-SKY MOVIH 0xa0a0 in both bodies establishes the physical register base.
 */
#include <stdint.h>

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

static void set_channel_field(uint32_t offset, uint32_t mask, uint32_t value)
{
    AUDIO_WORD(offset) = (AUDIO_WORD(offset) & ~mask) | value;
}

uint32_t gx8002_image_b_channel_rate_10005840(uint32_t rate)
{
    /* Five typed correction values at stock 0x10012aac. */
    static const uint8_t rate_correction[5] = {5u, 10u, 15u, 20u, 25u};
    uint32_t quotient = rate / 6u;
    uint32_t index = quotient - 4u;
    uint32_t correction = index < 5u ? rate_correction[index] : 0u;
    uint32_t field = ((rate % 6u) + quotient + correction) & 63u;
    set_channel_field(0x1a4u, 63u, field);
    AUDIO_WORD(0x1a0u) = AUDIO_WORD(0x1a0u) | UINT32_C(0x80000000);
    return 0u;
}

uint32_t gx8002_image_b_channel_polarity_100058bc(uint32_t channel, uint32_t enabled)
{
    uint32_t value = (enabled == 0u) ? UINT32_C(0x100) : 0u;
    if (channel == 1u) {
        set_channel_field(0x0cu, 0x100u, value);
    } else if (channel == 2u) {
        set_channel_field(0x28u, 0x100u, value);
        set_channel_field(0x2cu, 0x100u, value);
    } else if (channel == 4u) {
        set_channel_field(0x48u, 0x100u, value);
        set_channel_field(0x4cu, 0x100u, value);
    }
    return 0u;
}

uint32_t gx8002_image_b_channel_gain_10005920(uint32_t channel, uint32_t gain)
{
    uint32_t value = (gain & 15u) << 4;
    if (channel == 1u) {
        set_channel_field(0x0cu, 0xf0u, value);
    } else if (channel == 2u) {
        set_channel_field(0x28u, 0xf0u, value);
        set_channel_field(0x2cu, 0xf0u, value);
    } else if (channel == 4u) {
        set_channel_field(0x48u, 0xf0u, value);
        set_channel_field(0x4cu, 0xf0u, value);
    }
    return 0u;
}
