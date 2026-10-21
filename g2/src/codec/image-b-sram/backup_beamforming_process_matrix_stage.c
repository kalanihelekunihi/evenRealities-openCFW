/* Native process 0x1000d7f8..0x1000d8ce, using complete source-owned
 * matrix leaves at df38/e148/e0b8 and the separately verified residual.
 * The coefficient selection byte offset originates in the caller's earlier
 * band policy; no default mode or row is substituted here.
 */
#include <stdint.h>

extern void gx8002_image_b_complex_matrix_product_1000df38(
    float *,const float *,const float *,int32_t,int32_t,int32_t);
extern void gx8002_image_b_complex_rows_1000e148(
    float *,const float *,const float *,int32_t,int32_t,int32_t,int32_t);
extern void gx8002_image_b_complex_matrix_1000e0b8(
    float *,const float *,const float *,int32_t,int32_t,int32_t,int32_t);
extern void gx8002_image_b_process_residual_verified_chunk(
    const uint32_t *,uint32_t);

void gx8002_image_b_process_matrix_stage_verified_chunk(
    const uint32_t *ctx, uint32_t selected_coefficient_byte_offset,
    uint32_t coefficient_selection_byte_offset,
    uint32_t band_byte_offset)
{
    /* Native r6 at d80c/d846 is ctx+0x48, not the stack+0x18 word. */
    int32_t selected_columns=(int32_t)ctx[0x48/4];
    int32_t microphones=(int32_t)ctx[0x04/4];
    int32_t modes=(int32_t)ctx[0x08/4];
    gx8002_image_b_complex_matrix_product_1000df38(
        (float *)(uintptr_t)ctx[0xcc/4],
        (const float *)(uintptr_t)ctx[0xc0/4],
        (const float *)(uintptr_t)ctx[0x6c/4],
        selected_columns,microphones,modes);
    gx8002_image_b_complex_rows_1000e148(
        (float *)(uintptr_t)ctx[0xc8/4],
        (const float *)(uintptr_t)
            (ctx[0xa4/4]+selected_coefficient_byte_offset),
        (const float *)(uintptr_t)ctx[0x6c/4],
        microphones,1,microphones,modes);
    gx8002_image_b_complex_matrix_1000e0b8(
        (float *)(uintptr_t)ctx[0xd0/4],
        (const float *)(uintptr_t)(ctx[0xc4/4]+
                                   coefficient_selection_byte_offset),
        (const float *)(uintptr_t)ctx[0xcc/4],
        selected_columns,1,microphones,modes);
    gx8002_image_b_process_residual_verified_chunk(ctx,band_byte_offset);
}
