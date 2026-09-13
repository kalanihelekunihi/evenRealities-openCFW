/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t reserved0:8, w1:4, w2:4, w3:4, reserved1:12; } fftvad_weights;
_Static_assert(sizeof(GX_AUDIO_IN_FFTVAD_W)==3,"FFTVAD weights ABI");
/* Recovered package 0xdb80. Each byte narrows to a separate four-bit field. */
int open_cfw_gx8002_audio_fftvad_w(GX_AUDIO_IN_FFTVAD_W weights)
{
    volatile fftvad_weights *control=(volatile fftvad_weights *)(uintptr_t)0xa0a00158u;
    control->w1=weights.w1;
    control->w2=weights.w2;
    control->w3=weights.w3;
    return 0;
}
