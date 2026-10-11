/* SPDX-License-Identifier: MIT
 * Native XIP 0x10203360..0x102033c7: DesignWare FIFO depth decoder.
 */
#include <stdint.h>

uint32_t gx8002_xip_uart_fifo_depth_10203360(void *raw_channel)
{
    volatile const uint8_t *const channel = raw_channel;
    volatile const uint8_t *const registers =
        (volatile const uint8_t *)(uintptr_t)
        *(volatile const uint32_t *)(const void *)(channel + 4u);
    uint32_t parameter =
        *(volatile const uint32_t *)(const void *)(registers + 0xf4u);
    uint32_t encoded = (parameter & 0x7fffffu) >> 16;
    switch (encoded) {
    case 1u: return 0x10u;
    case 2u: return 0x20u;
    case 4u: return 0x40u;
    case 8u: return 0x80u;
    case 0x10u: return 0x100u;
    case 0x20u: return 0x200u;
    case 0x40u: return 0x400u;
    case 0x80u: return 0x800u;
    default: return 0u;
    }
}
