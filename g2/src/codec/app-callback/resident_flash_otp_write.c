/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10023eb8..0x10023f97, reconstructed from the native
 * C-SKY page-split loop and authenticated typed flash catalog.
 */
#include <stdint.h>
#include "resident_product_data.h"

extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);
extern void gx8002_resident_flash_addr_to_command_23b8c(
    const volatile uint32_t *, uint32_t, uint8_t *);
extern uint32_t gx8002_resident_flash_otp_transmit_23e14(
    uint32_t, const uint8_t *, uint32_t);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t, const uint8_t *, int32_t);

/* Stock 0x10023BD8 (gx8002_flash_otp_erase) */
uint32_t gx8002_resident_flash_otp_erase_23bd8(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct gx8002_flash_catalog_entry *const selected =
        (const volatile struct gx8002_flash_catalog_entry *)(uintptr_t)state[3];
    uint16_t type = (uint16_t)(selected->jedec >> 16);
    if (type == 0x5eu || type == 0x85u) {
        volatile struct gx8002_otp_config *const otp = selected->otp;
        uint32_t region = otp->current_region & 7u;
        uint32_t address = otp->field0 + region * otp->field4;
        volatile uint8_t *const command =
            (volatile uint8_t *)(uintptr_t)UINT32_C(0x200264f4);
        command[0] = 0x44u;
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        gx8002_resident_flash_addr_to_command_23b8c(
            &state[2], address, (uint8_t *)(uintptr_t)command);
        gx8002_resident_flash_command_write_236dc(
            command[0], (const uint8_t *)(uintptr_t)(command + 1), 3);
        gx8002_resident_flash_wait_ready_2375c();
    }
    return 0u;
}

/* Stock 0x10023EB8 (gx8002_flash_otp_write) */
uint32_t gx8002_resident_flash_otp_write_23eb8(
    uint32_t offset, const uint8_t *source, uint32_t bytes)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct gx8002_flash_catalog_entry *const selected =
        (const volatile struct gx8002_flash_catalog_entry *)(uintptr_t)state[3];
    volatile struct gx8002_otp_config *const otp = selected->otp;
    if (bytes == 0u || otp->region_size < offset + bytes)
        return UINT32_MAX;
    uint32_t address = otp->field0 + offset +
        (otp->current_region & 7u) * otp->field4;
    uint16_t type = (uint16_t)(selected->jedec >> 16);
    if (type != 0x5eu && type != 0x85u) return UINT32_MAX;

    gx8002_resident_flash_wait_ready_2375c();
    gx8002_resident_flash_write_enable_2374c();
    volatile uint8_t *const command =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x200264f4);
    command[0] = 0x42u;
    gx8002_resident_flash_addr_to_command_23b8c(
        &state[2], address, (uint8_t *)(uintptr_t)command);
    uint32_t page_offset = address & 0xffu;
    uint32_t command_bytes = state[2] + 1u;
    if (bytes + page_offset < 0x101u) {
        gx8002_resident_flash_otp_transmit_23e14(
            command_bytes, source, bytes);
        gx8002_resident_flash_wait_ready_2375c();
        return bytes;
    }

    uint32_t consumed = 0x100u - page_offset;
    gx8002_resident_flash_otp_transmit_23e14(
        command_bytes, source, consumed);
    while (consumed < bytes) {
        gx8002_resident_flash_addr_to_command_23b8c(
            &state[2], address + consumed,
            (uint8_t *)(uintptr_t)command);
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        uint32_t remaining = bytes - consumed;
        uint32_t chunk = remaining < 0x100u ? remaining : 0x100u;
        gx8002_resident_flash_otp_transmit_23e14(
            state[2] + 1u, source + consumed, chunk);
        consumed += chunk;
    }
    gx8002_resident_flash_wait_ready_2375c();
    return consumed;
}
