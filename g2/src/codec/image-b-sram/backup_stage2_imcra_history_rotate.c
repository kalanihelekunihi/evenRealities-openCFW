/* Image-B IMCRA 0x1001652a..0x1001662e.  On the period boundary the
 * current minima are copied into two rotating banks, each bank is reduced
 * across all slots, and the reduced vectors replace the working minima.
 * The caller must then enter the spectral path at native 0x10016404.
 */
#include <stdint.h>

extern void gx8002_image_b_copy_10011344(void *, const void *, uint32_t);

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_history_rotate_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    int32_t period = (int32_t)word(state, 0x70u);
    int32_t slots = (int32_t)word(state, 0x6cu);
    int32_t counter = (int32_t)word(state, 0x20u);
    int32_t slot = (counter / period) % slots;
    uint32_t vector_bytes = (uint32_t)bins * 4u;
    float *bank_a = (float *)(uintptr_t)word(state, 0x88u);
    float *bank_b = (float *)(uintptr_t)word(state, 0x90u);
    float *persistent_a = (float *)(uintptr_t)word(state, 0x80u);
    float *persistent_b = (float *)(uintptr_t)word(state, 0x84u);
    gx8002_image_b_copy_10011344(
        bank_a + slot * bins, (void *)(uintptr_t)word(state, 0x8cu),
        vector_bytes);
    gx8002_image_b_copy_10011344(
        bank_b + slot * bins, (void *)(uintptr_t)word(state, 0x94u),
        vector_bytes);
    gx8002_image_b_copy_10011344(persistent_a, bank_a, vector_bytes);
    gx8002_image_b_copy_10011344(persistent_b, bank_b, vector_bytes);
    for (int32_t bank = 1; bank < slots; ++bank) {
        for (int32_t i = 0; i < bins; ++i) {
            float a = bank_a[bank * bins + i];
            float b = bank_b[bank * bins + i];
            if (persistent_a[i] < a)
                a = persistent_a[i];
            if (persistent_b[i] < b)
                b = persistent_b[i];
            persistent_a[i] = a;
            persistent_b[i] = b;
        }
    }
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x78u), persistent_a, vector_bytes);
    gx8002_image_b_copy_10011344(
        (void *)(uintptr_t)word(state, 0x7cu), persistent_b, vector_bytes);
}
