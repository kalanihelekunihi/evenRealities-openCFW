/* Native process 0x1000dba2..0x1000dcd4 channel loop. r5 begins at
 * ctx+0x90 and advances by 2*(ctx+0x18); r6 is a byte index into the
 * halfword per-channel tables, and r7 advances by 2*(ctx+0x10).
 * The first-use energy word remains an explicit RAM contract.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_process_channel_fft_verified_chunk(
    const uint32_t *,int16_t *,uint32_t,volatile uint32_t *);
extern void gx8002_image_b_process_overlap_add_verified_chunk(
    const uint32_t *,uint32_t);

void gx8002_image_b_process_channel_loop_verified_chunk(
    const uint32_t *ctx,volatile uint32_t *energy_first_use_word)
{
    uint32_t channels=ctx[0x08/4];
    if ((int32_t)channels<=0) return;
    uint32_t input=(uint32_t)ctx[0x90/4];
    uint32_t input_step=ctx[0x18/4]*2u;
    uint32_t destination_offset=0;
    uint32_t destination_step=ctx[0x10/4]*2u;
    for (uint32_t channel=0;channel<channels;++channel) {
        gx8002_image_b_process_channel_fft_verified_chunk(
            ctx,(int16_t *)(uintptr_t)input,channel,energy_first_use_word);
        gx8002_image_b_process_overlap_add_verified_chunk(
            ctx,destination_offset);
        input+=input_step;
        destination_offset+=destination_step;
    }
}
