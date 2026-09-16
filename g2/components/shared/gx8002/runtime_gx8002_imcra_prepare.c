/* SPDX-License-Identifier: MIT
 * Candidate reconstruction of processing prefix 0x4e674..0x4e71a.
 * This is a separately callable development fragment, NOT the processing
 * entry point. It omits noise estimation, gain, inverse FFT and output.
 * State contains target 32-bit addresses. Valid allocated state is required.
 */
#include <stdint.h>
#include <stddef.h>
#include "fft_types.h"

extern void *open_cfw_gx8002_memmove(void *, const void *, size_t);
extern void *open_cfw_gx8002_memset(void *, int, size_t);
extern int32_t open_cfw_gx8002_imcra_peak_shift(const volatile int16_t *, int32_t);
extern void open_cfw_gx8002_imcra_sample_shift(volatile int16_t *, int32_t, int32_t);
extern const csky_vdsp2_rfft_instance_q15 source_rfft_forward;
extern void open_cfw_gx8002_backup_rfft(
    const volatile csky_vdsp2_rfft_instance_q15 *, q15_t *, q15_t *);

int32_t open_cfw_gx8002_imcra_prepare(volatile uint32_t *state,
                                     const int16_t *input)
{
    uint32_t hop = state[5];
    uint32_t frame = state[3];
    uint32_t history = state[9];
    open_cfw_gx8002_memmove((void *)(uintptr_t)history,
        (const void *)(uintptr_t)(history + hop * 2u), (frame - hop) * 2u);

    /* Stock reloads these fields across each external copy call. */
    hop = state[5];
    frame = state[3];
    history = state[9];
    open_cfw_gx8002_memmove(
        (void *)(uintptr_t)(history + (frame - hop) * 2u), input, hop * 2u);

    frame = state[3];
    uint32_t work = state[14];
    if ((int32_t)frame > 0) {
        const volatile int16_t *samples = (const volatile int16_t *)(uintptr_t)state[9];
        const volatile int16_t *window = (const volatile int16_t *)(uintptr_t)state[12];
        volatile int16_t *destination = (volatile int16_t *)(uintptr_t)work;
        for (uint32_t i = 0; i < frame; ++i) {
            int32_t sample = samples[i];
            int32_t coefficient = window[i];
            destination[i] = (int16_t)((sample * coefficient) >> 15);
        }
    }
    uint32_t transform = state[4];
    open_cfw_gx8002_memset((void *)(uintptr_t)(work + frame * 2u),
                         0, (transform - frame) * 2u);
    volatile int16_t *samples = (volatile int16_t *)(uintptr_t)state[14];
    int32_t count = (int32_t)state[6];
    int32_t shift = open_cfw_gx8002_imcra_peak_shift(samples, count);
    if (shift < -9) shift = -9;
    open_cfw_gx8002_imcra_sample_shift(samples, count, shift);
    q15_t *output = (q15_t *)(uintptr_t)state[15];
    q15_t *fft_input = (q15_t *)(uintptr_t)state[14];
    open_cfw_gx8002_backup_rfft(&source_rfft_forward, fft_input, output);
    return shift;
}
