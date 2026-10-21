/* Native process 0x1000d94c..0x1000da9c. The stock body is explicitly
 * unrolled for at most fourteen binary32 coefficients and exits after each
 * pair when 2*(ctx+0x04-1) falls below the next odd bound. The scratch
 * values are the actual preceding e004 block-dot outputs at stack+0x74.
 */
#include <stdint.h>

void gx8002_image_b_process_coeff_update_verified_chunk(
    const uint32_t *ctx, uint32_t coefficient_selection_byte_offset,
    const float complex_scratch[14], float scale)
{
    int32_t pairs=(int32_t)ctx[0x04/4]-1;
    if (pairs<=0) return;
    float *coeff=(float *)(uintptr_t)
        (ctx[0xc4/4]+coefficient_selection_byte_offset);
    int32_t words=pairs*2;
    if (words>14) words=14;
    for (int32_t i=0;i<words;++i)
        coeff[i]=coeff[i]+scale*complex_scratch[i];
}
