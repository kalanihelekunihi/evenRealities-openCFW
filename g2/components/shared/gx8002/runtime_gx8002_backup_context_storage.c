/* SPDX-License-Identifier: MIT */
/* Recovered backup layout: 16 kHz, 16 ms frames, two microphone channels. */
#include "runtime_gx8002_backup_context_storage.h"
#define STORAGE(name) __attribute__((section(".bss.backup_" name), aligned(16)))
LVP_CONTEXT_HEADER backup_context_header STORAGE("context_header");
/* Each context has a 32-byte header and 2784 bytes of processing storage. */
unsigned char backup_context_frames[BACKUP_CONTEXT_COUNT][BACKUP_CONTEXT_BYTES] STORAGE("context_frames");
short backup_output_samples[BACKUP_FRAME_SAMPLES * BACKUP_FRAMES_PER_CHANNEL] STORAGE("output_samples");
short backup_microphone_samples[BACKUP_FRAME_SAMPLES * BACKUP_FRAMES_PER_CHANNEL * BACKUP_MIC_CHANNELS] STORAGE("microphone_samples");
_Static_assert(sizeof(LVP_CONTEXT_HEADER) == 120, "header ABI");
_Static_assert(sizeof(backup_context_frames) == 11264, "context storage");
_Static_assert(sizeof(backup_output_samples) == 6144, "output storage");
_Static_assert(sizeof(backup_microphone_samples) == 12288, "microphone storage");
