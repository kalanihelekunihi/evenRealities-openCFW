/* Image-B IMCRA 0x10015ee8..0x10015ff0: three-region running minimum.
 * This is a source chunk, not a replacement for the complete 0x10015d34
 * provider.  The middle region uses the native inclusive 2*radius+1
 * weighted window; the edge regions use the unweighted energy vector.
 */
#include <stdint.h>

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_minimum_smoothing_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    int32_t radius = (int32_t)word(state, 0x74u);
    float *minimum = (float *)(uintptr_t)word(state, 0x78u);
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    const float *weights = (const float *)(uintptr_t)word(state, 0xacu);
    float alpha = *(const float *)(const void *)(state + 0x48u);
    float complement = 1.0f - alpha;
    if (radius > 0) {
        for (int32_t i = 0; i < radius; ++i)
            minimum[i] = alpha * minimum[i] + complement * energy[i];
    }
    int32_t end = bins - radius;
    if (radius < end) {
        for (int32_t i = radius; i < end; ++i) {
            float sum = 0.0f;
            for (int32_t j = 0; j <= radius * 2; ++j)
                sum += weights[j] * energy[i - radius + j];
            minimum[i] = complement * sum + alpha * minimum[i];
        }
    }
    if (end < bins) {
        for (int32_t i = end; i < bins; ++i)
            minimum[i] = alpha * minimum[i] + complement * energy[i];
    }
}
