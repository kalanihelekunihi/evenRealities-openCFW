/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020502c channel selector. Exact 12-byte
 * source table at 0x1020a9a4; direct C-SKY confirms three ordered
 * volatile writes to playback register 0xa0b00014.
 */
#include <stdint.h>

static const uint8_t channel_bits[12] = {
    0u, 0u, 1u, 0u,
    1u, 0u, 1u, 1u,
    0u, 0u, 0u, 1u
};

uint32_t gx8002_xip_aout_set_channel_1020502c(
    uint32_t unused, uint32_t channel)
{
    (void)unused;
    uint32_t high = 0u, middle = 0u, low = 0u;
    if (channel < 4u) {
        high = channel_bits[channel];
        middle = channel_bits[4u + channel];
        low = channel_bits[8u + channel];
    }
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00014);
    *control = (*control & ~UINT32_C(0x0f00)) |
               ((high << 8u) & UINT32_C(0x0f00));
    *control = (*control & ~UINT32_C(0xf000)) |
               ((middle << 12u) & UINT32_C(0xffff));
    *control = (*control & ~UINT32_C(1)) | (low & 1u);
    return 0u;
}
