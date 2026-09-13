/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint64_t open_cfw_gx8002_clock_time_us(void);
uint64_t open_cfw_gx8002_clock_time_ms(void)
{
    return open_cfw_gx8002_clock_time_us() / UINT64_C(1000);
}
