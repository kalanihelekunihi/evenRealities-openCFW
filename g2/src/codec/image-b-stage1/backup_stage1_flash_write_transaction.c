/* SPDX-License-Identifier: MIT
 * Native B stage1 SPI write transaction 0x10000f5c..0x10000fda.
 * The zero-byte command case still configures registers and waits.
 */
#include <stdint.h>

uint32_t gx8002_image_b_stage1_flash_write_transaction_10000f5c(
    uint32_t command, const uint8_t *source, uint32_t bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const chip_select =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    while ((spi[0x28u / 4u] & 1u) != 0u) {}
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x00u / 4u] = 1031u;
    spi[0x04u / 4u] = bytes;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = bytes << 16;
    chip_select[0x74u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) {}
        spi[0x60u / 4u] = source[i];
    }
    while (spi[0x20u / 4u] != 0u) {}
    uint32_t status;
    do {
        status = spi[0x28u / 4u] & 1u;
    } while (status != 0u);
    return status;
}
