/* Image-B IMCRA 0x10016260..0x1001634c: gain-table decision and the
 * native float-bit exponential approximation.  This separate source chunk
 * awaits whole-process control-flow and numerical qualification.
 */
#include <stdint.h>

typedef union { uint32_t bits; float value; } binary32;

static uint32_t word(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_gain_table_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)word(state, 0x1cu);
    uint32_t persistent_field = word(state, 0xbcu) == 2u ? 0x80u : 0x84u;
    const float *persistent =
        (const float *)(uintptr_t)word(state, persistent_field);
    const float *energy = (const float *)(uintptr_t)word(state, 0x40u);
    const float *smoothed = (const float *)(uintptr_t)word(state, 0x78u);
    const float *weighted = (const float *)(uintptr_t)word(state, 0xb0u);
    const float *adaptive = (const float *)(uintptr_t)word(state, 0x9cu);
    float *gain = (float *)(uintptr_t)word(state, 0xb8u);
    float lower_multiplier = *(const float *)(const void *)(state + 0x4cu);
    float upper_multiplier = *(const float *)(const void *)(state + 0x54u);
    float smoothing_multiplier = *(const float *)(const void *)(state + 0x58u);
    binary32 log2e = {.bits = UINT32_C(0x3fb8aa3b)};
    binary32 exp_bias = {.bits = UINT32_C(0x42fde250)};
    binary32 mantissa_scale = {.bits = UINT32_C(0x4b000000)};
    for (int32_t i = 0; i < bins; ++i) {
        float floor = persistent[i] * lower_multiplier;
        float upper = floor * smoothing_multiplier;
        float observation = energy[i];
        if (floor >= observation) {
            gain[i] = smoothed[i] < upper ? 0.0f : 1.0f;
            continue;
        }
        if (!(observation < floor * upper_multiplier) ||
            !(smoothed[i] < upper)) {
            gain[i] = 1.0f;
            continue;
        }
        float ratio = observation / floor;
        float fraction = (upper_multiplier - ratio) /
                         (upper_multiplier - 1.0f);
        float exponent = exp_bias.value - weighted[i] * log2e.value;
        binary32 approximation = {
            .bits = (uint32_t)(exponent * mantissa_scale.value)
        };
        float normalized = fraction / (1.0f - fraction);
        normalized *= adaptive[i] + 1.0f;
        gain[i] = 1.0f / (1.0f + normalized * approximation.value);
    }
}
