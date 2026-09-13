/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
#include <gx_audio_in/gx_audio_in_v2.h>
_Static_assert(offsetof(GX_AUDIO_IN_FFTVAD_STATE,vad_state_index)==12,"FFTVAD state ABI");
/* Recovered package 0xdd08. Preserve high/middle/low register read order. */
int open_cfw_gx8002_audio_fftvad_state(GX_AUDIO_IN_FFTVAD_STATE *state)
{
    if (!state) return -1;
    volatile GX_AUDIO_IN_FFTVAD_STATE *output=state;
    volatile uint32_t *registers=(volatile uint32_t *)(uintptr_t)0xa0a00000u;
    output->vad_state_h=registers[0x174/4];
    output->vad_state_m=registers[0x178/4];
    output->vad_state_l=registers[0x17c/4];
    output->vad_state_index=(registers[0x10c/4]>>16)&127u;
    return 0;
}
