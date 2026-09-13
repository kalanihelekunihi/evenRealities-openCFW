/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int open_cfw_gx8002_console_port;
extern int open_cfw_gx8002_uart_initialize(uint32_t,uint32_t);

/* Recovered package 0xcd6c: remember the port before UART initialization,
 * including when initialization returns an error. */
int open_cfw_gx8002_console_initialize(uint32_t port,uint32_t baud)
{
    open_cfw_gx8002_console_port=(int32_t)port;
    return open_cfw_gx8002_uart_initialize(port,baud);
}
