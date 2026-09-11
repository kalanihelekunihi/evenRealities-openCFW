/* SPDX-License-Identifier: MIT */
/* Recovered codec 0xcb64..0xcb90. Nonpositive signed lengths consume no
 * bytes. Each positive-length iteration uses the blocking byte receiver. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];
extern uint32_t open_cfw_gx8002_uart_receive_byte(volatile uint32_t *descriptor);
int32_t open_cfw_gx8002_uart_read(uint32_t port, uint8_t *buffer, int32_t length)
{
    volatile uint32_t *descriptor = (volatile uint32_t *)
        ((uintptr_t)open_cfw_gx8002_uart_descriptors + (port << 7));
    for (int32_t i = 0; i < length; ++i)
        buffer[i] = (uint8_t)open_cfw_gx8002_uart_receive_byte(descriptor);
    return length > 0 ? length : 0;
}
