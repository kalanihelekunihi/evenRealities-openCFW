/* SPDX-License-Identifier: MIT */
/* Backup LvpGetOutBuffer: four-slot layout and 512-byte PCM frames.
 * Preserve the inlined slot-zero initialization, even when output is off. */
#include "runtime_gx8002_backup_context_storage.h"
#include <stdint.h>
extern unsigned char backup_context_frames[BACKUP_CONTEXT_COUNT][BACKUP_CONTEXT_BYTES] __attribute__((aligned(16)));

void *open_cfw_gx8002_backup_get_out_buffer(unsigned index)
{
    volatile LVP_CONTEXT_HEADER *header=&backup_context_header;
    unsigned channels=header->out_num;
#ifdef __csky__
    /* The linker puts slot zero at header+128. Avoid a second address literal
     * while preserving the two ordered word writes. No encoded opcodes. */
    uintptr_t processing;
    __asm__ volatile ("addi %0, %1, 160\n\t"
                      "st.w %1, (%1, 128)\n\t"
                      "st.w %0, (%1, 144)"
        : "=&r" (processing)
        : "r" (header) : "memory");
#else
    volatile LVP_CONTEXT *context=(volatile LVP_CONTEXT *)backup_context_frames[0];
    context->ctx_header=&backup_context_header;
    context->snpu_buffer=backup_context_frames[0]+32;
#endif
    if (!channels)return (void *)0;
    unsigned frame_bytes=channels<<9;
    unsigned context_frames=header->pcm_frame_num_per_context;
    unsigned channel_frames=header->out_frame_num_per_channel;
    unsigned context_bytes=frame_bytes*context_frames;
    unsigned channel_bytes=frame_bytes*channel_frames;
    unsigned slots=channel_bytes/context_bytes;
    return (void *)((uintptr_t)header->out_buffer+(index%slots)*context_bytes);
}
