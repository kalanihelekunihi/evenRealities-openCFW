/* SPDX-License-Identifier: MIT
 * Image-A SRAM native PLL register sequence 0x10024b04 and 0x10025060.
 * Caller supplies the genuine 12-word clock configuration product object.
 */
#include <stdint.h>

void gx8002_resident_clock_set_pll_24b04(const uint32_t *configuration)
{
    if (configuration == 0) return;
    volatile uint32_t *const clock =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    clock[0x3cu / 4u] &= ~UINT32_C(2);
    clock[0x3cu / 4u] &= ~UINT32_C(1);
    if (configuration[0] == 0u) return;

    clock[0x1cu / 4u] &= ~UINT32_C(0x3f);
    clock[0x1cu / 4u] |= configuration[4];
    clock[0x20u / 4u] &= ~UINT32_C(0xff);
    clock[0x24u / 4u] &= ~UINT32_C(0x1f);
    clock[0x20u / 4u] |= (uint8_t)configuration[5];
    clock[0x24u / 4u] |= (configuration[5] & UINT32_C(0xfff)) >> 8;
    clock[0x28u / 4u] &= ~UINT32_C(7);
    clock[0x28u / 4u] |= configuration[9];
    clock[0x2cu / 4u] &= ~UINT32_C(0x7f);
    clock[0x2cu / 4u] |= configuration[6];
    clock[0x30u / 4u] &= ~UINT32_C(7);
    clock[0x30u / 4u] |= configuration[11] & 7u;
    clock[0x30u / 4u] &= ~UINT32_C(0x30);
    clock[0x30u / 4u] |= configuration[8] << 4;
    clock[0x3cu / 4u] &= ~UINT32_C(4);
    clock[0x3cu / 4u] |= (configuration[7] & 1u) << 2;
    clock[0x3cu / 4u] |= 2u;
    clock[0x3cu / 4u] |= 1u;
}

void gx8002_resident_clock_pll_wait_25060(const uint32_t *configuration)
{
    gx8002_resident_clock_set_pll_24b04(configuration);
    if (configuration[0] == 1u) {
        volatile uint32_t *const pll_status =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005098);
        while ((*pll_status & 8u) == 0u) { }
    }
}

extern uint64_t gx8002_resident_clock_time_us_2585c(void);

/* 0x1002500c: bounded PLL lock poll; the native unsigned 64-bit difference
 * requires both a zero high word and a low word no greater than limit*1000.
 */
uint32_t gx8002_resident_clock_pll_wait_timeout_2500c(
    const uint32_t *configuration, uint32_t limit_ms)
{
    gx8002_resident_clock_set_pll_24b04(configuration);
    if (configuration[0] != 1u) return 0u;
    uint64_t start = gx8002_resident_clock_time_us_2585c();
    const volatile uint32_t *const status =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005098);
    uint32_t timeout_us = limit_ms * 1000u;
    for (;;) {
        if ((*status & 8u) != 0u) return 0u;
        uint64_t elapsed = gx8002_resident_clock_time_us_2585c() - start;
        if (elapsed > timeout_us) return UINT32_MAX;
    }
}
