/* Native image-B GSC complex coefficient normalization c9be..ca38.
 * The caller supplies the destination selected from context+0xa4 plus
 * its live row offset. Native stores (1,0) first and uses frecips on the
 * first complex magnitude. CK804EF -O2 contracts the real/imag expressions
 * to fmacs/fmscs, the instructions present in the authenticated body.
 */
#include <stdint.h>

extern float gx8002_image_b_native_reciprocal_f32(float x);

void gx8002_image_b_angle_normalize_verified_chunk(
    const float *sines, const float *cosines, int32_t mic_count,
    float *complex_pairs)
{
    union { uint32_t u; float f; } one={.u=UINT32_C(0x3f800000)};
    complex_pairs[0]=one.f;
    complex_pairs[1]=0.0f;
    float sine0=sines[0], cosine0=cosines[0];
    float magnitude=cosine0*cosine0+sine0*sine0;
    float reciprocal=gx8002_image_b_native_reciprocal_f32(magnitude);
    for (int32_t mic=1; mic<mic_count; ++mic) {
        complex_pairs[mic*2]=
            (cosine0*cosines[mic]+sine0*sines[mic])*reciprocal;
        complex_pairs[mic*2+1]=
            (cosines[mic]*sine0-cosine0*sines[mic])*reciprocal;
    }
}
