/* SPDX-License-Identifier: MIT */
/* Backup _LvpAudioInRecordCallback, identified against NationalChip
 * lvp/lvp_mode_denoise.c at 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * This describes only fields accessed by this callback, not complete types. */
#include <stdint.h>
#include <stddef.h>
struct callback_header {
    uint32_t prefix[2];
    uint32_t mic_num;
    uint32_t middle[4];
    uint32_t frame_length, sample_rate, pcm_frame_num_per_context;
};
struct callback_context {
    volatile struct callback_header *header;
    uint32_t other;
    uint32_t ctx_index;
};
_Static_assert(offsetof(struct callback_header, mic_num)==8,"microphone count");
_Static_assert(offsetof(struct callback_header, pcm_frame_num_per_context)==36,"frames");
_Static_assert(offsetof(struct callback_header, frame_length)==28,"frame length");
_Static_assert(offsetof(struct callback_header, sample_rate)==32,"sample rate");
_Static_assert(offsetof(struct callback_context, ctx_index)==8,"context index");
extern void backup_get_context(uint32_t, volatile struct callback_context **, uint32_t *);
extern void *backup_get_mic_frame(volatile struct callback_context *, uint32_t, uint32_t);
extern void backup_dcache_invalid_range(void *, uint32_t);
extern int backup_queue_put(void *, const void *);
extern unsigned char backup_denoise_state[];
int open_cfw_gx8002_backup_denoise_record_callback(uint32_t index, void *priv)
{
    (void)priv;
    volatile struct callback_context *context;
    uint32_t context_size;
    backup_get_context(index, &context, &context_size);
    volatile struct callback_header *header=context->header;
    context->ctx_index=index;
    uint32_t length=header->frame_length;
    uint32_t frames=header->pcm_frame_num_per_context;
    uint32_t samples=length*frames;
    samples*=header->sample_rate;
    samples/=1000u;
    if (header->mic_num) {
        uint32_t bytes=samples*2u;
        uint32_t mic=0;
        do {
            void *buffer=backup_get_mic_frame(context,mic,0);
            backup_dcache_invalid_range(buffer,bytes);
        } while (++mic<header->mic_num);
    }
    backup_queue_put(backup_denoise_state+28,&context);
    return 0;
}
