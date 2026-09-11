/* SPDX-License-Identifier: MIT */
/* Recovered from authenticated codec package 0xcb24..0xcb40. The device
 * pointer is sampled once; status bit 6 is polled without a timeout. */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[][32];

void open_cfw_gx8002_uart_flush(uint32_t port)
{
    volatile uint32_t *descriptor = (volatile uint32_t *)
        ((uintptr_t)open_cfw_gx8002_uart_descriptors + (port << 7));
    volatile uint32_t *device = (volatile uint32_t *)(uintptr_t)descriptor[1];
    while (!(device[5] & 64U)) {}
}
