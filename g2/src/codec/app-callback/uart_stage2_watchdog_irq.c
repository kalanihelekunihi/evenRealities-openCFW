/* SPDX-License-Identifier: MIT
 * Direct watchdog IRQ trampoline at stock 0x10004454. Reading status
 * register +0x14 after callback invocation is the native acknowledge.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage2_watchdog_irq_4454(void)
{
    uint32_t (*callback)(void) = *(uint32_t (*volatile *)(void))
        (uintptr_t)UINT32_C(0x20009960);
    uint32_t result = callback != 0 ? callback() : 0u;
    (void)*(volatile const uint32_t *)(uintptr_t)UINT32_C(0xa0700014);
    return result;
}
