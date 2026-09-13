/* SPDX-License-Identifier: MIT */
#include <stdint.h>

uint64_t open_cfw_gx8002_clock_time_us(void)
{
    /* The low read precedes the high snapshot read, as in the recovered code. */
    uint32_t low = *(volatile uint32_t *)0xa0400044u;
    uint32_t high = *(volatile uint32_t *)0xa0400048u;
    uint64_t ticks = ((uint64_t)high << 32) | low;
    return (ticks * UINT64_C(1000)) >> 10;
}
