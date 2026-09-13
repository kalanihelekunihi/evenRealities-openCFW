/* SPDX-License-Identifier: MIT */
/* LvpGetLogfbankBuffer, using the pinned SDK context layout. */
#include <stdint.h>
#include <lvp_context.h>
void *open_cfw_gx8002_logfbank_index(LVP_CONTEXT *context, unsigned int index)
{
    LVP_CONTEXT_HEADER *header = context->ctx_header;
    unsigned int frame = (index * header->pcm_frame_num_per_context) %
                         header->logfbank_frame_num_per_channel;
    return (void *)((uintptr_t)header->logfbank_buffer +
                   frame * header->logfbank_dim_per_frame * sizeof(short));
}
