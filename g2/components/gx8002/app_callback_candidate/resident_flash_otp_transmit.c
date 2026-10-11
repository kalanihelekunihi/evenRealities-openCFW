/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10023e14..0x10023eb3, recovered from direct C-SKY
 * instructions in the authenticated image-A stage-2 SRAM body.
 * SPI and clock writes follow the native instruction order.
 */
#include <stdint.h>

extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_wait_tx_empty_23670(void);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);

uint32_t gx8002_resident_flash_otp_transmit_23e14(
    uint32_t command_bytes, const uint8_t *data, uint32_t data_bytes)
{
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const mux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300090);
    const volatile uint8_t *const command =
        (const volatile uint8_t *)(uintptr_t)UINT32_C(0x200264f4);

    gx8002_resident_flash_wait_bus_2364c();
    spi[0x08u / 4u] = 0u;
    *mux = 2u;
    spi[0x4cu / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0] = 0x407u;
    spi[0x04u / 4u] = data_bytes - 1u;
    spi[0x18u / 4u] = 0u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x50u / 4u] = 8u;
    spi[0x08u / 4u] = 1u;
    for (uint32_t i = 0; i != command_bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) { }
        spi[0x60u / 4u] = command[i];
    }
    spi[0x10u / 4u] = 1u;
    for (uint32_t i = 0; i != data_bytes; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) { }
        spi[0x60u / 4u] = data[i];
    }
    gx8002_resident_flash_wait_tx_empty_23670();
    spi[0x08u / 4u] = 0u;
    *mux = 3u;
    *mux = 1u;
    spi[0x08u / 4u] = 1u;
    gx8002_resident_flash_wait_ready_2375c();
    return 0u;
}
