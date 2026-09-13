/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t reserved0:4, gain:4, reserved1:24; } rough_gain_register;
/* Recovered package 0xd938. Raw gain codes narrow to four bits. */
int open_cfw_gx8002_audio_rough_gain(GX_AUDIO_IN_SOURCE source,GX_AUDIO_IN_GAIN gain)
{
    volatile rough_gain_register *registers=(volatile rough_gain_register *)(uintptr_t)0xa0a00000u;
    if (source==AUDIO_IN_SADC) registers[3].gain=gain;
    else if (source==AUDIO_IN_PDM) {
        registers[10].gain=gain;
        registers[11].gain=gain;
    } else if (source==AUDIO_IN_I2S) {
        registers[18].gain=gain;
        registers[19].gain=gain;
    }
    return 0;
}
