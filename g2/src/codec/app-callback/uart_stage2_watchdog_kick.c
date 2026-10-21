/* SPDX-License-Identifier: MIT
 * Direct native watchdog reload at stock 0x100044fc: one MMIO word store.
 */
#include <stdint.h>

void gx8002_uart_stage2_watchdog_kick_44fc(void)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa070000c) = 118u;
}
