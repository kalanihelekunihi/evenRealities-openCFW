/* SPDX-License-Identifier: MIT */
/* Recovered console path. Port descriptors are 128 bytes; only the MMIO-base
 * field at offset four is used here. Other descriptor fields remain separate
 * recovery work. No timeout is added to the stock transmit-ready wait.
 */
#include <stdint.h>
#include <stddef.h>
extern unsigned char open_cfw_gx8002_uart_descriptors[];
extern int open_cfw_gx8002_console_port;

void open_cfw_gx8002_uart_transmit(void *descriptor, unsigned int value)
{
    volatile uint32_t *base = *(volatile uint32_t **)((unsigned char *)descriptor + 4);
    while (!(base[5] & 32U)) {}
    base[0] = value;
}

void open_cfw_gx8002_uart_putc(int port, int character)
{
    void *descriptor = (void *)((uintptr_t)open_cfw_gx8002_uart_descriptors + ((uint32_t)port << 7));
    if (character == 10)
        open_cfw_gx8002_uart_transmit(descriptor, 13);
    open_cfw_gx8002_uart_transmit(descriptor, (unsigned char)character);
}

void open_cfw_gx8002_console_putc(int character)
{
    open_cfw_gx8002_uart_putc(open_cfw_gx8002_console_port, character);
}
