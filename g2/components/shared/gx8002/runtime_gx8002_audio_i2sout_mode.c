/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t reserved0:4, mode:1, reserved1:27; } i2sout_mode_register;
/* Recovered package 0xd8cc: raw enum values narrow to the low bit. */
int open_cfw_gx8002_audio_i2sout_mode(GX_AUDIO_IN_I2S_CLOCK_MODE mode)
{
    volatile i2sout_mode_register *control=(volatile i2sout_mode_register *)(uintptr_t)0xa0a00008u;
    control->mode=mode;
    return 0;
}
