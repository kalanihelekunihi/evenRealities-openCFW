/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef union { uint32_t word; struct { unsigned low:1, enable:1, high:30; } bits; } word_edit;
/* Matched to pinned audio_out/v2.0/hw.o. Each operation is one word RMW;
 * retain low-bit truncation rather than converting nonzero to boolean. */
void open_cfw_gx8002_aout_set_r1_frame_over_int_enable(volatile uint32_t *base,
                                                     uint32_t enable)
{
    word_edit edit;
    edit.word = base[2];
    edit.bits.enable = enable;
    base[2] = edit.word;
}
void open_cfw_gx8002_aout_play_check_idle(volatile uint32_t *base, uint32_t enable)
{
    word_edit edit;
    edit.word = base[0];
    edit.bits.enable = enable;
    base[0] = edit.word;
}
