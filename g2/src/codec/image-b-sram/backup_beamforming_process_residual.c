/* Native process 0x1000d852..0x1000d8ce after the matrix leaves.
 * Divides each complex matrix output by ctx+0x04, subtracts the paired
 * reference matrix, stores binary32 residuals, then rounds toward zero into
 * the strided halfword result. The caller's band offset is explicit.
 */
#include <stdint.h>

void gx8002_image_b_process_residual_verified_chunk(
    const uint32_t *ctx, uint32_t band_byte_offset)
{
    int32_t modes=(int32_t)ctx[0x08/4];
    if (modes<=0) return;
    const float *matrix=(const float *)(uintptr_t)ctx[0xc8/4];
    const float *reference=(const float *)(uintptr_t)ctx[0xd0/4];
    float *residual=(float *)(uintptr_t)ctx[0x68/4];
    uintptr_t output=(uintptr_t)(ctx[0x90/4]+band_byte_offset);
    uint32_t stride=ctx[0x18/4]*4u;
    float divisor=(float)(int32_t)ctx[0x04/4];
    for (int32_t i=0;i<modes;++i) {
        float real=matrix[2*i]/divisor-reference[2*i];
        residual[2*i]=real;
        float imag=matrix[2*i+1]/divisor-reference[2*i+1];
        residual[2*i+1]=imag;
        int16_t *sample=(int16_t *)output;
        sample[0]=(int16_t)(int32_t)real;
        sample[1]=(int16_t)(int32_t)imag;
        output+=stride;
    }
}
