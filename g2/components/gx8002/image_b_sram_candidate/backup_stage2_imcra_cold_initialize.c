/* Image-B IMCRA 0x10016648..0x100167a2: first-frame cold state.
 * The native branch from the initial FFT enters this block when +0x20 is
 * zero, then rejoins the adaptive loop (or the empty-bin branch).
 */
#include <stdint.h>

extern void gx8002_image_b_copy_10011344(void *, const void *, uint32_t);

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_cold_initialize_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    int32_t radius = (int32_t)word(state, 0x74u);
    int32_t end = bins - radius;
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    const float *weights = (const float *)(uintptr_t)word(state, 0xacu);
    float *minimum = (float *)(uintptr_t)word(state, 0x78u);
    if (radius > 0) {
        for (int32_t i = 0; i < radius; ++i)
            minimum[i] = energy[i];
    }
    if (radius < end) {
        for (int32_t i = radius; i < end; ++i) {
            float sum = 0.0f;
            for (int32_t j = 0; j <= radius * 2; ++j)
                sum += weights[j] * energy[i - radius + j];
            minimum[i] = sum;
        }
    }
    if (end < bins) {
        for (int32_t i = end; i < bins; ++i)
            minimum[i] = energy[i];
    }
    uint32_t bytes = (uint32_t)bins * 4u;
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x7cu), minimum, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x80u), minimum, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x84u), minimum, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x8cu), minimum, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x94u), minimum, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0xa4u), energy, bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0xa0u), energy, bytes);
    int32_t slots = (int32_t)word(state, 0x6cu);
    float *bank_a = (float *)(uintptr_t)word(state, 0x88u);
    float *bank_b = (float *)(uintptr_t)word(state, 0x90u);
    for (int32_t slot = 0; slot < slots; ++slot) {
        gx8002_image_b_copy_10011344(
            bank_a + slot * bins, energy, bytes);
        gx8002_image_b_copy_10011344(
            bank_b + slot * bins, energy, bytes);
    }
}
