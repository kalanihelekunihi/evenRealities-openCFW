/* SPDX-License-Identifier: MIT
 * Native AIN config leaves 0x10203f70, 0x102042d4, 0x10204570.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

uint32_t gx8002_xip_audio_set_input_channel_10203f70(
    uint32_t channel, uint32_t first, uint32_t second)
{
    uint32_t offset;
    if (channel == 4u) offset = 0x48u / 4u;
    else if (channel == 2u) offset = 0x28u / 4u;
    else return 0u;
    ain[offset] = (ain[offset] & ~UINT32_C(15)) | (first & 15u);
    ain[offset + 1u] = (ain[offset + 1u] & ~UINT32_C(15)) | (second & 15u);
    return 0u;
}

uint32_t gx8002_xip_audio_pga_gain_102042d4(uint32_t gain)
{
    static const uint8_t correction[5] = {5u, 10u, 15u, 20u, 25u};
    uint32_t quotient = gain / 6u;
    uint32_t index = quotient - 4u;
    uint32_t extra = index < 5u ? correction[index] : 0u;
    uint32_t result = (gain % 6u + quotient + extra) & 0x3fu;
    ain[0x1a4u / 4u] =
        (ain[0x1a4u / 4u] & ~UINT32_C(0x3f)) | result;
    ain[0x1a0u / 4u] |= UINT32_C(0x80000000);
    return 0u;
}

uint32_t gx8002_xip_audio_set_fftvad_enable_10204570(
    uint32_t enabled, uint32_t mode, uint32_t frames)
{
    uint32_t count = frames == 0u ? 0u : (frames - 1u) & 0xffu;
    ain[0x104u / 4u] = 0x20000u;
    ain[0x100u / 4u] =
        (ain[0x100u / 4u] & UINT32_C(0xfffcffff)) | UINT32_C(0x30000);
    uint32_t word = (ain[0x158u / 4u] & UINT32_C(0x3cffff80)) |
                    (count & 0x7fu) |
                    ((mode == 0u ? 1u : 0u) << 24u) |
                    ((enabled & 1u) << 25u) |
                    ((enabled & 1u) << 30u) |
                    ((enabled == 0u ? 1u : 0u) << 31u);
    ain[0x158u / 4u] = word;
    return 0u;
}
