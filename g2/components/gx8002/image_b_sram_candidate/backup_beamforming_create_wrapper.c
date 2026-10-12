/* Native 0x1000de40..0x1000de93. The public beamforming initializer
 * rearranges its integer and hard-float arguments before 0x1000ce14.
 * The body of that core remains a genuine separate source contract.
 */
#include <stdint.h>

extern void *gx8002_image_b_beamforming_core_1000ce14(
    int sample_rate, int mic_count, int angle_count, int linear,
    float elevation, float gain, float mic_distance, float mic_radius,
    int circular, float short_alpha, float long_alpha, int reserved,
    int output_count, const int *output_indices);

void *gx8002_image_b_beamforming_create_1000de40(
    int mic_count, int angle_count, int sample_rate, float gain,
    float subtraction_ratio, int subtraction_enabled, int linear,
    float mic_distance, int circular, float mic_radius, float elevation,
    float short_alpha, float long_alpha, int reserved, int output_count,
    const int *output_indices)
{
    /* Neither value is forwarded by the native 0xde40 wrapper. */
    (void)subtraction_ratio;
    (void)subtraction_enabled;
    return gx8002_image_b_beamforming_core_1000ce14(
        sample_rate, mic_count, angle_count, linear,
        elevation, gain, mic_distance, mic_radius,
        circular, short_alpha, long_alpha, reserved,
        output_count, output_indices);
}
