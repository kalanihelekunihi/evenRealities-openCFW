/* Native GSC create angle defaults cfb0..cfd8 and d19c..d1e0.
 * Circular mode computes integer 360/count and a binary32 scalar from
 * context+0x54; linear mode computes 180/(count-1), except count one.
 * Native circular count zero executes signed divide by zero before any
 * later branch; no artificial default is inserted here.
 */
#include <stdint.h>

typedef union { uint32_t u; float f; } gx8002_create_angle_word;

void gx8002_image_b_create_angles_verified_chunk(
    uint32_t *ctx, int32_t linear, int32_t angle_count)
{
    float *angles=(float *)(uintptr_t)ctx[0xa8/4];
    if (linear==0) {
        ctx[0x20/4]=(uint32_t)(360/angle_count);
        gx8002_create_angle_word ratio={.u=UINT32_C(0x3f8ccccd)};
        float value=((float)(int32_t)ctx[0x54/4]/
                     (float)angle_count)*ratio.f;
        for (int32_t i=0; i<angle_count; ++i) angles[i]=value;
    } else {
        ctx[0x20/4]=(uint32_t)(angle_count==1 ? 0 :
                                180/(angle_count-1));
        gx8002_create_angle_word angle={.u=UINT32_C(0x40875c29)};
        for (int32_t i=0; i<angle_count; ++i) angles[i]=angle.f;
    }
}
