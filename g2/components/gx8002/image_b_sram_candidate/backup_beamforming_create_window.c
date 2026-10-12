/* Native GSC create window d03c..d09e. The loop uses the source-owned
 * float sin child, literal binary32 constants 2π, 0.46, 0.54, 32768,
 * and round-toward-zero conversion before storing each 32-bit sample.
 * No host libm or guessed window table is used.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_window_word;
extern float gx8002_image_b_sin_float_1000ded0(float x);

void gx8002_image_b_create_window_verified_chunk(
    int32_t sample_count, int32_t *window)
{
    gx8002_window_word two_pi={.u=UINT32_C(0x40c90fdb)};
    gx8002_window_word sine_weight={.u=UINT32_C(0x3eeb851f)};
    gx8002_window_word base={.u=UINT32_C(0x3f0a3d71)};
    gx8002_window_word scale={.u=UINT32_C(0x47000000)};
    float step=two_pi.f/(float)sample_count;
    for (int32_t i=0; i<sample_count; ++i) {
        float sine=gx8002_image_b_sin_float_1000ded0((float)i*step);
        float value=(base.f-sine*sine_weight.f)*scale.f;
        window[i]=(int32_t)value;
    }
}
