/* SPDX-License-Identifier: MIT
 * Direct native 0x10004d3c tick ISR, 0x10004d64 timer setup,
 * and 0x10004db0 setup wrapper. Tick state is SRAM 0x20009964.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_clock_rate_4b50(uint32_t selector);
extern void gx8002_uart_stage2_irq_register_30e8(uint32_t irq,
                                                   uintptr_t callback,
                                                   uintptr_t context);
extern void gx8002_uart_stage2_vic_enable_30cc(uint32_t irq);

uint32_t gx8002_uart_stage2_timer_tick_4d3c(void)
{
    volatile uint32_t *const ticks =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009964);
    const uint64_t next = ((uint64_t)ticks[1] << 32) | ticks[0];
    const uint64_t incremented = next + UINT64_C(1000);
    ticks[0] = (uint32_t)incremented;
    ticks[1] = (uint32_t)(incremented >> 32);
    (void)*(const volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e010);
    return 0;
}

void gx8002_uart_stage2_timer_configure_4d64(void)
{
    const uint32_t rate =
        (uint32_t)gx8002_uart_stage2_clock_rate_4b50(10u);
    const uint32_t reload = rate / 1000u - 1u;
    if (reload <= UINT32_C(0x00ffffff)) {
        volatile uint32_t *const timer =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e010);
        timer[1] = reload;
        timer[2] = 0;
        timer[0] = 7;
    }
    gx8002_uart_stage2_irq_register_30e8(0u,
        (uintptr_t)&gx8002_uart_stage2_timer_tick_4d3c, 0);
    gx8002_uart_stage2_vic_enable_30cc(0u);
}

void gx8002_uart_stage2_setup_4db0(void)
{
    gx8002_uart_stage2_timer_configure_4d64();
}
