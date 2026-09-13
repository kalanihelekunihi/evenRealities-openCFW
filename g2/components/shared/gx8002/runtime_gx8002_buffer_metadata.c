/* SPDX-License-Identifier: MIT */
/* Recovered Lvp buffer metadata using pinned SDK layout. */
#include <lvp_context.h>
#define HEADER ((volatile LVP_CONTEXT_HEADER *)0x20027b60)
_Static_assert(sizeof(LVP_CONTEXT_HEADER) == 120, "Context header ABI");
int open_cfw_gx8002_pcm_frames_per_context(void) { return HEADER->pcm_frame_num_per_context; }
int open_cfw_gx8002_pcm_frame_size(void)
{
    unsigned int rate = HEADER->sample_rate;
    unsigned int length = HEADER->frame_length;
    return rate * length / 1000;
}
int open_cfw_gx8002_logfbank_frames_per_channel(void) { return HEADER->logfbank_frame_num_per_channel; }
int open_cfw_gx8002_context_gap(void) { return 1; }
int open_cfw_gx8002_context_count(void) { return HEADER->ctx_num; }
int open_cfw_gx8002_mic_channel_count(void) { return HEADER->mic_num; }
