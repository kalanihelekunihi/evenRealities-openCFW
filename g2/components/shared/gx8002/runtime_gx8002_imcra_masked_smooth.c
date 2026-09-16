/* SPDX-License-Identifier: MIT
 * Development reconstruction, processing 0x4e9d0..0x4eb66.
 * Preconditions: 0 <= radius <= bins/2; valid disjoint arrays/kernel.
 * Radius and bins are live values supplied by the preceding processing block.
 * Zero selected weight still performs the stock rounded self-update.
 * This is not a complete processing function or an admitted image component.
 */
#include <stdint.h>
typedef union { uint32_t bits; float value; } masked_word;
void open_cfw_gx8002_imcra_masked_smooth(volatile uint32_t *state,
                                       int32_t bins, int32_t radius)
{
    if (radius > 0) {
        volatile float *estimate = (volatile float *)(uintptr_t)state[31];
        const volatile float *mask = (const volatile float *)(uintptr_t)state[45];
        for (int32_t i = 0; i < radius; ++i) {
            float selected = mask[i];
            float current, previous;
            if (selected != 0.0f) {
                const volatile float *power = (const volatile float *)(uintptr_t)state[16];
                current = power[i];
                previous = estimate[i];
            } else {
                current = estimate[i];
                previous = current;
            }
            masked_word alpha = { .bits = state[18] };
            float complement = 1.0f - alpha.value;
            volatile float retained = alpha.value * previous;
            estimate[i] = retained + complement * current;
        }
    }
    int32_t end = bins - radius;
    if (radius < end) {
        volatile float *estimate = (volatile float *)(uintptr_t)state[31];
        for (int32_t i = radius; i < end; ++i) {
            const volatile float *kernel = (const volatile float *)(uintptr_t)state[43];
            const volatile float *mask = (const volatile float *)(uintptr_t)state[45];
            const volatile float *power = (const volatile float *)(uintptr_t)state[16];
            float total_weight = 0.0f;
            float total_power = 0.0f;
            for (int32_t j = 0; j <= radius * 2; ++j) {
                float coefficient = kernel[j];
                float selected = mask[i - radius + j];
                float weight = coefficient * selected;
                float current = power[i - radius + j];
                total_weight = total_weight + weight;
                total_power = total_power + weight * current;
            }
            if (total_weight != 0.0f) {
                masked_word alpha = { .bits = state[18] };
                float complement = 1.0f - alpha.value;
                volatile float scaled = complement * total_power;
                float contribution = scaled / total_weight;
                float previous = estimate[i];
                estimate[i] = contribution + alpha.value * previous;
            } else {
                masked_word alpha = { .bits = state[18] };
                float previous = estimate[i];
                float complement = 1.0f - alpha.value;
                volatile float retained = alpha.value * previous;
                estimate[i] = retained + complement * previous;
            }
        }
    }
    if (end < bins) {
        volatile float *estimate = (volatile float *)(uintptr_t)state[31];
        const volatile float *mask = (const volatile float *)(uintptr_t)state[45];
        for (int32_t i = end; i < bins; ++i) {
            float selected = mask[i];
            float current, previous;
            if (selected != 0.0f) {
                const volatile float *power = (const volatile float *)(uintptr_t)state[16];
                current = power[i];
                previous = estimate[i];
            } else {
                current = estimate[i];
                previous = current;
            }
            masked_word alpha = { .bits = state[18] };
            float complement = 1.0f - alpha.value;
            volatile float retained = alpha.value * previous;
            estimate[i] = retained + complement * current;
        }
    }
}
