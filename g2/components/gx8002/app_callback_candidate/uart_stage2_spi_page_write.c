/* SPDX-License-Identifier: MIT
 * Stock UART stage2 0x100038fc: page-bounded SPI flash programming.
 * The descriptor callback at +0x18 is an imported product contract.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_spi_read_34a4(uint32_t, uint8_t *, uint32_t);
extern void gx8002_uart_stage2_spi_write_raw_3524(
    uint32_t, const uint8_t *, uint32_t);

typedef void (*stage2_spi_program_page)(uint32_t, const uint8_t *, uint32_t);

uint32_t gx8002_uart_stage2_spi_page_write_38fc(
    uint32_t address, const uint8_t *data, uint32_t length)
{
    uint8_t status;
    do {
        gx8002_uart_stage2_spi_read_34a4(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    gx8002_uart_stage2_spi_write_raw_3524(6u, 0, 0u);

    uintptr_t descriptor = UINT32_C(0x200091c4);
    stage2_spi_program_page program = (stage2_spi_program_page)(uintptr_t)
        *(volatile const uint32_t *)(descriptor + 0x18u);
    if ((address & 0xffu) + length <= 0x100u) {
        program(address, data, length);
        return 0u;
    }

    uint32_t offset = 0x100u - (address & 0xffu);
    program(address, data, offset);
    while (offset < length) {
        uint32_t remainder = length - offset;
        uint32_t chunk = remainder < 0x100u ? remainder : 0x100u;
        gx8002_uart_stage2_spi_write_raw_3524(6u, 0, 0u);
        program(address + offset, data + offset, chunk);
        offset += chunk;
    }
    return 0u;
}
