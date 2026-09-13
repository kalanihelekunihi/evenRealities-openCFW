/* SPDX-License-Identifier: MIT */
/* Recovered package 0x177cc. Keep unsigned prescaler underflow as in stock. */
#include <stdint.h>
extern unsigned open_cfw_gx8002_clock_frequency(unsigned module);
#define TIMER_REGISTER(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0400000u+(offset)))
void open_cfw_gx8002_timer_channel_initialize(void)
{
    TIMER_REGISTER(0x50)=1;
    TIMER_REGISTER(0x50)=0;
    TIMER_REGISTER(0x60)=1;
    unsigned frequency=open_cfw_gx8002_clock_frequency(23);
    TIMER_REGISTER(0x64)=frequency/1000000u-1u;
    TIMER_REGISTER(0x68)=0;
    TIMER_REGISTER(0x50)=2;
}
