/* Native process 0x1000d924..0x1000d94c. The caller's stack+0x74
 * complex scratch is supplied explicitly. d930 uses stack+0x18, which was
 * initialized at d4a0 to ctx+0x04 minus one; its block-dot fifth argument
 * is ctx+0x08 from d928. The scale is fr8 (0x3c23d70a) divided by the
 * observed energy slot, without a zero denominator guard.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_process_scale_word;
extern void gx8002_image_b_complex_block_dot_1000e004(
    float *,const float *,const float *,int32_t,int32_t);

float gx8002_image_b_process_block_scale_verified_chunk(
    const uint32_t *ctx, uint32_t energy_slot_byte_offset,
    float *complex_scratch)
{
    const float *residual=(const float *)(uintptr_t)ctx[0x68/4];
    int32_t output_blocks=(int32_t)ctx[0x04/4]-1;
    int32_t complex_pairs=(int32_t)ctx[0x08/4];
    gx8002_image_b_complex_block_dot_1000e004(
        complex_scratch,residual,residual,output_blocks,complex_pairs);
    const float *energy=(const float *)(uintptr_t)
        (ctx[0xb8/4]+energy_slot_byte_offset);
    const gx8002_process_scale_word numerator={.u=UINT32_C(0x3c23d70a)};
    return numerator.f/(*energy);
}
