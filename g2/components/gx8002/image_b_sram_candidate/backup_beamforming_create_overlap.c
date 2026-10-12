/* Native GSC create tail 0x1000d0ce..0x1000d160. The temporary buffer
 * accumulates squared 32-bit window samples shifted by 15 over overlapping
 * frames. A central range of it produces the inverse normalization table
 * with two binary32 32768 multiplications and round-toward-zero conversion.
 * The native product path uses stages=3, shift=256, frame=512. The caller
 * passes the source-owned free callback for the final temporary release.
 */
#include <stdint.h>

void gx8002_image_b_create_overlap_verified_chunk(
    const int32_t *window, int32_t *inverse, int32_t stages,
    int32_t shift, int32_t frame, int32_t *temporary,
    void (*release)(void *))
{
    for (int32_t stage=0; stage<stages+2; ++stage) {
        for (int32_t i=0; i<frame; ++i) {
            int32_t sample=window[i];
            temporary[stage*shift+i]+=(sample*sample)>>15;
        }
    }
    int32_t output_count=(int32_t)
        (((uint32_t)(stages+2)*(uint32_t)shift)-
         ((uint32_t)shift*2u));
    if (output_count>0) {
        const float scale=32768.0f; /* native 0x47000000 */
        for (int32_t i=0; i<output_count; ++i) {
            float quotient=scale/(float)temporary[shift+i];
            inverse[i]=(int32_t)(quotient*scale);
        }
    }
    release(temporary);
}
