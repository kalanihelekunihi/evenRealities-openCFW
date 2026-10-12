/* SPDX-License-Identifier: MIT
 * Stock stage1 SPI read transaction 0x10000edc..0x10000f5a.
 * Register order and blocking reads are retained from native instructions.
 * Physical SPI controller behavior remains an external hardware contract.
 */
#include <stdint.h>

uint32_t gx8002_image_b_stage1_flash_transaction_10000edc(
    uint32_t command, uint8_t *destination, uint32_t bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const chip_select =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    while ((spi[0x28u / 4u] & 1u) != 0u) {}
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x00u / 4u] = 3079u;
    spi[0x04u / 4u] = bytes - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0u;
    chip_select[0x74u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) {}
        destination[i] = (uint8_t)spi[0x60u / 4u];
    }
    while (spi[0x24u / 4u] != 0u) {}
    uint32_t status;
    do {
        status = spi[0x28u / 4u] & 1u;
    } while (status != 0u);
    return status;
}
