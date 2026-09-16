/* SPDX-License-Identifier: MIT
 * Development block 0x4e930..0x4e9d0: minimum tracking and noise-update mask.
 * The two complete passes and short-circuit parameter reads match stock.
 * Not a complete processing entry point.
 */
#include <stdint.h>
typedef union { uint32_t bits; float value; } mask_word;
void open_cfw_gx8002_imcra_minimum_mask(volatile uint32_t *state, int32_t bins)
{
    if (bins <= 0) return;
    volatile float *minimum = (volatile float *)(uintptr_t)state[32];
    const volatile float *smooth = (const volatile float *)(uintptr_t)state[30];
    for (int32_t i = 0; i < bins; ++i) {
        float previous = minimum[i];
        float current = smooth[i];
        if (previous < current) current = previous;
        minimum[i] = current;
    }
    const volatile float *power = (const volatile float *)(uintptr_t)state[16];
    volatile float *mask = (volatile float *)(uintptr_t)state[45];
    for (int32_t i = 0; i < bins; ++i) {
        float low = minimum[i];
        mask_word bias = { .bits = state[19] };
        float baseline = bias.value * low;
        mask_word power_limit = { .bits = state[20] };
        float threshold = baseline * power_limit.value;
        float current = power[i];
        float selected = 0.0f;
        if (current < threshold) {
            mask_word smooth_limit = { .bits = state[22] };
            float smooth_threshold = baseline * smooth_limit.value;
            float smoothed = smooth[i];
            if (smoothed < smooth_threshold) selected = 1.0f;
        }
        mask[i] = selected;
    }
}
