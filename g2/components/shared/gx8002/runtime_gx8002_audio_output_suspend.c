/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern void open_cfw_gx8002_aout_play_check_idle(volatile uint32_t *,uint32_t);
extern void open_cfw_gx8002_aout_set_r1_frame_over_int_enable(volatile uint32_t *,uint32_t);
int open_cfw_gx8002_aout_suspend(void *handle)
{
    const uint8_t *state=(const uint8_t *)handle;
    volatile uint32_t *base=(volatile uint32_t *)0xa0b00000u;
    if (state[27]) {
        base[2]=base[2]&~1u;
        base[3]=base[3]&1u;
    }
    __asm__ volatile ("" ::: "memory");
    if (state[26]) {
        open_cfw_gx8002_aout_play_check_idle(base,0);
        open_cfw_gx8002_aout_set_r1_frame_over_int_enable(base,0);
        base[3]=base[3]&2u;
    }
    open_cfw_gx8002_platform_gate(11,0);
    open_cfw_gx8002_platform_gate(15,0);
    return 0;
}
