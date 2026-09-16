/* SPDX-License-Identifier: MIT
 * Processing block 0x4e71a..0x4e776, separately callable development fragment.
 * The preceding peak clamp produces shifts -9..1 for signed Q15 input.
 * This does not implement the complete noise estimator or processing entry.
 */
#include <stdint.h>
void open_cfw_gx8002_imcra_power_spectrum(volatile uint32_t *state, int32_t shift)
{
    float scale = (float)(int32_t)(1u << (uint32_t)(shift + 9));
    int32_t bins = (int32_t)state[7];
    if (bins > 0) {
        volatile float *power = (volatile float *)(uintptr_t)state[16];
        const volatile int16_t *complex = (const volatile int16_t *)(uintptr_t)state[15];
        for (int32_t i = 0; i < bins; ++i) {
            float real = (float)complex[0];
            float imaginary = (float)complex[1];
            float imaginary_squared = imaginary * imaginary;
            float real_squared = real * real;
            /* Preserve the separate imaginary multiply before the MAC. */
            volatile float imaginary_scaled = imaginary_squared * scale;
            *power++ = imaginary_scaled + real_squared * scale;
            complex += 2;
        }
    }
}
