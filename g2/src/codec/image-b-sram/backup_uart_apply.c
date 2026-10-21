/* SPDX-License-Identifier: MIT
 * Image-B UART register application, native 0x100043a4..0x10004517.
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * The binary64 arithmetic follows calls 0x123cc, 0x12050, 0x11e50,
 * 0x11de4, and 0x11464. Its exact C-SKY rounding/exception ABI remains
 * a separate qualification gate.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_uart_fifo_depth_1000433c(
    volatile uint32_t *record);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t line, int32_t (*handler)(int32_t, void *), uint32_t argument);
extern int32_t gx8002_image_b_uart_irq_10004250(int32_t line, void *argument);

static int32_t quarter_toward_zero(int32_t value)
{
    return (value + ((value < 0) ? 3 : 0)) >> 2;
}

int32_t gx8002_image_b_uart_apply_100043a4(volatile uint32_t *record)
{
    if (record[0x1cu / 4u] == 0u) record[0x1cu / 4u] = 8u;
    if (record[0x20u / 4u] == 0u) record[0x20u / 4u] = 1u;

    volatile uint32_t *uart = (volatile uint32_t *)(uintptr_t)record[1];
    uart[1] = 0u;
    uart[4] = record[0x24u / 4u] ? 34u : 3u;
    uart[2] = record[0x24u / 4u] ? 127u : 111u;

    uint32_t divisor = record[0x10u / 4u];
    if (divisor != 0u) {
        uint32_t scale = divisor << 4;
        uint32_t quotient = record[0x0cu / 4u] / scale;
        uint32_t remainder = record[0x0cu / 4u] - quotient * scale;
        record[0x14u / 4u] = quotient;
        double fractional = (double)remainder / (double)scale;
        fractional = fractional * 16.0 + 0.5;
        record[0x18u / 4u] = (uint32_t)(int32_t)fractional;
        uart[2] = 0u;
        uint32_t control = uart[3];
        uart[3] = control | 0x80u;
        uart[0] = quotient & 0xffu;
        uart[1] = (quotient >> 8) & 0x7fu;
        uart[0xc0u / 4u] = (uint8_t)record[0x18u / 4u];
        uart[3] = control;
        uart[2] = record[0x24u / 4u] ? 127u : 111u;
    }

    uart[2] = 0u;
    uart[3] = (uart[3] & ~31u) | 3u;
    uart[2] = record[0x24u / 4u] ? 127u : 111u;

    int32_t depth = (int32_t)gx8002_image_b_uart_fifo_depth_1000433c(record);
    record[0x30u / 4u] = (uint32_t)depth;
    switch (uart[0x9cu / 4u]) {
    case 0u: record[0x38u / 4u] = 1u; break;
    case 1u: record[0x38u / 4u] = (uint32_t)quarter_toward_zero(depth); break;
    case 2u: record[0x38u / 4u] = (uint32_t)(depth / 2); break;
    case 3u: record[0x38u / 4u] = (uint32_t)(depth - 2); break;
    default: break;
    }
    switch (uart[0xa0u / 4u]) {
    case 0u: record[0x34u / 4u] = 0u; break;
    case 1u: record[0x34u / 4u] = 2u; break;
    case 2u: record[0x34u / 4u] = (uint32_t)quarter_toward_zero(depth); break;
    case 3u: record[0x34u / 4u] = (uint32_t)(depth / 2); break;
    default: break;
    }
    record[0x2cu / 4u] = 1u;
    record[0x68u / 4u] = UINT32_MAX;
    record[0x7cu / 4u] = UINT32_MAX;
    gx8002_image_b_request_irq_10004844(
        record[0x3cu / 4u], gx8002_image_b_uart_irq_10004250,
        (uint32_t)(uintptr_t)record);
    return 0;
}
