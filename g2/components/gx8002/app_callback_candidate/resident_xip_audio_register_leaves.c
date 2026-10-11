/* SPDX-License-Identifier: MIT
 * Native AIN register setters 0x10204320/30/50/ac.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

uint32_t gx8002_xip_audio_set_i2s_clock_10204320(uint32_t clock)
{
    ain[0] = (ain[0] & UINT32_C(0xf8ffffff)) | ((clock & 7u) << 24u);
    return 0u;
}

uint32_t gx8002_xip_audio_set_i2sin_mode_10204330(uint32_t mode)
{
    ain[1] = (ain[1] & UINT32_C(0xfffeffff)) | ((mode & 1u) << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_set_dc_enable_10204350(
    uint32_t channel, uint32_t enabled)
{
    uint32_t bit = enabled == 0u ? 1u : 0u;
    if (channel == 1u) {
        ain[0x0cu / 4u] = (ain[0x0cu / 4u] & ~UINT32_C(0x100)) | (bit << 8u);
    } else if (channel == 2u || channel == 4u) {
        uint32_t first = channel == 2u ? 0x28u / 4u : 0x48u / 4u;
        ain[first] = (ain[first] & ~UINT32_C(0x100)) | (bit << 8u);
        ain[first + 1u] = (ain[first + 1u] & ~UINT32_C(0x100)) | (bit << 8u);
    }
    return 0u;
}

uint32_t gx8002_xip_audio_set_rough_gain_102043ac(
    uint32_t channel, uint32_t gain)
{
    uint32_t bits = (gain & 15u) << 4u;
    if (channel == 1u) {
        ain[0x0cu / 4u] = (ain[0x0cu / 4u] & ~UINT32_C(0xf0)) | bits;
    } else if (channel == 2u || channel == 4u) {
        uint32_t first = channel == 2u ? 0x28u / 4u : 0x48u / 4u;
        ain[first] = (ain[first] & ~UINT32_C(0xf0)) | bits;
        ain[first + 1u] = (ain[first + 1u] & ~UINT32_C(0xf0)) | bits;
    }
    return 0u;
}
