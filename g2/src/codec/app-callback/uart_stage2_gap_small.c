/* SPDX-License-Identifier: MIT
 * Small retained seeded stage-2 bodies: descriptor UART read 0x2ece,
 * IRQ wait 0x42c8, callback wrapper 0x3f00, and SPI register setup
 * 0x385c/0x387c/0x38b8. Lower SPI controller bodies remain explicit.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_irq_release_420c(uint32_t);
extern int32_t gx8002_uart_stage2_route_3b4c(uint32_t, uint32_t);
extern void gx8002_uart_stage2_spi_read_34a4(
    uint32_t address, uint8_t *buffer, uint32_t bytes);
extern uint32_t gx8002_uart_stage2_spi_write_35a8(
    const uint8_t *buffer, uint32_t bytes, uint32_t mode);

uint32_t gx8002_uart_stage2_dw_uart_getc_2ece(
    volatile const uint32_t *descriptor)
{
    volatile const uint32_t *uart =
        (volatile const uint32_t *)(uintptr_t)descriptor[1];
    while ((uart[5] & 1u) == 0u) { }
    return uart[0] & 0xffu;
}

uint32_t gx8002_uart_stage2_irq_wait_42c8(uint32_t line)
{
    uintptr_t controller = *(volatile const uint32_t *)(uintptr_t)
        UINT32_C(0x20009ddc);
    uint32_t mask = line < 32u ? 1u << line : 0u;
    while ((*(volatile const uint32_t *)(controller + 0x2c0u) & mask) == 0u) { }
    gx8002_uart_stage2_irq_release_420c(line);
    return 0;
}

void gx8002_uart_stage2_route_wrapper_3f00(void)
{
    uint32_t channel = *(volatile const uint32_t *)(uintptr_t)
        UINT32_C(0x200091c8);
    (void)gx8002_uart_stage2_route_3b4c(0u, channel);
}

void gx8002_uart_stage2_spi_wait_ready_385c(void)
{
    uint8_t state;
    do {
        gx8002_uart_stage2_spi_read_34a4(5u, &state, 1u);
    } while ((state & 1u) != 0u);
}

uint32_t gx8002_uart_stage2_spi_enable_387c(void)
{
    uint8_t state;
    gx8002_uart_stage2_spi_read_34a4(0x35u, &state, 1u);
    if ((state & 2u) == 0u) {
        state |= 2u;
        (void)gx8002_uart_stage2_spi_write_35a8(&state, 1u, 2u);
        gx8002_uart_stage2_spi_wait_ready_385c();
    }
    return 0;
}

uint32_t gx8002_uart_stage2_spi_enable_pair_38b8(void)
{
    uint8_t block[2];
    gx8002_uart_stage2_spi_read_34a4(5u, &block[0], 1u);
    uint8_t mode;
    gx8002_uart_stage2_spi_read_34a4(0x35u, &mode, 1u);
    if ((mode & 2u) == 0u) {
        block[1] = mode | 2u;
        (void)gx8002_uart_stage2_spi_write_35a8(block, 2u, 1u);
        gx8002_uart_stage2_spi_wait_ready_385c();
    }
    return 0;
}
