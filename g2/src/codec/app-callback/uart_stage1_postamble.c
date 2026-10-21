/* SPDX-License-Identifier: MIT
 * UART stage-1 postamble at 0x10001d9c. Stock literal 0x20002274 is a
 * runtime peripheral-base word, whose initial value remains product data.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled);

void gx8002_uart_stage1_postamble(void)
{
    const volatile uint32_t *const base_word =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002274);
    volatile uint32_t *const peripheral = (volatile uint32_t *)(uintptr_t)*base_word;
    peripheral[0x3a0 / 4] |= UINT32_C(0x101);
    while ((peripheral[0x2c0 / 4] & 1u) == 0) { }
    peripheral[0x3a0 / 4] &= ~UINT32_C(0x101);
    peripheral[0x398 / 4] = 0;
    gx8002_uart_stage1_pmu_dispatch(0x19u, 0);
}
