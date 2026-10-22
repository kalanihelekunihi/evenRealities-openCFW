/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10023fa4..0x100240f5, direct C-SKY SPI read sequence.
 * The native signed min.s32 instruction supplies each 32-byte chunk.
 */
#include <stdint.h>
#include "resident_product_data.h"

extern void gx8002_resident_flash_wait_bus_2364c(void);
extern uint32_t gx8002_resident_flash_wait_tx_empty_23670(void);
extern uint32_t gx8002_resident_flash_wait_rx_empty_2365c(void);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern void gx8002_resident_flash_addr_to_command_23b8c(
    const volatile uint32_t *, uint32_t, uint8_t *);

/* Stock 0x10023FA4 (gx8002_flash_otp_read) */
int32_t gx8002_resident_flash_otp_read_23fa4(
    uint32_t offset, uint8_t *destination, uint32_t bytes)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct gx8002_flash_catalog_entry *const selected =
        (const volatile struct gx8002_flash_catalog_entry *)(uintptr_t)state[3];
    volatile struct gx8002_otp_config *const otp = selected->otp;
    if (bytes == 0u || otp->region_size < offset + bytes) return -1;
    uint32_t address = otp->field0 + offset +
        (otp->current_region & 7u) * otp->field4;
    uint16_t type = (uint16_t)(selected->jedec >> 16);
    if (type != 0x5eu && type != 0x85u) return -1;

    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const mux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300090);
    volatile uint8_t *const command =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x200264f4);
    gx8002_resident_flash_wait_ready_2375c();
    command[0] = 0x48u;
    gx8002_resident_flash_addr_to_command_23b8c(
        &state[2], address, (uint8_t *)(uintptr_t)command);
    uint32_t remaining = bytes;
    uint32_t completed = 0u;
    do {
        int32_t signed_chunk = (int32_t)remaining < 32 ?
            (int32_t)remaining : 32;
        uint32_t chunk = (uint32_t)signed_chunk;
        if (chunk != 0u) {
            uint32_t command_bytes = state[2] + 2u;
            gx8002_resident_flash_wait_bus_2364c();
            spi[0x08u / 4u] = 0u;
            *mux = 2u;
            spi[0x4cu / 4u] = 0u;
            spi[0x10u / 4u] = 0u;
            spi[0] = 0x407u;
            spi[0x04u / 4u] = state[2] + 1u;
            spi[0x18u / 4u] = 0u;
            *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4) = 0u;
            spi[0x08u / 4u] = 1u;
            for (uint32_t i = 0; i != command_bytes; ++i) {
                while ((spi[0x28u / 4u] & 2u) == 0u) { }
                spi[0x60u / 4u] = command[i];
            }
            spi[0x10u / 4u] = 1u;
            gx8002_resident_flash_wait_tx_empty_23670();
            spi[0x08u / 4u] = 0u;
            spi[0x10u / 4u] = 0u;
            spi[0] = 0x807u;
            spi[0x04u / 4u] = chunk - 1u;
            spi[0x18u / 4u] = 0u;
            spi[0x54u / 4u] = 7u;
            spi[0x4cu / 4u] = 1u;
            spi[0x08u / 4u] = 1u;
            spi[0x10u / 4u] = 1u;
            spi[0x60u / 4u] = 0u;
            for (uint32_t i = 0; i != chunk; ++i) {
                while ((spi[0x28u / 4u] & 8u) == 0u) { }
                destination[i] = (uint8_t)spi[0x60u / 4u];
            }
            gx8002_resident_flash_wait_rx_empty_2365c();
            spi[0x08u / 4u] = 0u;
            spi[0x4cu / 4u] = 0u;
            *mux = 3u;
            *mux = 1u;
            spi[0x08u / 4u] = 1u;
        }
        address += chunk;
        remaining -= chunk;
        destination += chunk;
        completed += chunk;
        gx8002_resident_flash_addr_to_command_23b8c(
            &state[2], address, (uint8_t *)(uintptr_t)command);
    } while (remaining != 0u);
    gx8002_resident_flash_wait_ready_2375c();
    return (int32_t)completed;
}
