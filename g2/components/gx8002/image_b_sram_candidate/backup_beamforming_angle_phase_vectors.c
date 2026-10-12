/* Native GSC angle inner phase transform 0x1000c970..0x1000c9b2.
 * The parent loops over matrix rows and supplies its live row pointer.
 * Native stack+0x0c is reset at 0x1000c936 and thereafter holds the frame
 * counter: fr1 = float(frame_index) * fr8, then each row element is scaled,
 * followed by the source-owned vector sin and cos adapters in that order.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);
extern void gx8002_image_b_cos_float_array_1000df0c(
    float *output, const float *input, int count);

void gx8002_image_b_angle_phase_vectors_verified_chunk(
    const float *matrix_row, int32_t mic_count, int32_t frame_index,
    float scaled_distance,
    float *scratch, float *sines, float *cosines)
{
    float phase_scale=(float)frame_index*scaled_distance;
    for (int32_t mic=0; mic<mic_count; ++mic)
        scratch[mic]=matrix_row[mic]*phase_scale;
    gx8002_image_b_sin_float_array_1000dee0(sines,scratch,mic_count);
    gx8002_image_b_cos_float_array_1000df0c(cosines,scratch,mic_count);
}
