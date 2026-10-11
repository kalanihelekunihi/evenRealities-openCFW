/* SPDX-License-Identifier: MIT
 * Image-B SDK audio I2S setters 0x1000588c/9c/ac. Native MOVIH 0xa0a0
 * and one read/modify/write per body establish the MMIO contract.
 */
#include <stdint.h>

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

int32_t gx8002_image_b_audio_i2s_clock_1000588c(uint32_t value)
{
    AUDIO_WORD(0u) = (AUDIO_WORD(0u) & UINT32_C(0xf8ffffff)) |
        ((value & 7u) << 24);
    return 0;
}

int32_t gx8002_image_b_audio_i2s_input_mode_1000589c(uint32_t value)
{
    AUDIO_WORD(4u) = (AUDIO_WORD(4u) & UINT32_C(0xfffeffff)) |
        ((value & 1u) << 16);
    return 0;
}

int32_t gx8002_image_b_audio_i2s_output_mode_100058ac(uint32_t value)
{
    AUDIO_WORD(8u) = (AUDIO_WORD(8u) & UINT32_C(0xffffffef)) |
        ((value & 1u) << 4);
    return 0;
}
