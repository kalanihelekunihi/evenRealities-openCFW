/* SPDX-License-Identifier: MIT
 * Stage-2 watchdog reset at stock 0x10004508. Native stores are preserved
 * in order; hardware behavior has not been exercised on a GX8002 device.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_dispatch_4a48(uint32_t id,
                                              uint32_t enable);

__attribute__((noreturn)) void gx8002_uart_stage2_watchdog_reset_4508(void)
{
    gx8002_uart_stage2_dispatch_4a48(24u, 1u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa001002c) = 1u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0700000) = 0u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0700004) = 0u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa070000c) = 118u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0700000) = 1u;
    for (;;) { }
}
