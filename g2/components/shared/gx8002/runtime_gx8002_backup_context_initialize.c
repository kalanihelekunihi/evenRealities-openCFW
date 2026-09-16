/* SPDX-License-Identifier: MIT */
/* Backup LvpInitBuffer, recovered using the authenticated SDK context ABI. */
#include <stddef.h>
#include "runtime_gx8002_backup_context_storage.h"
extern void *memset(void *, int, size_t);
_Static_assert(sizeof(LVP_CONTEXT_HEADER) == 120, "Context header ABI");
int open_cfw_gx8002_backup_context_initialize(void)
{
    volatile LVP_CONTEXT_HEADER *h = &backup_context_header;
    memset((void *)h, 0, sizeof(*h));
    memset(backup_context_frames, 0, sizeof(backup_context_frames));
    h->version = LVP_CONTEXT_VERSION;
    h->mic_num = 2;
    h->mic_buffer = backup_microphone_samples;
    h->mic_buffer_size = sizeof(backup_microphone_samples);
    h->out_num = 1;
    h->out_buffer = backup_output_samples;
    h->out_buffer_size = sizeof(backup_output_samples);
    h->out_frame_num_per_channel = 12;
    h->pcm_frame_num_per_channel = 12;
    h->logfbank_dim_per_frame = 40;
    h->fft_dim_per_frame = 256;
    h->frame_length = 16;
    h->snpu_buffer_size = 2784;
    h->sample_rate = 16000;
    h->ctx_size = 2816;
    h->ref_num = 0;
    h->ref_buffer = 0;
    h->ref_buffer_size = 0;
    h->fft_num = 0;
    h->fft_buffer = 0;
    h->fft_buffer_size = 0;
    h->fft_frame_num_per_channel = 0;
    h->logfbank_num = 0;
    h->logfbank_buffer = 0;
    h->logfbank_buffer_size = 0;
    h->logfbank_frame_num_per_channel = 0;
    h->pcm_frame_num_per_context = 3;
    h->ctx_buffer = backup_context_frames;
    h->ctx_num = 4;
    h->fft_vad_en = 0;
    return 0;
}
