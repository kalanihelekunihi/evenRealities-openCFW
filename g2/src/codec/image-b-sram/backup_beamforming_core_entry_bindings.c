/* Native entry ABIs at 0x1000c6e8 and 0x1000ce14. The complete C
 * reconstructions retain external runtime RAM contracts in their bodies. */
#include <stdint.h>

extern int gx8002_image_b_beamforming_angles_whole_candidate(
    void *state, int angle_count, const int16_t *degrees);

int gx8002_image_b_beamforming_angles_1000c6e8(
    void *state, int angle_count, const int16_t *degrees)
{
    return gx8002_image_b_beamforming_angles_whole_candidate(
        state, angle_count, degrees);
}

extern void *gx8002_image_b_beamforming_core_whole_candidate(
    int sample_rate, int mic_count, int angle_count, int linear,
    float elevation, float gain, float mic_distance, float mic_radius,
    int circular, float short_alpha, float long_alpha, int reserved,
    int output_count, const int *output_indices);

void *gx8002_image_b_beamforming_core_1000ce14(
    int sample_rate, int mic_count, int angle_count, int linear,
    float elevation, float gain, float mic_distance, float mic_radius,
    int circular, float short_alpha, float long_alpha, int reserved,
    int output_count, const int *output_indices)
{
    return gx8002_image_b_beamforming_core_whole_candidate(
        sample_rate, mic_count, angle_count, linear, elevation, gain,
        mic_distance, mic_radius, circular, short_alpha, long_alpha,
        reserved, output_count, output_indices);
}
