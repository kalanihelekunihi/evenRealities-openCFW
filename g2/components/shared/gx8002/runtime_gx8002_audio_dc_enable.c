/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t reserved0:8, bypass:1, reserved1:23; } dc_register;
/* Recovered package 0xd8dc. Hardware bypass is the inverse of enable. */
int open_cfw_gx8002_audio_dc_enable(GX_AUDIO_IN_SOURCE source,unsigned int enable)
{
    volatile dc_register *registers=(volatile dc_register *)(uintptr_t)0xa0a00000u;
    if (source==AUDIO_IN_SADC) registers[3].bypass=!enable;
    else if (source==AUDIO_IN_PDM) {
        registers[10].bypass=!enable;
        registers[11].bypass=!enable;
    } else if (source==AUDIO_IN_I2S) {
        registers[18].bypass=!enable;
        registers[19].bypass=!enable;
    }
    return 0;
}
