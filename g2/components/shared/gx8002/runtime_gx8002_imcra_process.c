/* SPDX-License-Identifier: MIT
 * Development composition of the reconstructed IMCRA stages.
 * Assumes the valid initialized state and stable pointers between stages.
 * Individual stage tests do NOT establish this entry's equivalence or ABI.
 * Not admitted to the firmware image; no binary implementation fallback.
 */
#include <stdint.h>
extern int32_t open_cfw_gx8002_imcra_prepare(volatile uint32_t *, const int16_t *);
extern void open_cfw_gx8002_imcra_power_spectrum(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_first_frame(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_prior_update(volatile uint32_t *, volatile float *, int32_t);
extern void open_cfw_gx8002_imcra_smooth(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_minimum_mask(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_masked_smooth(volatile uint32_t *, int32_t, int32_t);
extern void open_cfw_gx8002_imcra_probability(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_noise_update(volatile uint32_t *, int32_t);
extern void open_cfw_gx8002_imcra_history_rotate(volatile uint32_t *, int32_t, int32_t);
extern void open_cfw_gx8002_imcra_synthesize(volatile uint32_t *, volatile int16_t *, int32_t, int32_t);
void open_cfw_gx8002_imcra_process(volatile uint32_t *state,
                                  const int16_t *input, volatile int16_t *output)
{
    int32_t shift = open_cfw_gx8002_imcra_prepare(state, input);
    open_cfw_gx8002_imcra_power_spectrum(state, shift);
    int32_t bins = (int32_t)state[7];
    if (state[8] == 0) {
        open_cfw_gx8002_imcra_first_frame(state, bins);
        bins = (int32_t)state[7];
    }
    int32_t frame = (int32_t)state[8];
    if (bins > 0) {
        volatile float *power = (volatile float *)(uintptr_t)state[16];
        open_cfw_gx8002_imcra_prior_update(state, power, bins);
    }
    open_cfw_gx8002_imcra_smooth(state, bins);
    int32_t radius = (int32_t)state[29];
    open_cfw_gx8002_imcra_minimum_mask(state, bins);
    open_cfw_gx8002_imcra_masked_smooth(state, bins, radius);
    if (bins > 0) {
        open_cfw_gx8002_imcra_probability(state, bins);
        open_cfw_gx8002_imcra_noise_update(state, bins);
    }
    open_cfw_gx8002_imcra_history_rotate(state, bins, frame);
    bins = (int32_t)state[7];
    open_cfw_gx8002_imcra_synthesize(state, output, bins, shift);
}
