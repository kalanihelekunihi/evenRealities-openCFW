/* SPDX-License-Identifier: MIT
 * Development reconstruction of 0x4eb66..0x4ec8c, positive bins only.
 * Includes secondary minimum update and mode-dependent probability estimate.
 * Float-to-unsigned conversion requires finite values in uint32 range.
 * Stock reinterprets those integer bits as float: this is intentional.
 * Target reciprocal uses a symbolic ISA instruction, not extracted code bytes.
 * This fragment is not a complete processing entry or hardware-qualified.
 */
#include <stdint.h>
typedef union { uint32_t bits; float value; } probability_word;
void open_cfw_gx8002_imcra_probability(volatile uint32_t *state, int32_t bins)
{
    if (bins <= 0) return;
    volatile float *minimum = (volatile float *)(uintptr_t)state[33];
    const volatile float *masked = (const volatile float *)(uintptr_t)state[31];
    for (int32_t i = 0; i < bins; ++i) {
        float previous = minimum[i];
        float current = masked[i];
        if (previous < current) current = previous;
        minimum[i] = current;
    }
    if (state[47] == 2) {
        minimum = (volatile float *)(uintptr_t)state[32];
        /* Stock also reloads masked here for subsequent processing stages. */
        (void)state[31];
    }
    const probability_word log2e = { .bits = 0x3fb8aa3b };
    const probability_word exponent_bias = { .bits = 0x42fde250 };
    volatile float *probability = (volatile float *)(uintptr_t)state[46];
    const volatile float *power = (const volatile float *)(uintptr_t)state[16];
    const volatile float *smooth = (const volatile float *)(uintptr_t)state[30];
    for (int32_t i = 0; i < bins; ++i) {
        float low = minimum[i];
        probability_word bias = { .bits = state[19] };
        float baseline = bias.value * low;
        probability_word smooth_limit = { .bits = state[22] };
        float smooth_threshold = baseline * smooth_limit.value;
        float current = power[i];
        if (baseline >= current) {
            float smoothed = smooth[i];
            if (smoothed < smooth_threshold) {
                probability[i] = 0.0f;
                continue;
            }
        }
        if (baseline < current) {
            probability_word upper = { .bits = state[21] };
            float upper_threshold = baseline * upper.value;
            if (current < upper_threshold) {
                float smoothed = smooth[i];
                if (smoothed < smooth_threshold) {
                    const volatile float *weighted = (const volatile float *)(uintptr_t)state[44];
                    float ratio = current / baseline;
                    float numerator = upper.value - ratio;
                    float weight = weighted[i];
                    float denominator = upper.value - 1.0f;
                    float q = numerator / denominator;
                    float exponent = exponent_bias.value - weight * log2e.value;
                    const volatile float *prior = (const volatile float *)(uintptr_t)state[39];
                    float encoded = exponent * 8388608.0f;
                    float complement = 1.0f - q;
                    float prior_value = prior[i];
                    float prior_plus_one = prior_value + 1.0f;
                    float odds = q / complement;
                    float factor = prior_plus_one * odds;
                    probability_word exponential = { .bits = (uint32_t)encoded };
                    float divisor = 1.0f + factor * exponential.value;
                    float result;
#ifdef __csky__
                    __asm__("frecips %0, %1" : "=v"(result) : "v"(divisor));
#else
                    result = 1.0f / divisor;
#endif
                    probability[i] = result;
                    continue;
                }
            }
        }
        probability[i] = 1.0f;
    }
}
