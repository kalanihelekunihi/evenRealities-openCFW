/* SPDX-License-Identifier: MIT
 * Native B stage1 controller/profile initialization 0x100010e2..0x10001222.
 * This is entered only when the cached JEDEC word is not 0x00ffffff.
 * Native SPI transactions remain separate source/contract functions.
 */
#include <stdint.h>
extern volatile uint32_t gx8002_stage1_flash_jedec;

extern uint32_t gx8002_image_b_stage1_flash_transaction_10000edc(
    uint32_t command, uint8_t *destination, uint32_t bytes);
extern uint32_t gx8002_image_b_stage1_flash_write_transaction_10000f5c(
    uint32_t command, const uint8_t *source, uint32_t bytes);

static void wait_status_clear(uint8_t *status)
{
    do {
        (void)gx8002_image_b_stage1_flash_transaction_10000edc(
            5u, status, 1u);
    } while ((*status & 1u) != 0u);
}

void gx8002_image_b_stage1_flash_initialize_100010e2(void)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const chip_select =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
    volatile uint32_t *const aux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);
    volatile uint32_t *const cached_id =
        &gx8002_stage1_flash_jedec;
    uint8_t buffer[3];
    uint8_t second_status;
    aux[0x10u / 4u] = 1u;
    spi[0x08u / 4u] = 0u;
    spi[0x2cu / 4u] = 0u;
    chip_select[0x70u / 4u] = 1u;
    spi[0x14u / 4u] = 2u;
    spi[0x1cu / 4u] = 31u;
    spi[0x08u / 4u] = 1u;
    if (gx8002_image_b_stage1_flash_transaction_10000edc(
            159u, buffer, 3u) != 0u) return;
    uint32_t id = ((uint32_t)buffer[0] << 16) |
                  ((uint32_t)buffer[1] << 8) | buffer[2];
    *cached_id = id;
    if (id != UINT32_C(0x854012) &&
        id != UINT32_C(0x1c3812) && id != UINT32_C(0x1c3813) &&
        id != UINT32_C(0x856013) && id != UINT32_C(0x856014)) {
        (void)gx8002_image_b_stage1_flash_transaction_10000edc(
            53u, &buffer[0], 1u);
        if ((buffer[0] & 2u) != 0u) return;
        second_status = (uint8_t)(buffer[0] | 2u);
        wait_status_clear(&buffer[0]);
        (void)gx8002_image_b_stage1_flash_write_transaction_10000f5c(
            6u, (const uint8_t *)0, 0u);
        (void)gx8002_image_b_stage1_flash_write_transaction_10000f5c(
            49u, &second_status, 1u);
        wait_status_clear(&buffer[0]);
    } else {
        (void)gx8002_image_b_stage1_flash_transaction_10000edc(
            5u, &buffer[0], 1u);
        (void)gx8002_image_b_stage1_flash_transaction_10000edc(
            53u, &second_status, 1u);
        buffer[1] = second_status;
        if ((second_status & 2u) != 0u) return;
        buffer[1] = (uint8_t)(second_status | 2u);
        wait_status_clear(&second_status);
        (void)gx8002_image_b_stage1_flash_write_transaction_10000f5c(
            6u, (const uint8_t *)0, 0u);
        (void)gx8002_image_b_stage1_flash_write_transaction_10000f5c(
            1u, buffer, 2u);
        wait_status_clear(&second_status);
    }
}
