/* SPDX-License-Identifier: MIT */
/* Recovered codec 0xc7ec..0xc804. Sample the device once, wait for data-ready,
 * then perform one full-width data-register read and return its low byte. */
#include <stdint.h>
uint32_t open_cfw_gx8002_uart_receive_byte(volatile uint32_t *descriptor)
{
    volatile uint32_t *device = (volatile uint32_t *)(uintptr_t)descriptor[1];
    while (!(device[5] & 1U)) {}
    return (uint8_t)device[0];
}
