/* SPDX-License-Identifier: MIT
 * UART stage-1 postamble at 0x10001d9c. Stock literal 0x20002274
 * (gx8002_uart_stage1_dma_base) is a
 * runtime peripheral-base word, whose initial value remains product data.
 */
#include <stdint.h>
#include "uart_stage1_state.h"

extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled);

void gx8002_uart_stage1_postamble(void)
{
    volatile uint32_t *const peripheral =
        (volatile uint32_t *)(uintptr_t)gx8002_uart_stage1_dma_base;
    peripheral[0x3a0 / 4] |= UINT32_C(0x101);
    while ((peripheral[0x2c0 / 4] & 1u) == 0) { }
    peripheral[0x3a0 / 4] &= ~UINT32_C(0x101);
    peripheral[0x398 / 4] = 0;
    gx8002_uart_stage1_pmu_dispatch(0x19u, 0);
}
