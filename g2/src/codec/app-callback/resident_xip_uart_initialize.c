/* SPDX-License-Identifier: MIT
 * Native XIP 0x10203530..0x10203591. The frequency snap to nearby MHz,
 * channel stride, and argument propagation are from C-SKY instructions.
 * UART channel storage is a typed external data contract until final SRAM
 * object ownership and placement are established.
 */
#include <stdint.h>
#include "resident_uart_product_descriptors.h"

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t);
extern uint32_t gx8002_xip_uart_configure_102033c8(void *channel);

uint32_t gx8002_xip_uart_initialize_10203530(uint32_t port, uint32_t baud)
{
    if (port >= 2u) return UINT32_MAX;
    gx8002_resident_platform_gate_25080(17u + (port != 0u), 1u);
    uint32_t clock = gx8002_resident_clock_frequency_25210(16u);
    const uint32_t remainder = clock % 1000000u;
    if (remainder <= 100u) clock -= remainder;
    else if (1000000u - remainder <= 100u)
        clock += 1000000u - remainder;
    volatile uint8_t *const channel =
        (volatile uint8_t *)(void *)&gx8002_uart_channels_26a94[port];
    *(volatile uint32_t *)(void *)(channel + 0x0cu) = clock;
    *(volatile uint32_t *)(void *)(channel + 0x10u) = baud;
    return gx8002_xip_uart_configure_102033c8((void *)channel);
}
