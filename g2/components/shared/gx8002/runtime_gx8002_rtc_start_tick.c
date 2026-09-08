/* SPDX-License-Identifier: MIT */
#include <stdint.h>
void open_cfw_gx8002_rtc_start_tick(void)
{
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)0xa000300cu;
    *control = *control | 4u;
}
