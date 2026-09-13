/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
extern volatile uint32_t open_cfw_gx8002_audio_output_state;
typedef struct {
    uint32_t reserved0:16, source:3, endian:2, bit21:1, bit22:1, bit23:1, reserved1:8;
} logfbank_output_register;
_Static_assert(sizeof(GX_AUDIO_IN_OUTPUT_LOGFBANK)==20,"Logfbank output ABI");

/* Recovered package 0xd60c. frame_num must be nonzero; the original
 * performs an unsigned hardware division without a zero guard. */
int open_cfw_gx8002_audio_output_logfbank(GX_AUDIO_IN_OUTPUT_LOGFBANK config)
{
    volatile uint32_t *registers=(volatile uint32_t *)(uintptr_t)0xa0a00000u;
    volatile logfbank_output_register *output=(volatile logfbank_output_register *)(registers+66);
    if ((config.buffer&7u) || config.size%80u || config.size%config.frame_num) return -1;
    output->endian=config.endian;
    output->source=config.source;
    registers[87]=config.frame_num;
    registers[88]=config.buffer&~7u;
    registers[89]=config.size;
    registers[65]=1u<<13;
    output->bit22=1;
    output->bit23=0;
    output->bit21=1;
    open_cfw_gx8002_audio_output_state|=4u;
    return 0;
}
