/* SPDX-License-Identifier: MIT */
/* Recovered LvpInitBuffer using the pinned SDK context layout. */
#include <stddef.h>
#include <lvp_context.h>
extern void *memset(void *, int, size_t);
_Static_assert(sizeof(LVP_CONTEXT_HEADER) == 120, "Context header ABI");
int open_cfw_gx8002_buffer_initialize(void)
{
    volatile LVP_CONTEXT_HEADER *header = (void *)0x20027b60;
    memset((void *)header, 0, 120);
    memset((void *)0x20027be0, 0, 25536);
    memset((void *)0x20030000, 0, 1040);
    header->logfbank_buffer = (short *)0x20032210;
    header->logfbank_buffer_size = 3840;
    header->logfbank_frame_num_per_channel = 48;
    header->frame_length = 10;
    header->sample_rate = 16000;
    header->pcm_frame_num_per_context = 4;
    header->pcm_frame_num_per_channel = 12;
    header->logfbank_dim_per_frame = 40;
    header->version = LVP_CONTEXT_VERSION;
    header->mic_num = 2;
    header->fft_dim_per_frame = 256;
    header->mic_buffer = (short *)0x20030410;
    header->snpu_buffer_size = 8480;
    header->mic_buffer_size = 7680;
    header->ctx_size = 8512;
    header->ref_num = 0;
    header->ref_buffer = 0;
    header->ref_buffer_size = 0;
    header->fft_num = 0;
    header->fft_buffer = 0;
    header->fft_buffer_size = 0;
    header->fft_frame_num_per_channel = 0;
    header->logfbank_num = 1;
    header->out_num = 0;
    header->out_buffer = 0;
    header->out_buffer_size = 0;
    header->out_frame_num_per_channel = 0;
    header->ctx_buffer = (void *)0x20027be0;
    header->ctx_num = 3;
    header->fft_vad_en = 1;
    return 0;
}
