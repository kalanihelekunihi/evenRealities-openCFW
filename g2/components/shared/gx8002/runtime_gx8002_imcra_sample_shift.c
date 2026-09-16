/* SPDX-License-Identifier: MIT
 * Backup 0x1000e28c: in-place, nonsaturating Q15 scaling. Positive shift
 * means arithmetic right; zero/negative means left by its unsigned negation.
 * Explicit target mnemonics retain ISA shift-count behavior without C's
 * undefined out-of-range shifts. The portable path is for counts -31..31.
 */
#include <stdint.h>
void open_cfw_gx8002_imcra_sample_shift(volatile int16_t *samples,
                                      int32_t count, int32_t shift)
{
    if (shift > 0) {
        for (; count > 0; --count, ++samples) {
            int32_t value = *samples;
#if defined(__csky__)
            __asm__("asr %0, %1" : "+r"(value) : "r"(shift));
#else
            value >>= shift;
#endif
            *samples = (int16_t)value;
        }
    } else {
        uint32_t amount = 0u - (uint32_t)shift;
        for (; count > 0; --count, ++samples) {
            uint32_t value = (uint32_t)(int32_t)*samples;
#if defined(__csky__)
            __asm__("lsl %0, %1" : "+r"(value) : "r"(amount));
#else
            value <<= amount;
#endif
            *samples = (int16_t)value;
        }
    }
}
