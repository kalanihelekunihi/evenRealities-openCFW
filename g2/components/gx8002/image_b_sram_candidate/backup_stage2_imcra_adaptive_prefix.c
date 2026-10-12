/* Native image-B IMCRA process 0x10015e3e..0x10015ee4.
 * This is the first adaptive float-vector block of the complete process;
 * later subwindow/minimum tracking and overlap-output blocks remain open.
 */
#include <stdint.h>

typedef union { uint32_t bits; float value; } image_b_float_word;

static uint32_t field(const uint8_t *state, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(state + offset);
}

void gx8002_image_b_imcra_adaptive_prefix_chunk(uint8_t *state)
{
    int32_t bins = (int32_t)field(state, 0x1cu);
    /* Native cold initialization rejoins at 0x10015e3e while +0x20 is
     * still zero; the adaptive vector executes on that first frame. */
    if (bins <= 0)
        return;
    float *minimum = (float *)(uintptr_t)field(state, 0xa4u);
    float *history = (float *)(uintptr_t)field(state, 0xa8u);
    float *prior = (float *)(uintptr_t)field(state, 0x98u);
    float *adaptive = (float *)(uintptr_t)field(state, 0x9cu);
    float *gain = (float *)(uintptr_t)field(state, 0x44u);
    float *weighted = (float *)(uintptr_t)field(state, 0xb0u);
    float *energy = (float *)(uintptr_t)field(state, 0x40u);
    image_b_float_word epsilon = {.bits = UINT32_C(0x257da48a)};
    float alpha = *(float *)(void *)(state + 0x5cu);
    float floor = *(float *)(void *)(state + 0xc0u);
    for (int32_t i = 0; i < bins; ++i) {
        float ratio = energy[i] / (minimum[i] + epsilon.value);
        volatile float squared = history[i] * history[i];
        volatile float prior_weighted = squared * prior[i];
        float excess = ratio - 1.0f;
        if (!(0.0f < excess))
            excess = 0.0f;
        volatile float smooth = alpha * prior_weighted;
        smooth = smooth + (1.0f - alpha) * excess;
        float clamped = floor < smooth ? smooth : floor;
        adaptive[i] = clamped;
        gain[i] = clamped / (clamped + 1.0f);
        weighted[i] = ratio * gain[i];
        prior[i] = ratio;
    }
}
