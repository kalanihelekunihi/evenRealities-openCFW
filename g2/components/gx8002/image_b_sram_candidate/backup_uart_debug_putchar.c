/* SPDX-License-Identifier: MIT
 * Image-B debug byte writer 0x10004818. Native reads the configured port
 * index from 0x2001739c and passes it with the byte to polled UART output.
 */
#include <stdint.h>

extern void gx8002_image_b_uart_poll_write_100045a0(uint32_t port, uint32_t value);

void gx8002_image_b_uart_debug_putchar_10004818(uint32_t value)
{
    uint32_t port = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2001739c);
    gx8002_image_b_uart_poll_write_100045a0(port, value);
}
