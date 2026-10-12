/* Native nonzero-mode angle branch 0x1000c83e..0x1000c85e. The caller
 * establishes mode!=0, ready!=0, and positive angle count. This copies
 * the signed-degree-derived radians into the first allocation before the
 * vector sin child writes the matrix allocation. The later branch at c862
 * remains part of the open complete GSC angle function.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);

void gx8002_image_b_angle_nonzero_mode_verified_chunk(
    const float *radians, uint32_t angle_count, float *angle_vector,
    float *matrix)
{
    for (uint32_t i=0; i<angle_count; ++i)
        angle_vector[i]=radians[i];
    gx8002_image_b_sin_float_array_1000dee0(
        matrix, angle_vector, (int)angle_count);
}
