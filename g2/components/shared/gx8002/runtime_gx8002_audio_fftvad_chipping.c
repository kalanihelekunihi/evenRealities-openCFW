/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
_Static_assert(sizeof(GX_AUDIO_IN_FFTVAD_CHIPPING)==8,"FFTVAD chipping ABI");
/* Recovered package 0xdcb8. Four separate full-word RMW operations. */
int open_cfw_gx8002_audio_fftvad_chipping(GX_AUDIO_IN_FFTVAD_CHIPPING config)
{
    volatile uint32_t *registers=(volatile uint32_t *)(uintptr_t)0xa0a00198u;
    union { uint32_t word; struct { uint32_t low:16, high:16; } fields; } value;
    value.word=registers[0]; value.fields.low=config.chipping_1; registers[0]=value.word;
    value.word=registers[0]; value.fields.high=config.chipping_2; registers[0]=value.word;
    value.word=registers[1]; value.fields.low=config.chipping_3; registers[1]=value.word;
    value.word=registers[1]; value.fields.high=config.chipping_4; registers[1]=value.word;
    return 0;
}
