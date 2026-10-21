/* SPDX-License-Identifier: MIT
 * Image-B UART FIFO selector 0x1000433c: low-byte field in register +0xf4
 * is accepted only for powers of two from 1 through 128.
 */
#include <stdint.h>

uint32_t gx8002_image_b_uart_fifo_depth_1000433c(volatile uint32_t *record)
{
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)record[1];
    uint32_t selector = (registers[0xf4u / 4u] >> 16) & 0xffu;
    switch (selector) {
    case 1u: return 0x10u;
    case 2u: return 0x20u;
    case 4u: return 0x40u;
    case 8u: return 0x80u;
    case 16u: return 0x100u;
    case 32u: return 0x200u;
    case 64u: return 0x400u;
    case 128u: return 0x800u;
    default: return 0u;
    }
}
