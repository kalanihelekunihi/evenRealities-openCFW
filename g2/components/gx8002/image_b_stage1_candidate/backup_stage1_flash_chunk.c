/* SPDX-License-Identifier: MIT
 * Native stage1 reader's 0x10001052..0x100010be chunk loop, expressed as
 * one bounded transaction per invocation. The caller owns 64 KiB chunking.
 * Source owns register sequence; actual SPI responses are hardware input.
 */
#include <stdint.h>
extern volatile uint32_t gx8002_stage1_flash_jedec;

void gx8002_image_b_stage1_flash_read_chunk_1000105a(
    uint32_t source_offset, uint8_t *destination, uint32_t bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const chip_select =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    volatile uint32_t *const flash_state =
        &gx8002_stage1_flash_jedec;
    if (bytes == 0u) return;
    while ((spi[0x28u / 4u] & 1u) != 0u) {}
    spi[0x4cu / 4u] = 0u;
    spi[0x08u / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0x00u / 4u] = UINT32_C(0x00800807);
    spi[0x04u / 4u] = bytes - 1u;
    spi[0x18u / 4u] = 0u;
    spi[0x54u / 4u] = 7u;
    if ((*flash_state + UINT32_C(0xffe3c7ee)) < 2u) {
        chip_select[0x74u / 4u] = UINT32_C(0x40003219);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 235u;
    } else {
        chip_select[0x74u / 4u] = UINT32_C(0x40004218);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 107u;
    }
    spi[0x64u / 4u] = source_offset;
    spi[0x10u / 4u] = 1u;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) {}
        destination[i] = (uint8_t)spi[0x60u / 4u];
    }
    while (spi[0x24u / 4u] != 0u) {}
    while ((spi[0x28u / 4u] & 1u) != 0u) {}
}
