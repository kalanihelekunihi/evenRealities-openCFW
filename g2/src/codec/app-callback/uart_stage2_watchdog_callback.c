/* SPDX-License-Identifier: MIT
 * Watchdog interrupt callback at stock 0x10005958. Native increments the
 * RAM counter, logs its new value, reloads watchdog, and returns zero.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_launch_61a4(const char *, ...);
extern void gx8002_uart_stage2_watchdog_kick_44fc(void);

uint32_t gx8002_uart_stage2_watchdog_callback_5958(void)
{
    volatile uint32_t *counter = (volatile uint32_t *)(uintptr_t)
        UINT32_C(0x20009978);
    uint32_t value = *counter + 1u;
    *counter = value;
    gx8002_uart_stage2_launch_61a4(
        "watchdog level interrupt! %d\n", value);
    gx8002_uart_stage2_watchdog_kick_44fc();
    return 0;
}
