/* Image-B IMCRA 0x1001634c..0x10016404: noise estimate, running minima,
 * and periodic spectral-output decision.  The preceding gain-table writer
 * must have completed before this chunk; the complete provider is open.
 */
#include <stdint.h>

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

int gx8002_image_b_imcra_noise_update_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    float *noise = (float *)(uintptr_t)word(state, 0xa0u);
    float *scaled = (float *)(uintptr_t)word(state, 0xa4u);
    const float *gain = (const float *)(uintptr_t)word(state, 0xb8u);
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    const float *minimum_a = (const float *)(uintptr_t)word(state, 0x78u);
    const float *minimum_b = (const float *)(uintptr_t)word(state, 0x7cu);
    float *history_a = (float *)(uintptr_t)word(state, 0x8cu);
    float *history_b = (float *)(uintptr_t)word(state, 0x94u);
    float alpha = *(const float *)(const void *)(state + 0x60u);
    float scale = *(const float *)(const void *)(state + 0x64u);
    for (int32_t i = 0; i < bins; ++i) {
        float blend = alpha + (1.0f - alpha) * gain[i];
        noise[i] = blend * noise[i] + (1.0f - blend) * energy[i];
    }
    for (int32_t i = 0; i < bins; ++i)
        scaled[i] = scale * noise[i];
    for (int32_t i = 0; i < bins; ++i) {
        float current = minimum_a[i];
        if (history_a[i] < current)
            current = history_a[i];
        history_a[i] = current;
    }
    for (int32_t i = 0; i < bins; ++i) {
        float current = minimum_b[i];
        if (history_b[i] < current)
            current = history_b[i];
        history_b[i] = current;
    }
    int32_t period = (int32_t)word(state, 0x70u);
    int32_t frame = (int32_t)word(state, 0x20u) + 1;
    return frame % period != 0;
}
