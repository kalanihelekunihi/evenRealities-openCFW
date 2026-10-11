/* SPDX-License-Identifier: MIT
 * UART stage-1 clock milliseconds 0x100003bc and delay 0x100003fc.
 * Native clock source is a pair of words at 0xa0400004/08.
 */
#include <stdint.h>

static uint64_t stage1_clock_ticks(void)
{
    const volatile uint32_t *const timer =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400004);
    const uint32_t low = timer[0];
    const uint32_t high = timer[1];
    return ((uint64_t)high << 32) | low;
}

static uint32_t stage1_divide_1000_low32(uint64_t numerator)
{
    uint32_t remainder = 0;
    uint32_t quotient_low = 0;
    for (int bit = 63; bit >= 0; --bit) {
        remainder = (remainder << 1) | (uint32_t)((numerator >> bit) & 1u);
        if (remainder >= 1000u) {
            remainder -= 1000u;
            if (bit < 32) quotient_low |= UINT32_C(1) << bit;
        }
    }
    return quotient_low;
}

uint32_t gx8002_uart_stage1_time_ms(void)
{
    return stage1_divide_1000_low32(stage1_clock_ticks());
}

void gx8002_uart_stage1_mdelay(int32_t milliseconds)
{
    uint32_t remaining = (uint32_t)milliseconds;
    while (--remaining != UINT32_MAX) {
        const uint64_t target = stage1_clock_ticks() + UINT64_C(1001);
        while (stage1_clock_ticks() < target) { }
    }
}
