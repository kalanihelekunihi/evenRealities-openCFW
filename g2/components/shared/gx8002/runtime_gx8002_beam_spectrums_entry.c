// SPDX-License-Identifier: MIT
// Backup package 0x467d4: forward arguments and discard the core result.
#include <stdint.h>
extern int open_cfw_gx8002_beam_spectrums(volatile uint32_t *, const int16_t *, int32_t);
int beamforming_triMic_spectrums(volatile uint32_t *state, const int16_t *input, int32_t frame)
{
    open_cfw_gx8002_beam_spectrums(state, input, frame);
    return 0;
}
