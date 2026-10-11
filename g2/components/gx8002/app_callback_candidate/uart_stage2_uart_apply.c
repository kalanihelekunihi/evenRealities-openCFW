/* SPDX-License-Identifier: MIT
 * UART hardware configuration body at stage-2 0x10002c38.
 * Native 0x10002d3a..6c converts the remainder and divisor to binary64,
 * divides, multiplies by 16.0, adds 0.5, and converts to unsigned integer.
 * The arithmetic is expressed in C; target IEEE/ABI equality is pending.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_irq_register_30e8(uint32_t irq,
                                                   uintptr_t callback,
                                                   uintptr_t context);
extern void gx8002_uart_stage2_irq_handler_2aa8(void);

uint32_t gx8002_uart_stage2_uart_apply_2c38(volatile uint32_t *descriptor)
{
    if (descriptor[0x1c / 4] == 0) descriptor[0x1c / 4] = 8;
    if (descriptor[0x20 / 4] == 0) descriptor[0x20 / 4] = 1;
    volatile uint32_t *const uart =
        (volatile uint32_t *)(uintptr_t)descriptor[1];
    const uint32_t extended = descriptor[0x24 / 4] != 0;
    const uint32_t lcr = extended ? 0x7fu : 0x6fu;
    uart[1] = 0;
    uart[4] = extended ? 0x22u : 3u;
    uart[2] = lcr;
    if (descriptor[0x10 / 4] != 0) {
        const uint32_t denominator = descriptor[0x10 / 4] * 16u;
        const uint32_t quotient = descriptor[0x0c / 4] / denominator;
        const uint32_t remainder =
            descriptor[0x0c / 4] - quotient * denominator;
        descriptor[0x14 / 4] = quotient;
        const uint32_t fraction = (uint32_t)
            (((double)remainder / (double)denominator) * 16.0 + 0.5);
        descriptor[0x18 / 4] = fraction;
        uart[2] = 0;
        const uint32_t old_lcr = uart[3];
        uart[3] = old_lcr | 0x80u;
        uart[0] = quotient & 0xffu;
        uart[1] = (quotient & 0x7fffu) >> 8;
        uart[0xc0 / 4] = fraction & 0xffu;
        uart[3] = old_lcr;
        uart[2] = lcr;
    }
    uart[2] = 0;
    uart[3] = (uart[3] & ~UINT32_C(0x1f)) | 3u;
    uart[2] = lcr;
    const uint32_t width = (uart[0xf4 / 4] & UINT32_C(0x7fffff)) >> 16;
    uint32_t bit = 0;
    switch (width) {
    case 1: bit = 0x10; break;
    case 2: bit = 0x20; break;
    case 4: bit = 0x40; break;
    case 8: bit = 0x80; break;
    case 16: bit = 0x100; break;
    case 32: bit = 0x200; break;
    case 64: bit = 0x400; break;
    case 128: bit = 0x800; break;
    default: break;
    }
    descriptor[0x30 / 4] = bit;
    switch (uart[0x9c / 4]) {
    case 0: descriptor[0x38 / 4] = 1; break;
    case 1: descriptor[0x38 / 4] = bit / 4u; break;
    case 2: descriptor[0x38 / 4] = bit / 2u; break;
    case 3: descriptor[0x38 / 4] = bit - 2u; break;
    default: break;
    }
    switch (uart[0xa0 / 4]) {
    case 0: descriptor[0x34 / 4] = 0; break;
    case 1: descriptor[0x34 / 4] = 2; break;
    case 2: descriptor[0x34 / 4] = bit / 4u; break;
    case 3: descriptor[0x34 / 4] = bit / 2u; break;
    default: break;
    }
    descriptor[0x2c / 4] = 1;
    descriptor[0x68 / 4] = UINT32_MAX;
    descriptor[0x7c / 4] = UINT32_MAX;
    gx8002_uart_stage2_irq_register_30e8(descriptor[0x3c / 4],
        (uintptr_t)&gx8002_uart_stage2_irq_handler_2aa8,
        (uintptr_t)descriptor);
    return 0;
}
