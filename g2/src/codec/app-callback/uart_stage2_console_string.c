/* SPDX-License-Identifier: MIT
 * Direct native console string output 0x1000618c.
 * The stock loop sends bytes to the UART sink until NUL.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_console_putc_2a84(uint32_t character);

void gx8002_uart_stage2_prepare_lower_618c(const void *literal)
{
    const uint8_t *p = (const uint8_t *)literal;
    while (*p != 0) gx8002_uart_stage2_console_putc_2a84(*p++);
}
