/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "console_upstream_declarations.h"

/* Stored before initialization, even when gx_uart_init rejects the port.
 * Keep this symbolic state at its original location until all consumers
 * and the underlying UART implementation are reconstructed.
 */
__attribute__((section(".bss.backup_console_port"),aligned(4)))
volatile int open_cfw_gx8002_backup_console_port;

int gx_console_init(int port, uint32_t baudrate)
{
    open_cfw_gx8002_backup_console_port = port;
    return gx_uart_init(port, baudrate);
}

void gx_console_putc(int ch)
{
    gx_uart_putc(open_cfw_gx8002_backup_console_port, ch);
}
