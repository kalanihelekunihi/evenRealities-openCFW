/* Native process 0x1000db5c..0x1000dba2 output preparation. The original
 * third register argument, saved at stack+0x58, selects the output frame;
 * it is passed explicitly. The pinned DSP clear/copy bodies retain native
 * halfword count and forward-copy overlap semantics.
 */
#include <stdint.h>

extern void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t value,int16_t *destination,uint32_t count);
extern void gx8002_image_b_dsp_copy_1000f180(
    const int16_t *source,int16_t *destination,uint32_t count);

uint32_t gx8002_image_b_process_output_prepare_verified_chunk(
    const uint32_t *ctx,uint32_t output_frame_index)
{
    uint32_t prefill=ctx[0x10/4]*ctx[0x08/4];
    uint32_t tail=ctx[0x0c/4]-ctx[0x10/4];
    uint32_t clear_count=prefill+tail;
    gx8002_image_b_dsp_clear_1000f1ac(
        0u,(int16_t *)(uintptr_t)ctx[0x88/4],clear_count);
    gx8002_image_b_dsp_copy_1000f180(
        (const int16_t *)(uintptr_t)ctx[0x80/4],
        (int16_t *)(uintptr_t)ctx[0x88/4],tail);
    return output_frame_index*prefill*2u;
}
