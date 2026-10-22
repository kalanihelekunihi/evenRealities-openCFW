/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash UID read, stock 0x10024104. The selected JEDEC
 * product descriptor and SPI MMIO are required runtime inputs.
 */
#include <stdint.h>

extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_wait_rx_empty_2365c(void);

/* Stock 0x10024104 (gx8002_flash_uid_read) */
int32_t gx8002_resident_flash_uid_read_24104(
    uint8_t *destination, int32_t requested, int32_t *actual)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint8_t *const selected =
        (const volatile uint8_t *)(uintptr_t)state[3];
    uint8_t type = selected[6];
    if (type != 0x85u && type != 0x5eu) {
        *actual = 0;
        return -1;
    }
    int32_t count = requested < 16 ? requested : 16;
    *actual = count;
    gx8002_resident_flash_wait_bus_2364c();
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0xc07u;
    spi[0x04u / 4u] = (uint32_t)count - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0x40000u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = 0x4bu;
    for (uint32_t i = 0; i < 4u; ++i) spi[0x60u / 4u] = 0u;
    uint32_t cursor = (uint32_t)(uintptr_t)destination;
    uint32_t end = cursor + (uint32_t)count;
    while (cursor != end) {
        while ((spi[0x28u / 4u] & 8u) == 0u) { }
        *(volatile uint8_t *)(uintptr_t)cursor = (uint8_t)spi[0x60u / 4u];
        ++cursor;
    }
    gx8002_resident_flash_wait_rx_empty_2365c();
    return 0;
}
