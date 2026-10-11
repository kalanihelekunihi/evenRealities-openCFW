/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash word transfer, stock 0x10023788 and 0x10023cac.
 * Register order and the product-ID branch follow the retained native code.
 */
#include <stdint.h>

extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_wait_rx_empty_2365c(void);
extern uint32_t gx8002_resident_flash_wait_tx_empty_23670(void);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);

static volatile uint32_t *const spi =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
static volatile uint32_t *const spi_extra =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4);

/* 0x1002381c: the native top-level read chunks at exactly 64 KiB and
 * dispatches via the selected product callback at state + 0x1c. */
uint32_t gx8002_resident_flash_read_2381c(
    uint32_t address, void *destination, uint32_t byte_count)
{
    gx8002_resident_flash_wait_ready_2375c();
    volatile const uint32_t *const state =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    uintptr_t output = (uintptr_t)destination;
    int32_t remaining = (int32_t)byte_count;
    while (remaining != 0) {
        /* Native min.s32 applies signed comparison even to a high-bit count. */
        int32_t signed_chunk = remaining < 0x10000 ? remaining : 0x10000;
        uint32_t chunk = (uint32_t)signed_chunk;
        uintptr_t callback = state[7];
        ((void (*)(uint32_t, void *, uint32_t))callback)(
            address, (void *)output, chunk);
        remaining -= signed_chunk;
        address += chunk;
        output += chunk;
    }
    return 0u;
}

/* 0x10023858: 14-entry native jump table at XIP 0x1020be1c. Each entry was
 * decoded from the authenticated XIP image; this switch names its targets. */
uint32_t gx8002_resident_flash_getinfo_23858(uint32_t query)
{
    volatile const uint32_t *const state =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    switch (query) {
    case 0u: case 12u: return 0u;
    case 1u: case 2u: {
        volatile const uint32_t *const selected =
            (volatile const uint32_t *)(uintptr_t)state[3];
        return selected[query - 1u];
    }
    case 3u: return state[1];
    case 4u: case 6u: case 10u: return UINT32_C(0x1000);
    case 5u: case 7u: case 11u: return state[1] >> 12;
    case 8u: return 256u;
    case 13u: return 1u;
    default: return UINT32_MAX;
    }
}

void gx8002_resident_flash_word_program_23788(
    uint32_t address, const uint32_t *source, uint32_t byte_count)
{
    uint32_t words = byte_count >> 2;
    gx8002_resident_flash_wait_bus_2364c();
    spi[0x08u / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0x41fu;
    spi[0x04u / 4u] = words - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0x20000u;
    *spi_extra = 0x218u;
    spi[0x50u / 4u] = 8u;
    spi[0x4cu / 4u] = 2u;
    spi[0x08u / 4u] = 1u;
    spi[0x64u / 4u] = 50u;
    spi[0x64u / 4u] = address;
    for (uint32_t i = 0; i < words; ++i) {
        while ((spi[0x28u / 4u] & 2u) == 0u) { }
        spi[0x60u / 4u] = source[i];
    }
    gx8002_resident_flash_wait_tx_empty_23670();
    gx8002_resident_flash_wait_ready_2375c();
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
}

uint32_t gx8002_resident_flash_word_read_23cac(
    uint32_t address, uint32_t *destination, uint32_t byte_count)
{
    if (byte_count == 0u) return 0u;
    uint32_t words = byte_count >> 2;
    gx8002_resident_flash_wait_bus_2364c();
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0] = 0x81fu;
    spi[0x04u / 4u] = words - 1u;
    spi[0x18u / 4u] = 0u;
    spi[0x54u / 4u] = 7u;
    spi[0x4cu / 4u] = 1u;
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile uint32_t *const selected =
        (const volatile uint32_t *)(uintptr_t)state[3];
    if ((uint32_t)(selected[1] + UINT32_C(0xffe3c7ee)) < 2u) {
        *spi_extra = UINT32_C(0x40003219);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 0xebu;
    } else {
        *spi_extra = UINT32_C(0x40004218);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 0x6bu;
    }
    spi[0x64u / 4u] = address;
    spi[0x10u / 4u] = 1u;
    for (uint32_t i = 0; i < words; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) { }
        destination[i] = spi[0x60u / 4u];
    }
    gx8002_resident_flash_wait_rx_empty_2365c();
    spi[0x08u / 4u] = 0u;
    spi[0x4cu / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    return 0u;
}
