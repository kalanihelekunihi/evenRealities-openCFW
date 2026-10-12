/* Native GSC fallback linear-angle sweep 0x1000cae0..0x1000cb10.
 * The parent has allocated a positive-count angle vector. Native writes
 * zero first, accumulates fr10 once per later element, and runs vector sin
 * over the completed vector. This is a component, not the full GSC body.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);

void gx8002_image_b_angle_linear_sweep_verified_chunk(
    int32_t angle_count, float steering_radians,
    float *angle_vector, float *matrix)
{
    angle_vector[0]=0.0f;
    float current=0.0f;
    for (int32_t i=1; i<angle_count; ++i) {
        current=current+steering_radians;
        angle_vector[i]=current;
    }
    gx8002_image_b_sin_float_array_1000dee0(
        matrix,angle_vector,angle_count);
}
