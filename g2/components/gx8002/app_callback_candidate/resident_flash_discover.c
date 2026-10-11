/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash read/discovery chain: stock 0x1002364c, 0x1002365c,
 * 0x10023684, and 0x10024190. The 24-byte product flash table at
 * Product IDs come from the typed source catalog; its SRAM placement remains
 * a final linker/scatter-copy contract.
 */
#include <stdint.h>
#include "resident_product_data.h"

static volatile uint32_t *const spi =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);

void gx8002_resident_flash_wait_bus_2364c(void)
{
    while ((spi[0x28u / 4u] & 1u) != 0u) { }
}

uint32_t gx8002_resident_flash_wait_rx_empty_2365c(void)
{
    while (spi[0x24u / 4u] != 0u) { }
    gx8002_resident_flash_wait_bus_2364c();
    return 0u;
}

uint32_t gx8002_resident_flash_command_read_23684(
    uint32_t command, uint8_t *destination, int32_t bytes)
{
    gx8002_resident_flash_wait_bus_2364c();
    spi[0x4cu / 4u] = 0u;
    spi[0] = 0xc07u;
    spi[0x04u / 4u] = (uint32_t)bytes - 1u;
    spi[0x10u / 4u] = 1u;
    spi[0x18u / 4u] = 0u;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
    spi[0x08u / 4u] = 1u;
    spi[0x60u / 4u] = command;
    for (int32_t i = 0; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) { }
        destination[i] = (uint8_t)spi[0x60u / 4u];
    }
    gx8002_resident_flash_wait_rx_empty_2365c();
    return 0u;
}

_Static_assert(sizeof(struct gx8002_flash_catalog_entry) == 24,
               "resident flash catalog ABI");

int32_t gx8002_resident_flash_discover_24190(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const struct gx8002_flash_catalog_entry *const table =
        gx8002_flash_catalog_26624;
    uint8_t id[3];
    state[0] = UINT32_MAX;
    if ((int32_t)gx8002_resident_flash_command_read_23684(
            0x9fu, id, 3) < 0)
        return -1;
    uint32_t jedec = ((uint32_t)id[0] << 16) |
                     ((uint32_t)id[1] << 8) | id[2];
    for (uint32_t i = 0; table[i].jedec != 0u; ++i) {
        if (table[i].jedec == jedec) {
            state[0] = i;
            state[1] = table[i].capacity;
            state[2] = 3u;
            state[3] = (uint32_t)(uintptr_t)&table[i];
            return 0;
        }
    }
    for (uint32_t i = 0; table[i].jedec != 0u; ++i) {
        if (table[i].jedec == UINT32_C(0xc22016)) {
            state[0] = i;
            state[1] = table[i].capacity;
            state[2] = 3u;
            state[3] = (uint32_t)(uintptr_t)&table[i];
            break;
        }
    }
    return -2;
}
