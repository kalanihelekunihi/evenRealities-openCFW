/* Image-B IMCRA 0x10015ff0..0x10016090: persistent minimum and flags.
 * Separate source chunk pending composition into the full process provider.
 */
#include <stdint.h>

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_minimum_flags_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    if (bins <= 0)
        return;
    float *persistent = (float *)(uintptr_t)word(state, 0x80u);
    const float *smoothed = (const float *)(uintptr_t)word(state, 0x78u);
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    uint32_t *flags = (uint32_t *)(uintptr_t)word(state, 0xb4u);
    float threshold_a = *(const float *)(const void *)(state + 0x4cu);
    float threshold_b = *(const float *)(const void *)(state + 0x50u);
    float activation = *(const float *)(const void *)(state + 0x58u);
    for (int32_t i = 0; i < bins; ++i) {
        float current = smoothed[i];
        float previous = persistent[i];
        if (previous < current)
            current = previous;
        persistent[i] = current;
    }
    for (int32_t i = 0; i < bins; ++i) {
        float base = persistent[i] * threshold_a;
        float threshold = base * threshold_b;
        uint32_t active = 0u;
        if (energy[i] < threshold) {
            float scaled = base * activation;
            if (smoothed[i] < scaled)
                active = UINT32_C(0x3f800000);
        }
        flags[i] = active;
    }
}
