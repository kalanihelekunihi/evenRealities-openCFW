/* SPDX-License-Identifier: MIT */
#include <stdint.h>
void open_cfw_gx8002_rtc_set_tick (uint32_t duration)
{
    *(volatile uint32_t *)(uintptr_t)0xa0003008u = duration;
}
