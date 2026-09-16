/* SPDX-License-Identifier: MIT
 * Development reconstruction of processing block 0x4e77e..0x4e828.
 * Called only on the noninitial-frame path with positive bin count.
 * This block updates posterior/prior ratios and the preliminary Wiener gain.
 * It is not a replacement for the complete processing function.
 */
#include <stdint.h>

typedef union { uint32_t bits; float value; } imcra_float_word;

void open_cfw_gx8002_imcra_prior_update(volatile uint32_t *state,
                                      volatile float *power, int32_t bins)
{
    const imcra_float_word epsilon = { .bits = 0x257da48a };
    const volatile float *noise = (const volatile float *)(uintptr_t)state[41];
    const volatile float *previous_gain = (const volatile float *)(uintptr_t)state[42];
    volatile float *prior = (volatile float *)(uintptr_t)state[39];
    volatile float *gain = (volatile float *)(uintptr_t)state[17];
    volatile float *weighted = (volatile float *)(uintptr_t)state[44];
    volatile float *posterior = (volatile float *)(uintptr_t)state[38];
    for (int32_t i = 0; i < bins; ++i) {
        float noise_value = noise[i];
        float denominator = noise_value + epsilon.value;
        float current_power = power[i];
        float ratio = current_power / denominator;
        float old_gain = previous_gain[i];
        float old_ratio = posterior[i];
        float old_gain_squared = old_gain * old_gain;
        float prediction = old_gain_squared * old_ratio;
        float excess = ratio - 1.0f;
        if (!(0.0f < excess)) excess = 0.0f;
        imcra_float_word alpha = { .bits = state[23] };
        float complement = 1.0f - alpha.value;
        volatile float retained = prediction * alpha.value;
        float estimate = retained + complement * excess;
        imcra_float_word floor = { .bits = state[48] };
        float bounded = floor.value;
        if (bounded < estimate) bounded = estimate;
        float divisor = bounded + 1.0f;
        prior[i] = bounded;
        float current_gain = bounded / divisor;
        gain[i] = current_gain;
        weighted[i] = ratio * current_gain;
        posterior[i] = ratio;
    }
}
