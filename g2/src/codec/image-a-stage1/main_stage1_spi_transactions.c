/* SPDX-License-Identifier: MIT
 * BINH A stage-1 SPI write/read transactions at 0x10000b5c and 0x10000bbc.
 * Register order and polling are reconstructed from the locked C-SKY code.
 * The controller's physical responses remain hardware inputs.
 */
#include <stdint.h>

extern uint32_t gx8002_image_a_stage1_wait_bus_10000b4c(void);

__attribute__((used, section(".spl_a.flash_write")))
uint32_t gx8002_image_a_stage1_flash_write_10000b5c(
    uint32_t command, const uint8_t *source, uint32_t bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    (void)gx8002_image_a_stage1_wait_bus_10000b4c();
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x00u / 4u] = 1031u;
    spi[0x04u / 4u] = bytes;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = bytes << 16;
    control[0x74u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) {}
        spi[0x60u / 4u] = source[i];
    }
    uint32_t fifo_count;
    do {
        fifo_count = spi[0x20u / 4u];
    } while (fifo_count != 0u);
    (void)gx8002_image_a_stage1_wait_bus_10000b4c();
    return fifo_count;
}

__attribute__((used, section(".spl_a.flash_transaction")))
uint32_t gx8002_image_a_stage1_flash_transaction_10000bbc(
    uint32_t command, uint8_t *destination, uint32_t bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    (void)gx8002_image_a_stage1_wait_bus_10000b4c();
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x00u / 4u] = 3079u;
    spi[0x04u / 4u] = bytes - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0u;
    control[0x74u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) {}
        destination[i] = (uint8_t)spi[0x60u / 4u];
    }
    uint32_t fifo_count;
    do {
        fifo_count = spi[0x24u / 4u];
    } while (fifo_count != 0u);
    (void)gx8002_image_a_stage1_wait_bus_10000b4c();
    return fifo_count;
}
