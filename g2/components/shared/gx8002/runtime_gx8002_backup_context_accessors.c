/* SPDX-License-Identifier: MIT */
/* Recovered backup context readers using the authenticated SDK field layout. */
#include "runtime_gx8002_backup_context_storage.h"
unsigned int backup_pcm_frames_per_context(void) { return backup_context_header.pcm_frame_num_per_context; }
unsigned int backup_pcm_frames_per_channel(void) { return backup_context_header.pcm_frame_num_per_channel; }
unsigned int backup_pcm_sample_rate(void) { return backup_context_header.sample_rate; }
unsigned int backup_context_count(void) { return backup_context_header.ctx_num; }
unsigned int backup_microphone_count(void) { return backup_context_header.mic_num; }
