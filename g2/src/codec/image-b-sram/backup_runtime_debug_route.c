/* SPDX-License-Identifier: MIT
 * Native image-B 0x10009990 preserves R0 into the selected debug-byte sink.
 */
#include <stdint.h>

extern void gx8002_image_b_uart_debug_putchar_10004818(uint32_t value);

void gx8002_image_b_runtime_debug_putchar_10009990(uint32_t value)
{
    gx8002_image_b_uart_debug_putchar_10004818(value);
}
