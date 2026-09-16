/* SPDX-License-Identifier: MIT
 * Backup 0x1000e2c4: returns floor(log2(max(abs(samples)))) - 14,
 * or -15 for all zero samples. Stock always reads sample zero, even count<=0.
 * Such calls therefore still require one valid readable sample.
 */
#include <stdint.h>
int32_t open_cfw_gx8002_imcra_peak_shift(const volatile int16_t *samples,
                                       int32_t count)
{
    int32_t first = samples[0];
    uint32_t peak = (uint32_t)(first < 0 ? -first : first);
    for (int32_t i = 1; i < count; ++i) {
        int32_t value = samples[i];
        uint32_t magnitude = (uint32_t)(value < 0 ? -value : value);
        if (magnitude > peak) peak = magnitude;
    }
    if (!peak) return -15;
    return 17 - (int32_t)__builtin_clz(peak);
}
