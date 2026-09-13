/* SPDX-License-Identifier: MIT */
/* Recovered package 0x47a74: maximum saturated Q15 magnitude.
 * Empty input writes zero; all input reads precede the output write.
 * Scalar halfword reads replace the original grouped DSP loads. */
#include <stdint.h>
void open_cfw_gx8002_backup_maxabs_q15(const int16_t *input, int16_t *output,
                                      uint32_t count)
{
    uint32_t maximum = 0;
    for (; count; --count) {
        int32_t sample = *input++;
        uint32_t magnitude = sample < 0 ? (uint32_t)-sample : (uint32_t)sample;
        if (magnitude > 32767u) magnitude = 32767u;
        if (magnitude > maximum) maximum = magnitude;
    }
    *output = (int16_t)maximum;
}
