/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_aout_play_check_idle(uint32_t,uint32_t);
extern void open_cfw_gx8002_aout_set_r1_frame_over_int_enable(uint32_t,uint32_t);
extern void open_cfw_gx8002_mdelay(uint32_t);
/* Completion at handle28 is published by the playback ISR. Stock has no
 * timeout: if completion never arrives, this function continues waiting. */
int open_cfw_gx8002_aout_drain_frame(void *handle)
{
    volatile uint8_t *state=handle;
    state[28]=0;
    state[26]=1;
    open_cfw_gx8002_aout_play_check_idle(0xa0b00000u,1);
    open_cfw_gx8002_aout_set_r1_frame_over_int_enable(0xa0b00000u,1);
    for (;;) {
        __asm__ volatile ("" ::: "memory");
        if (((const uint8_t *)state)[28]) break;
        open_cfw_gx8002_mdelay(1);
    }
    return 0;
}
