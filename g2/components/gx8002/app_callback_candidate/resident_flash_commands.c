/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash command/status chain, stock 0x10023670..0x1002436b.
 * All routines use the native SPI MMIO region and the source-owned
 * read/bus lowers in resident_flash_discover.c.
 */
#include <stdint.h>

extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_command_read_23684(
    uint32_t command, uint8_t *destination, int32_t bytes);

static volatile uint32_t *const spi =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);

uint32_t gx8002_resident_flash_wait_tx_empty_23670(void)
{
    while (spi[0x20u / 4u] != 0u) { }
    gx8002_resident_flash_wait_bus_2364c();
    return 0u;
}

uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t command, const uint8_t *data, int32_t bytes)
{
    gx8002_resident_flash_wait_bus_2364c();
    spi[0x08u / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0x407u;
    spi[0x04u / 4u] = (uint32_t)bytes;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = (uint32_t)bytes << 16;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (int32_t i = 0; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) { }
        spi[0x60u / 4u] = data[i];
    }
    gx8002_resident_flash_wait_tx_empty_23670();
    return 0u;
}

uint8_t gx8002_resident_flash_read_status_23734(void)
{
    uint8_t result;
    gx8002_resident_flash_command_read_23684(5u, &result, 1);
    return result;
}

uint32_t gx8002_resident_flash_write_enable_2374c(void)
{
    gx8002_resident_flash_command_write_236dc(6u, 0, 0);
    return 0u;
}

uint32_t gx8002_resident_flash_wait_ready_2375c(void)
{
    while ((gx8002_resident_flash_read_status_23734() & 1u) != 0u) { }
    return 1u;
}

uint8_t gx8002_resident_flash_read_status2_23770(void)
{
    uint8_t result;
    gx8002_resident_flash_command_read_23684(0x35u, &result, 1);
    return result;
}

uint32_t gx8002_resident_flash_quad_enable_242b4(void)
{
    uint8_t state = gx8002_resident_flash_read_status2_23770();
    if ((state & 2u) == 0u) {
        state |= 2u;
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        gx8002_resident_flash_command_write_236dc(0x31u, &state, 1);
        gx8002_resident_flash_wait_ready_2375c();
    }
    return 0u;
}

uint32_t gx8002_resident_flash_quad_enable_pair_24330(void)
{
    uint8_t states[2] = {
        gx8002_resident_flash_read_status_23734(),
        gx8002_resident_flash_read_status2_23770()
    };
    if ((states[1] & 2u) == 0u) {
        states[1] |= 2u;
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        gx8002_resident_flash_command_write_236dc(1u, states, 2);
        gx8002_resident_flash_wait_ready_2375c();
    }
    return 0u;
}
