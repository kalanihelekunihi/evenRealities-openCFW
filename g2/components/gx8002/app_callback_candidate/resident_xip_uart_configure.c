/* SPDX-License-Identifier: MIT
 * Native XIP 0x102033c8..0x1020352b. Register order, default fields,
 * divisor/fraction calculation, FIFO thresholds and IRQ registration are
 * from direct C-SKY instructions. Fraction uses the stock double sequence
 * remainder/divisor * 16.0 + 0.5, rounded toward zero to uint32.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_uart_fifo_depth_10203360(void *channel);
extern uint32_t gx8002_xip_uart_isr_10203278(uint32_t, uint32_t);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);

static uint32_t uart_load(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void uart_store(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_uart_configure_102033c8(void *raw_channel)
{
    volatile uint8_t *const channel = raw_channel;
    if (uart_load(channel, 0x1cu) == 0u) uart_store(channel, 0x1cu, 8u);
    if (uart_load(channel, 0x20u) == 0u) uart_store(channel, 0x20u, 1u);
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        uart_load(channel, 4u);
    uart_store(registers, 4u, 0u);
    uint32_t fifo_mode = uart_load(channel, 0x24u);
    uart_store(registers, 0x10u, fifo_mode ? 0x22u : 3u);
    uart_store(registers, 8u, fifo_mode ? 0x7fu : 0x6fu);

    uint32_t baud = uart_load(channel, 0x10u);
    if (baud != 0u) {
        uint32_t denominator = baud * 16u;
        uint32_t clock = uart_load(channel, 0x0cu);
        uint32_t divisor = clock / denominator;
        uart_store(channel, 0x14u, divisor);
        uint32_t remainder = clock - divisor * denominator;
        uint32_t fraction = (uint32_t)(
            ((double)remainder / (double)denominator) * 16.0 + 0.5);
        uart_store(channel, 0x18u, fraction);
        uart_store(registers, 8u, 0u);
        uint32_t line = uart_load(registers, 0x0cu);
        uart_store(registers, 0x0cu, line | 0x80u);
        uart_store(registers, 0u, divisor & 0xffu);
        uart_store(registers, 4u, (divisor & 0x7fffu) >> 8);
        uart_store(registers, 0xc0u, fraction & 0xffu);
        uart_store(registers, 0x0cu, line);
        uart_store(registers, 8u, fifo_mode ? 0x7fu : 0x6fu);
    }
    uart_store(registers, 8u, 0u);
    uart_store(registers, 0x0cu,
               (uart_load(registers, 0x0cu) & ~UINT32_C(0x1f)) | 3u);
    uart_store(registers, 8u, fifo_mode ? 0x7fu : 0x6fu);

    uint32_t depth = gx8002_xip_uart_fifo_depth_10203360((void *)channel);
    uart_store(channel, 0x30u, depth);
    uint32_t rx_mode = uart_load(registers, 0x9cu);
    uint32_t tx_mode = uart_load(registers, 0xa0u);
    if (rx_mode == 0u) uart_store(channel, 0x38u, 1u);
    else if (rx_mode == 1u)
        uart_store(channel, 0x38u, (uint32_t)((int32_t)depth / 4));
    else if (rx_mode == 2u)
        uart_store(channel, 0x38u, (uint32_t)((int32_t)depth / 2));
    else if (rx_mode == 3u) uart_store(channel, 0x38u, depth - 2u);
    if (tx_mode == 0u) uart_store(channel, 0x34u, 0u);
    else if (tx_mode == 1u) uart_store(channel, 0x34u, 2u);
    else if (tx_mode == 2u)
        uart_store(channel, 0x34u, (uint32_t)((int32_t)depth / 4));
    else if (tx_mode == 3u)
        uart_store(channel, 0x34u, (uint32_t)((int32_t)depth / 2));

    uart_store(channel, 0x2cu, 1u);
    uart_store(channel, 0x68u, UINT32_MAX);
    uart_store(channel, 0x7cu, UINT32_MAX);
    gx8002_resident_request_irq_2553c(
        uart_load(channel, 0x3cu),
        (uint32_t)(uintptr_t)gx8002_xip_uart_isr_10203278,
        (uint32_t)(uintptr_t)channel);
    return 0u;
}
