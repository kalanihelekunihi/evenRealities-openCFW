/* SPDX-License-Identifier: MIT
 * Stage-1 announce at 0x1000065c. Native branch compares UART base with
 * 0xa0100000, not null as inferred by the decompiler.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_announce_transfer(uint32_t first,
                                                   uintptr_t uart_base,
                                                   uint32_t second,
                                                   uint32_t width);
extern void gx8002_uart_stage1_postamble(void);

int32_t gx8002_uart_stage1_announce(uint32_t first, uint32_t second)
{
    const volatile uint32_t *const base_word =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002014);
    volatile uint32_t *uart = (volatile uint32_t *)(uintptr_t)*base_word;
    uart[0xa8 / 4] = 1;
    const uint32_t width = (uintptr_t)uart == UINT32_C(0xa0100000) ? 6u : 4u;
    gx8002_uart_stage1_announce_transfer(first, (uintptr_t)uart, second, width);
    uart = (volatile uint32_t *)(uintptr_t)*base_word;
    static const uint8_t ready[] = {'r', 'e', 'a', 'd', 'y'};
    for (unsigned i = 0; i < sizeof ready; ++i) {
        while ((uart[5] & UINT32_C(0x40)) == 0) { }
        uart[0] = ready[i];
    }
    gx8002_uart_stage1_postamble();
    return 0;
}
