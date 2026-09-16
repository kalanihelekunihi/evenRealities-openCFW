/* SPDX-License-Identifier: MIT
 * Development reconstruction 0x4ed44..0x4ee50 (before original epilogue).
 * Valid initialized dimensions, finite gains and in-range float conversions.
 * Output uses stock halfword wrapping before its -32767 lower clamp.
 * Not a complete processing entry; history rotation precedes this fragment.
 */
#include <stdint.h>
#include "fft_types.h"
extern int32_t open_cfw_gx8002_imcra_peak_shift(const volatile int16_t *, int32_t);
extern void open_cfw_gx8002_imcra_sample_shift(volatile int16_t *, int32_t, int32_t);
extern const csky_vdsp2_rfft_instance_q15 source_rfft_inverse;
extern void open_cfw_gx8002_backup_rfft(const volatile csky_vdsp2_rfft_instance_q15 *, q15_t *, q15_t *);
void open_cfw_gx8002_imcra_synthesize(volatile uint32_t *state,
                                      volatile int16_t *output,
                                      int32_t bins, int32_t forward_shift)
{
    volatile int16_t *spectrum = (volatile int16_t *)(uintptr_t)state[15];
    if (bins > 0) {
        const volatile float *gain = (const volatile float *)(uintptr_t)state[17];
        for (int32_t i = 0; i < bins; ++i) {
            int32_t real = spectrum[2*i];
            float factor = gain[i];
            spectrum[2*i] = (int16_t)(int32_t)((float)real * factor);
            int32_t imaginary = spectrum[2*i+1];
            spectrum[2*i+1] = (int16_t)(int32_t)((float)imaginary * factor);
        }
    }
    int32_t count = (int32_t)(state[6] + 2u);
    int32_t inverse_shift = open_cfw_gx8002_imcra_peak_shift(spectrum, count);
    open_cfw_gx8002_imcra_sample_shift(spectrum, count, inverse_shift);
    q15_t *work = (q15_t *)(uintptr_t)state[14];
    q15_t *complex = (q15_t *)(uintptr_t)state[15];
    open_cfw_gx8002_backup_rfft(&source_rfft_inverse, complex, work);
    uint32_t shift = 0u - 9u - (uint32_t)forward_shift - (uint32_t)inverse_shift;
    volatile int16_t *samples = (volatile int16_t *)(uintptr_t)state[14];
    count = (int32_t)state[6];
    open_cfw_gx8002_imcra_sample_shift(samples, count, (int32_t)shift);
    int32_t hop = (int32_t)state[5];
    if (hop > 0) {
        const volatile int16_t *time = (const volatile int16_t *)(uintptr_t)state[14];
        const volatile int16_t *window = (const volatile int16_t *)(uintptr_t)state[12];
        const volatile int16_t *overlap = (const volatile int16_t *)(uintptr_t)state[11];
        const volatile int16_t *normalization = (const volatile int16_t *)(uintptr_t)state[13];
        for (int32_t i = 0; i < hop; ++i) {
            int32_t coefficient = window[i];
            int32_t sample = time[i];
            int32_t windowed = (sample * coefficient) >> 15;
            int32_t previous = overlap[i];
            int16_t combined = (int16_t)(previous + windowed);
            int32_t scale = normalization[i];
            int32_t normalized = (int16_t)((scale * combined) >> 14);
            if (normalized < -32767) normalized = -32767;
            output[i] = (int16_t)normalized;
        }
    }
    int32_t remainder = (int32_t)(state[3] - (uint32_t)hop);
    if (remainder > 0) {
        const volatile int16_t *window = (const volatile int16_t *)(uintptr_t)state[12];
        const volatile int16_t *time = (const volatile int16_t *)(uintptr_t)state[14];
        volatile int16_t *overlap = (volatile int16_t *)(uintptr_t)state[11];
        for (int32_t i = 0; i < remainder; ++i) {
            int32_t sample = time[hop+i];
            int32_t coefficient = window[hop+i];
            overlap[i] = (int16_t)((sample * coefficient) >> 15);
        }
    }
    uint32_t frame = state[8];
    state[8] = frame + 1u;
}
