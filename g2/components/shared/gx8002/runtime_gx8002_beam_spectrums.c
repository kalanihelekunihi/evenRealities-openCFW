// SPDX-License-Identifier: MIT
// Reconstructed from backup package 0x45be4..0x45dac.
// Development candidate: valid initialized state, positive ring length,
// nonnegative counts, and nonoverflowing buffer dimensions required.
#include <stdint.h>
extern void beam_peak_q15(const int16_t *, int16_t *, uint32_t);
extern void beam_shift_q15(const int16_t *, int32_t, int16_t *, uint32_t);
extern void beam_fill_q15(int16_t, int16_t *, uint32_t);
extern void open_cfw_gx8002_backup_rfft(const void *, int16_t *, int16_t *);
extern const unsigned char source_rfft_forward[];

int open_cfw_gx8002_beam_spectrums(volatile uint32_t *state,
                                  const int16_t *input, int32_t frame)
{
    int32_t ring_length = (int32_t)state[2];
    int32_t slot = frame % ring_length;
    int32_t samples = (int32_t)state[3];
    int32_t channels = (int32_t)state[1];
    uint32_t spectrum_stride = state[6];
    int32_t transform_size = (int32_t)state[5];
    int16_t *work = (int16_t *)(uintptr_t)state[33];
    int16_t peak = 0;
    beam_peak_q15(input, &peak, (uint32_t)samples * (uint32_t)channels);
    // Stock scans bits 14..0; zero selects 15. Bit 15 is not tested.
    int32_t shift = 15;
    for (int32_t bit = 14; bit >= 0; --bit) {
        if ((uint16_t)peak & (1u << bit)) { shift = 14 - bit; break; }
    }
    ((volatile int16_t *)(uintptr_t)state[37])[slot] = (int16_t)shift;
    for (int32_t channel = 0; channel < channels; ++channel) {
        int16_t *spectrum = (int16_t *)(uintptr_t)state[channel == 0 ? 30 : 31];
        spectrum += (uint32_t)slot * spectrum_stride * 2;
        beam_shift_q15(input, shift, work, (uint32_t)samples);
        int32_t window_samples = (int32_t)state[3];
        if (window_samples > 0) {
            const volatile uint32_t *window = (const volatile uint32_t *)(uintptr_t)state[28];
            for (int32_t i = 0; i < window_samples; ++i) {
                // Stock MULT keeps the low 32 bits before arithmetic >> 15.
                uint32_t product = (uint32_t)(int32_t)work[i] * window[i];
                work[i] = (int16_t)((int32_t)product >> 15);
            }
        }
        beam_fill_q15(0, work + samples, (uint32_t)(transform_size - samples));
        open_cfw_gx8002_backup_rfft(source_rfft_forward, work, spectrum);
        input += samples;
    }
    return 0;
}
