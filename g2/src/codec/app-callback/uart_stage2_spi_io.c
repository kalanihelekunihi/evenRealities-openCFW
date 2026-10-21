/* SPDX-License-Identifier: MIT
 * Retained seeded SPI controller bodies 0x100034a4, 0x10003524,
 * 0x100035a8. Native MMIO base is 0xa2000000 with status/control
 * register at +0x28. These are real hardware paths, untested on device.
 */
#include <stdint.h>

static volatile uint32_t *const spi =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);

void gx8002_uart_stage2_spi_read_34a4(uint32_t address,
                                       uint8_t *buffer,
                                       uint32_t bytes)
{
    while ((spi[0x28u / 4u] & 1u) != 0u) { }
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0xc07u;
    spi[1] = bytes - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = address;
    for (uint32_t i = 0; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) { }
        buffer[i] = (uint8_t)spi[0x60u / 4u];
    }
    while (spi[0x24u / 4u] != 0u) { }
    while ((spi[0x28u / 4u] & 1u) != 0u) { }
}

void gx8002_uart_stage2_spi_write_raw_3524(
    uint32_t address, const uint8_t *buffer, uint32_t bytes)
{
    while ((spi[0x28u / 4u] & 1u) != 0u) { }
    spi[0x08u / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0x407u;
    spi[1] = bytes;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = bytes << 16;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = address;
    for (uint32_t i = 0; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) { }
        spi[0x60u / 4u] = buffer[i];
    }
    while (spi[0x20u / 4u] != 0u) { }
    while ((spi[0x28u / 4u] & 1u) != 0u) { }
}

uint32_t gx8002_uart_stage2_spi_write_35a8(
    const uint8_t *buffer, uint32_t bytes, uint32_t mode)
{
    if (bytes > 2u) return UINT32_MAX;
    uint32_t command;
    if (mode == 2u) command = 0x31u;
    else if (mode == 3u) command = 0x11u;
    else if (mode == 1u) command = 1u;
    else return UINT32_MAX;
    uint8_t state;
    do {
        gx8002_uart_stage2_spi_read_34a4(5u, &state, 1u);
    } while ((state & 1u) != 0u);
    gx8002_uart_stage2_spi_write_raw_3524(6u, 0, 0u);
    gx8002_uart_stage2_spi_write_raw_3524(command, buffer, bytes);
    return 0;
}
