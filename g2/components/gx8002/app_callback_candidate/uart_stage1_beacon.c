/* SPDX-License-Identifier: MIT
 * UART stage-1 beacon/baud setup at 0x100004d0. Native branch compares
 * UART base against 0xa0100000, correcting the decompiler's null check.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage1_pmu_clock_rate(uint32_t selector);
extern uint32_t gx8002_uart_stage1_udiv(uint32_t numerator, uint32_t denominator);
extern uint32_t gx8002_uart_stage1_umod(uint32_t numerator, uint32_t denominator);

void gx8002_uart_stage1_beacon(uint32_t baud, uint32_t configured)
{
    const volatile uint32_t *const base_word =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002014);
    volatile uint32_t *uart = (volatile uint32_t *)(uintptr_t)*base_word;
    uart[0x04 / 4] = 0;
    uart[0x10 / 4] = 3;
    if (configured == 0) {
        const uint32_t selector = (uintptr_t)uart == UINT32_C(0xa0100000)
                                      ? 0x11u : 0x12u;
        const uint32_t rate = (uint32_t)gx8002_uart_stage1_pmu_clock_rate(selector);
        const uint32_t scaled_baud = baud << 4;
        const uint32_t divider = gx8002_uart_stage1_udiv(rate, scaled_baud);
        const uint32_t remainder = gx8002_uart_stage1_umod(rate, scaled_baud);
        const uint32_t percentage =
            gx8002_uart_stage1_udiv(remainder * 100u, scaled_baud);
        const uint32_t fractional = gx8002_uart_stage1_udiv(percentage << 4, 100u);
        uart = (volatile uint32_t *)(uintptr_t)*base_word;
        while ((uart[0x7c / 4] & 1u) != 0) { }
        uart[0x0c / 4] = 0x80u;
        uart[0x00 / 4] = divider & 0xffu;
        uart[0x04 / 4] = (divider & 0x7fffu) >> 8;
        uart[0xc0 / 4] = fractional & 0xffu;
    }
    while ((uart[0x7c / 4] & 1u) != 0) { }
    uart[0x0c / 4] = 3;
    uart[0x08 / 4] = 'O';
}
