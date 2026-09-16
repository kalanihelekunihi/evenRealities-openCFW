/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_BACKUP_CONTEXT_STORAGE_H
#define OPEN_CFW_GX8002_BACKUP_CONTEXT_STORAGE_H
#include <lvp_context.h>
enum {
    BACKUP_FRAME_SAMPLES = 256,
    BACKUP_FRAMES_PER_CHANNEL = 12,
    BACKUP_MIC_CHANNELS = 2,
    BACKUP_CONTEXT_COUNT = 4,
    BACKUP_CONTEXT_BYTES = 32 + 2784
};
extern LVP_CONTEXT_HEADER backup_context_header;
extern unsigned char backup_context_frames[BACKUP_CONTEXT_COUNT][BACKUP_CONTEXT_BYTES];
extern short backup_output_samples[BACKUP_FRAME_SAMPLES * BACKUP_FRAMES_PER_CHANNEL];
extern short backup_microphone_samples[BACKUP_FRAME_SAMPLES * BACKUP_FRAMES_PER_CHANNEL * BACKUP_MIC_CHANNELS];
#endif
