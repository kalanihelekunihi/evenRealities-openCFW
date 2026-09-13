/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <driver/gx_clock.h>
extern void open_cfw_gx8002_clock_pll(GX_CLOCK_PLL *pll);
extern uint64_t open_cfw_gx8002_clock_time_us(void);

/* Recovered driver semantics differ from the SDK SPL wrappers: configuration
 * runs before the enable check, and the timeout uses a 64-bit microsecond clock.
 * Preserve the observed 32-bit timeout multiplication and strict > boundary. */
int open_cfw_gx8002_clock_pll_wait_timeout(GX_CLOCK_PLL *pll, uint32_t timeout_ms)
{
    open_cfw_gx8002_clock_pll(pll);
    if (pll->pll_enable != 1) return 0;
    uint64_t start = open_cfw_gx8002_clock_time_us();
    uint32_t timeout_us = timeout_ms * 1000u;
    while ((*(volatile uint32_t *)0xa0005098u & 8u) == 0) {
        if (open_cfw_gx8002_clock_time_us() - start > timeout_us) return -1;
    }
    return 0;
}

void open_cfw_gx8002_clock_pll_wait(GX_CLOCK_PLL *pll)
{
    open_cfw_gx8002_clock_pll(pll);
    if (pll->pll_enable == 1) {
        while ((*(volatile uint32_t *)0xa0005098u & 8u) == 0) {}
    }
}
