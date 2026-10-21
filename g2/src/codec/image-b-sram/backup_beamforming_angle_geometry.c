/* Decoded GSC angle arithmetic at native 0x1000c7ee..0x1000c834.
 * This is an independently compiled component of the still-open full angle
 * body. The target hard-float sin adapter is already source-owned at ded0.
 * Exact constants come from native literal words ca84, c800, and ca7c.
 */
#include <stdint.h>
#include "backup_beamforming_angle_work.h"

typedef union { uint32_t u; float f; } gx8002_bf_float_word;

extern float gx8002_image_b_sin_float_1000ded0(float x);

void gx8002_image_b_angle_geometry_verified_chunk(
    const uint32_t *ctx, struct gx8002_image_b_angle_geometry *out)
{
    gx8002_bf_float_word w={.u=ctx[0x28/4]};
    float sine=gx8002_image_b_sin_float_1000ded0(w.f);
    float ratio=(float)(int32_t)ctx[0]/(float)(int32_t)ctx[0x14/4];
    const float two_pi=0x1.921fb6p+2f; /* 0x40c90fdb */
    const float pi=0x1.921fb6p+1f;     /* 0x40490fdb */
    float increment=((ratio*two_pi)*sine)/340.0f; /* 0x43aa0000 */
    float steering=((float)(int32_t)ctx[0x30/4]*pi)/180.0f;
    if (ctx[0x30/4] != 0) {
        w.u=ctx[0x34/4];
        increment=-(increment*w.f);
    }
    out->increment=increment;
    out->steering_radians=steering;
}
