/* SPDX-License-Identifier: MIT
 * Processing block 0x4e828..0x4e930. Development fragment, not full processing.
 * Valid initialized layout: 0 <= radius <= bins/2, sufficient kernel storage.
 * Radius zero (the observed initializer default) is included.
 */
#include <stdint.h>
typedef union { uint32_t bits; float value; } smooth_word;
void open_cfw_gx8002_imcra_smooth(volatile uint32_t *state, int32_t bins)
{
    int32_t radius = (int32_t)state[29];
    if (radius > 0) {
        volatile float *smoothed = (volatile float *)(uintptr_t)state[30];
        const volatile float *power = (const volatile float *)(uintptr_t)state[16];
        for (int32_t i = 0; i < radius; ++i) {
            smooth_word alpha = { .bits = state[18] };
            float old = smoothed[i];
            float current = power[i];
            float complement = 1.0f - alpha.value;
            volatile float retained = alpha.value * old;
            smoothed[i] = retained + complement * current;
        }
    }
    int32_t end = bins - radius;
    if (radius < end) {
        volatile float *smoothed = (volatile float *)(uintptr_t)state[30];
        for (int32_t i = radius; i < end; ++i) {
            const volatile float *kernel = (const volatile float *)(uintptr_t)state[43];
            const volatile float *power = (const volatile float *)(uintptr_t)state[16];
            float sum = 0.0f;
            for (int32_t j = 0; j <= radius * 2; ++j) {
                float coefficient = kernel[j];
                float current = power[i - radius + j];
                sum = sum + coefficient * current;
            }
            smooth_word alpha = { .bits = state[18] };
            float complement = 1.0f - alpha.value;
            float old = smoothed[i];
            volatile float contribution = complement * sum;
            smoothed[i] = contribution + alpha.value * old;
        }
    }
    if (end < bins) {
        volatile float *smoothed = (volatile float *)(uintptr_t)state[30];
        const volatile float *power = (const volatile float *)(uintptr_t)state[16];
        for (int32_t i = end; i < bins; ++i) {
            smooth_word alpha = { .bits = state[18] };
            float old = smoothed[i];
            float current = power[i];
            float complement = 1.0f - alpha.value;
            volatile float retained = alpha.value * old;
            smoothed[i] = retained + complement * current;
        }
    }
}
