/* Image-B IMCRA 0x10016090..0x10016260.  Two edge regions and one
 * weighted middle region update the flagged noise minimum, followed by
 * the persistent-minimum comparison at +0x84.
 */
#include <stdint.h>

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_flagged_smoothing_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    int32_t radius = (int32_t)word(state, 0x74u);
    int32_t end = bins - radius;
    float *minimum = (float *)(uintptr_t)word(state, 0x7cu);
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    const float *weights = (const float *)(uintptr_t)word(state, 0xacu);
    const uint32_t *flags = (const uint32_t *)(uintptr_t)word(state, 0xb4u);
    float alpha = *(const float *)(const void *)(state + 0x48u);
    float complement = 1.0f - alpha;
    if (radius > 0) {
        for (int32_t i = 0; i < radius; ++i) {
            float prior = minimum[i];
            float source = flags[i] != 0u ? energy[i] : prior;
            minimum[i] = alpha * prior + complement * source;
        }
    }
    if (radius < end) {
        for (int32_t i = radius; i < end; ++i) {
            float denominator = 0.0f;
            float numerator = 0.0f;
            for (int32_t j = 0; j <= radius * 2; ++j) {
                union { uint32_t bits; float value; } flag = {
                    .bits = flags[i - radius + j]
                };
                float selected = weights[j] * flag.value;
                denominator += selected;
                numerator += selected * energy[i - radius + j];
            }
            float prior = minimum[i];
            if (denominator != 0.0f)
                minimum[i] = complement * numerator / denominator + alpha * prior;
            else
                minimum[i] = alpha * prior + complement * prior;
        }
    }
    if (end < bins) {
        for (int32_t i = end; i < bins; ++i) {
            float prior = minimum[i];
            float source = flags[i] != 0u ? energy[i] : prior;
            minimum[i] = alpha * prior + complement * source;
        }
    }
    if (bins > 0) {
        float *persistent = (float *)(uintptr_t)word(state, 0x84u);
        for (int32_t i = 0; i < bins; ++i) {
            float current = minimum[i];
            if (persistent[i] < current)
                current = persistent[i];
            persistent[i] = current;
        }
    }
}
