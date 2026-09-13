/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t channel:4, reserved:28; } input_channel_register;

/* Recovered package0xd4fc. Other source selectors intentionally do nothing. */
int open_cfw_gx8002_audio_input_channel(GX_AUDIO_IN_SOURCE source,uint32_t left,uint32_t right)
{
    if (source==AUDIO_IN_I2S) {
        ((volatile input_channel_register *)(uintptr_t)0xa0a00048u)->channel=left;
        ((volatile input_channel_register *)(uintptr_t)0xa0a0004cu)->channel=right;
    } else if (source==AUDIO_IN_PDM) {
        ((volatile input_channel_register *)(uintptr_t)0xa0a00028u)->channel=left;
        ((volatile input_channel_register *)(uintptr_t)0xa0a0002cu)->channel=right;
    }
    return 0;
}
