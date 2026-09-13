/* SPDX-License-Identifier: MIT */
/* Recovered AUDIO_IN_CTRL word fields from upstream lvp_audio_in.c. */
#include <stdint.h>
#define STATE ((volatile uint32_t *)0x2002ecb0)
int open_cfw_gx8002_audio_input_delayed_vad(void) { return STATE[3]; }
int open_cfw_gx8002_audio_input_update_read(int offset)
{
    uint32_t next = STATE[0] + (uint32_t)offset;
    if (next > STATE[1]) return -1;
    STATE[0] = next;
    return 0;
}
