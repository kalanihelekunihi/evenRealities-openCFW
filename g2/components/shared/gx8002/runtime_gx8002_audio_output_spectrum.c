/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
extern int open_cfw_gx8002_pcm_channel_setting(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern volatile uint32_t open_cfw_gx8002_audio_output_state;
typedef struct {
    uint32_t source0:2, endian0:2, reserved0:1, bit5:1, bit6:1, bit7:1;
    uint32_t source1:2, endian1:2, reserved1:1, bit13:1, bit14:1, bit15:1;
    uint32_t spectrum_source:3, reserved2:13;
} pcm_output_register;
_Static_assert(sizeof(GX_AUDIO_IN_OUTPUT_SPECTRUM)==20,"Spectrum output ABI");

/* Recovered package0xd6b8. Preserve individual volatile field writes. */
int open_cfw_gx8002_audio_output_spectrum(GX_AUDIO_IN_CHANNEL channel,GX_AUDIO_IN_OUTPUT_SPECTRUM pcm)
{
    volatile pcm_output_register *output=(volatile pcm_output_register *)(uintptr_t)0xa0a00108u;
    output->spectrum_source=pcm.source;
    if ((pcm.size&127u) || (pcm.buffer&7u)) return -1;
    if (channel==AUDIO_IN_CHANNEL_PCM0) {
        (void)open_cfw_gx8002_pcm_channel_setting(0,pcm.buffer,0,pcm.size,pcm.frame_num*2u);
        output->source0=PCM_SOURCE_FSPEC;
        output->endian0=pcm.endian;
        output->bit6=1;
        output->bit7=0;
        output->bit5=1;
    } else if (channel==AUDIO_IN_CHANNEL_PCM1) {
        (void)open_cfw_gx8002_pcm_channel_setting(1,pcm.buffer,0,pcm.size,pcm.frame_num*2u);
        output->source1=PCM_SOURCE_FSPEC;
        output->endian1=pcm.endian;
        output->bit14=1;
        output->bit15=0;
        output->bit13=1;
    } else return -1;
    open_cfw_gx8002_audio_output_state|=(uint32_t)channel;
    return 0;
}
