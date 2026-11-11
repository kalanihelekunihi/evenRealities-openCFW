/* SPDX-License-Identifier: MIT
 * Omitted UART boot stage 1, stock 0x10000584..0x10000658.
 * Its literal pool repeatedly points to the RAM UART-base word 0x20002014
 * (gx8002_uart_stage1_state.uart_base).
 * The initializer of that word is a separate product/startup obligation.
 */
#include <stdint.h>
#include "uart_stage1_state.h"

static volatile uint32_t *stage1_uart(void)
{
    return (volatile uint32_t *)(uintptr_t)gx8002_uart_stage1_state.uart_base;
}

void gx8002_uart_stage1_put(uint32_t value)
{
    volatile uint32_t *const uart = stage1_uart();
    while ((uart[5] & UINT32_C(0x40)) == 0) { }
    uart[0] = value;
}

void gx8002_uart_stage1_put_sync(uint32_t value)
{
    volatile uint32_t *const uart = stage1_uart();
    while ((uart[5] & UINT32_C(0x40)) == 0) { }
    uart[0] = value;
    while ((uart[5] & UINT32_C(0x40)) == 0) { }
}

int32_t gx8002_uart_stage1_try_get(uint8_t *out)
{
    volatile uint32_t *const uart = stage1_uart();
    if ((uart[5] & 1u) == 0) return -1;
    *out = (uint8_t)uart[0];
    return 0;
}

uint32_t gx8002_uart_stage1_get_char(void)
{
    volatile uint32_t *const uart = stage1_uart();
    while ((uart[5] & 1u) == 0) { }
    return uart[0] & UINT32_C(0xff);
}
