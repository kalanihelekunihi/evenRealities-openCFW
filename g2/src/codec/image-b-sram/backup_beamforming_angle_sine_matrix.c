/* Zero-mode GSC angle body 0x1000c8ae..0x1000c90c. For each configured
 * angle, subtract every microphone position, then call the source-owned
 * vector sin adapter at 0x1000dee0. The allocation-failure and count
 * branches are handled by the eventual full angle composer.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);

void gx8002_image_b_angle_sine_matrix_verified_chunk(
    const float *radians, int32_t angle_count, const float *positions,
    int32_t mic_count, float *scratch, float *matrix)
{
    for (int32_t angle=0; angle<angle_count; ++angle) {
        if (mic_count>0) {
            for (int32_t mic=0; mic<mic_count; ++mic)
                scratch[mic]=radians[angle]-positions[mic];
        }
        gx8002_image_b_sin_float_array_1000dee0(
            matrix + (uint32_t)angle*(uint32_t)mic_count, scratch, mic_count);
    }
}
