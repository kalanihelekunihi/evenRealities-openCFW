/* SPDX-License-Identifier: MIT
 * Development block 0x4ec8c..0x4ed32, positive bins and stable state pointers.
 * Standalone wrapper reloads four pointers held live by the stock caller.
 * Not a complete processing entry point.
 */
#include <stdint.h>
typedef union { uint32_t bits; float value; } noise_word;
void open_cfw_gx8002_imcra_noise_update(volatile uint32_t *state, int32_t bins)
{
    const volatile float *probability = (const volatile float *)(uintptr_t)state[46];
    const volatile float *power = (const volatile float *)(uintptr_t)state[16];
    const volatile float *smooth = (const volatile float *)(uintptr_t)state[30];
    const volatile float *masked = (const volatile float *)(uintptr_t)state[31];
    volatile float *estimate = (volatile float *)(uintptr_t)state[40];
    for (int32_t i = 0; i < bins; ++i) {
        noise_word base = { .bits = state[24] };
        float chance = probability[i];
        float complement = 1.0f - base.value;
        float alpha = base.value + complement * chance;
        float previous = estimate[i];
        float current = power[i];
        float remaining = 1.0f - alpha;
        volatile float retained = alpha * previous;
        estimate[i] = retained + remaining * current;
    }
    volatile float *noise = (volatile float *)(uintptr_t)state[41];
    for (int32_t i = 0; i < bins; ++i) {
        float current = estimate[i];
        noise_word bias = { .bits = state[25] };
        noise[i] = bias.value * current;
    }
    volatile float *minimum = (volatile float *)(uintptr_t)state[35];
    for (int32_t i = 0; i < bins; ++i) {
        float previous = minimum[i];
        float current = smooth[i];
        if (previous < current) current = previous;
        minimum[i] = current;
    }
    minimum = (volatile float *)(uintptr_t)state[37];
    for (int32_t i = 0; i < bins; ++i) {
        float previous = minimum[i];
        float current = masked[i];
        if (previous < current) current = previous;
        minimum[i] = current;
    }
}
