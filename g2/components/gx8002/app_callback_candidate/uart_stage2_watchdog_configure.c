/* SPDX-License-Identifier: MIT
 * Native watchdog configuration at stock 0x10004478. The 16-way scale
 * search uses the stock 1,000,000 divisor and duplicated nibble encoding.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_dispatch_4a48(uint32_t, uint32_t);
extern void gx8002_uart_stage2_irq_register_30e8(uint32_t, uintptr_t,
                                                  uintptr_t);
extern void gx8002_uart_stage2_watchdog_irq_4454(void);
extern int32_t gx8002_uart_stage2_launch_61a4(const char *, ...);

void gx8002_uart_stage2_watchdog_configure_4478(
    uint32_t doubled, uint32_t value, uint32_t (*callback)(void))
{
    (void)doubled; /* Native r0 is overwritten before its first use. */
    if (value < 1000u) {
        gx8002_uart_stage2_launch_61a4("level timout invalid\n");
        return;
    }
    gx8002_uart_stage2_dispatch_4a48(24u, 1u);
    uint32_t desired = value / 1000u;
    uint32_t scale = 0xffu;
    for (uint32_t i = 0; i < 16u; ++i) {
        uint32_t period = (uint32_t)
            ((int32_t)(UINT32_C(1) << (i + 16u)) / 1000000);
        if (period >= desired) {
            scale = i | (i << 4);
            break;
        }
    }
    volatile uint32_t *watchdog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0700000);
    watchdog[1] = scale;
    watchdog[3] = 118u;
    *(volatile uintptr_t *)(uintptr_t)UINT32_C(0x20009960) =
        (uintptr_t)callback;
    gx8002_uart_stage2_irq_register_30e8(
        11u, (uintptr_t)&gx8002_uart_stage2_watchdog_irq_4454, 0u);
    watchdog[0] = watchdog[0] | 1u;
}
