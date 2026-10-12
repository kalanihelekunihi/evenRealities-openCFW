/* Alternate GSC angle sweep at native 0x1000ca88..0x1000cade.
 * The parent requires positive angle count; for each angle index the
 * source computes float(index)*steering_radians minus each microphone
 * position, then invokes the source-owned vector sin adapter.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);

void gx8002_image_b_angle_sweep_verified_chunk(
    int32_t angle_count, int32_t mic_count, float steering_radians,
    const float *positions, float *scratch, float *matrix)
{
    for (int32_t angle=0; angle<angle_count; ++angle) {
        float base=(float)angle*steering_radians;
        for (int32_t mic=0; mic<mic_count; ++mic)
            scratch[mic]=base-positions[mic];
        gx8002_image_b_sin_float_array_1000dee0(
            matrix+(uint32_t)angle*(uint32_t)mic_count,scratch,mic_count);
    }
}
