/* SPDX-License-Identifier: MIT
 * Retained seeded SPI flash erase-range body at stock 0x10003b4c.
 * It chooses 4 KiB (0x20) or aligned 64 KiB (0xd8) erase commands and
 * uses the descriptor's source-owned address-width shift setting.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_spi_read_34a4(
    uint32_t, uint8_t *, uint32_t);
extern void gx8002_uart_stage2_spi_write_raw_3524(
    uint32_t, const uint8_t *, uint32_t);

static void wait_ready(void)
{
    uint8_t state;
    do {
        gx8002_uart_stage2_spi_read_34a4(5u, &state, 1u);
    } while ((state & 1u) != 0u);
}

int32_t gx8002_uart_stage2_route_3b4c(uint32_t start, uint32_t bytes)
{
    uintptr_t descriptor = UINT32_C(0x200091c4);
    uint32_t capacity = *(volatile const uint32_t *)(descriptor + 4u);
    if (start >= capacity) return -22;
    uint32_t end = start + bytes;
    if (end > capacity) end = capacity;
    uint32_t address = start & ~UINT32_C(0xfff);
    uint32_t remaining = end - address;
    uint8_t *argument = (uint8_t *)(descriptor + 0x11u);
    uint32_t width = *(volatile const uint32_t *)(descriptor + 8u);
    while (remaining != 0u) {
        uint32_t block;
        uint32_t command;
        if ((address & 0xffffu) == 0u && remaining >= 0x10000u) {
            block = 0x10000u;
            command = 0xd8u;
            remaining -= block;
        } else {
            block = 0x1000u;
            command = 0x20u;
            remaining = remaining < block ? 0u : remaining - block;
        }
        wait_ready();
        gx8002_uart_stage2_spi_write_raw_3524(6u, 0, 0u);
        uint32_t initial_shift = (width + UINT32_C(0x1fffffff)) * 8u;
        for (uint32_t i = 0; i < 4u; ++i) {
            uint32_t shift = (initial_shift - i * 8u) & 63u;
            argument[i] = shift > 31u ? 0u : (uint8_t)(address >> shift);
        }
        gx8002_uart_stage2_spi_write_raw_3524(command, argument, 3u);
        wait_ready();
        address += block;
    }
    return 0;
}
