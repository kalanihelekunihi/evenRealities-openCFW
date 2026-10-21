/* Experimental composition of native 0x1000d6b6..0x1000dd44 after
 * threshold/ring setup. It carries original r1/r3 through the frame loop
 * and uses db86's new stack+0x18 lifetime for caller-output placement.
 * Whole-entry numerical/state equivalence remains unqualified.
 */
#include <stdint.h>

extern void gx8002_image_b_process_frame_loop_experimental(
    const uint32_t *);
extern uint32_t gx8002_image_b_process_output_prepare_verified_chunk(
    const uint32_t *,uint32_t);
extern void gx8002_image_b_process_channel_loop_verified_chunk(
    const uint32_t *,volatile uint32_t *);
extern void gx8002_image_b_process_output_finish_verified_chunk(
    const uint32_t *,uint8_t *,uint32_t);

void gx8002_image_b_process_post_ring_experimental(
    const uint32_t *ctx,uint8_t *caller_output,
    uint32_t output_frame_index,
    volatile uint32_t *energy_first_use_word)
{
    gx8002_image_b_process_frame_loop_experimental(ctx);
    uint32_t output_frame_byte_offset=
        gx8002_image_b_process_output_prepare_verified_chunk(
            ctx,output_frame_index);
    gx8002_image_b_process_channel_loop_verified_chunk(
        ctx,energy_first_use_word);
    gx8002_image_b_process_output_finish_verified_chunk(
        ctx,caller_output,output_frame_byte_offset);
}
