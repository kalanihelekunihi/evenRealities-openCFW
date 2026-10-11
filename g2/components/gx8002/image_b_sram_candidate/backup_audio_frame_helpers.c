/* SPDX-License-Identifier: MIT
 * Image-B 0x10009ec0 and 0x10009f08..0x10009fa8 frame calculations.
 */
#include <stdint.h>

static volatile uint32_t *const audio_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20017700);

uint32_t gx8002_image_b_mic_frame_10009ec0(
    const uint32_t *frame_state, uint32_t channel, uint32_t sample)
{
    const uint32_t *const state =
        (const uint32_t *)(uintptr_t)frame_state[0];
    uint32_t period = state[0x3cu / 4u];
    uint32_t remainder = frame_state[2] -
        (frame_state[2] / period) * period;
    uint32_t offset = sample + channel * state[0x28u / 4u] +
                      remainder * state[0x24u / 4u];
    uint32_t sample_bytes =
        (state[0x20u / 4u] * state[0x1cu / 4u]) / 1000u;
    return state[0x50u / 4u] + offset * (sample_bytes * 2u);
}

uint32_t gx8002_image_b_audio_frame_buffer_address_10009f08(void)
{
    return UINT32_C(0x2001bb80);
}

uint32_t gx8002_image_b_audio_word_24_10009f50(void)
{
    return audio_state[0x24u / 4u];
}

uint32_t gx8002_image_b_audio_sample_bytes_10009f5c(void)
{
    return (audio_state[0x1cu / 4u] * audio_state[0x20u / 4u]) / 1000u;
}

uint32_t gx8002_image_b_audio_word_28_10009f74(void)
{
    return audio_state[0x28u / 4u];
}

uint32_t gx8002_image_b_audio_word_20_10009f80(void)
{
    return audio_state[0x20u / 4u];
}

uint32_t gx8002_image_b_audio_one_10009f8c(void)
{
    return 1u;
}

uint32_t gx8002_image_b_audio_word_3c_10009f90(void)
{
    return audio_state[0x3cu / 4u];
}

uint32_t gx8002_image_b_audio_word_08_10009f9c(void)
{
    return audio_state[0x08u / 4u];
}

void gx8002_image_b_audio_frame_set_10009fa8(
    uint32_t *frame, uint32_t value, int32_t count, int32_t unit)
{
    frame[4] = (uint32_t)unit;
    frame[2] = value;
    frame[3] = (uint32_t)unit * (uint32_t)(count / unit);
    frame[0] = 0u;
    frame[1] = 0u;
}
