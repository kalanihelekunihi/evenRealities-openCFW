/* SPDX-License-Identifier: MIT */
/* LvpGetMicFrame: upstream field definitions with explicit address arithmetic. */
#include <stdint.h>
#include <lvp_context.h>
short *open_cfw_gx8002_mic_frame(LVP_CONTEXT *context,
                                unsigned int channel, unsigned int frame)
{
    LVP_CONTEXT_HEADER *header = context->ctx_header;
    unsigned int samples = header->frame_length * header->sample_rate / 1000;
    unsigned int position = frame + channel * header->pcm_frame_num_per_channel +
        (context->ctx_index % header->ctx_num) * header->pcm_frame_num_per_context;
    return (short *)((uintptr_t)header->mic_buffer + position * samples * 2);
}
