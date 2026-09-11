/* SPDX-License-Identifier: MIT */
/* Recovered codec 0xcb90..0xcbbc. Nonpositive signed lengths consume no
 * bytes. Each positive-length iteration uses the blocking byte transmitter. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern void open_cfw_gx8002_uart_transmit(void *descriptor, unsigned int value);
int32_t open_cfw_gx8002_uart_write(uint32_t port, const uint8_t *buffer, int32_t length)
{
    volatile uint32_t *descriptor = (volatile uint32_t *)
        ((uintptr_t)open_cfw_gx8002_uart_descriptors + (port << 7));
    for (int32_t i = 0; i < length; ++i)
        open_cfw_gx8002_uart_transmit((void *)descriptor, buffer[i]);
    return length > 0 ? length : 0;
}
