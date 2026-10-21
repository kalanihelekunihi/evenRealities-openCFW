/* Native zero-mode angle path 0x1000c868..0x1000c8a4. This fills the
 * sixth allocated vector, preserving native writes to entries zero and one
 * even when mic_count is less than two. Full angle core remains unprovided.
 */
#include <stdint.h>

float gx8002_image_b_angle_spacing_verified_chunk(
    uint32_t mic_count, float distance, float increment, float *positions)
{
    const float two_pi=0x1.921fb6p+2f; /* native 0x40c90fdb */
    float step=two_pi/(float)(int32_t)mic_count;
    positions[0]=0.0f;
    float scaled=distance*increment;
    positions[1]=step;
    for (uint32_t i=2; i<mic_count; ++i)
        positions[i]=(float)(int32_t)i*step;
    return scaled; /* native fr8 at 0x1000c87c */
}
