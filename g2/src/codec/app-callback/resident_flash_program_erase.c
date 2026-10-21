/* SPDX-License-Identifier: MIT
 * Image-A SRAM page programming and erase graph, native 0x10023b8c,
 * 0x10023c34, 0x10023d58, and 0x10023e00.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t, const uint8_t *, int32_t);

typedef void (*flash_program_fn)(uint32_t, const uint32_t *, uint32_t);

void gx8002_resident_flash_addr_to_command_23b8c(
    const volatile uint32_t *address_bytes, uint32_t address, uint8_t *command)
{
    uint32_t count = *address_bytes;
    for (uint32_t i = 0; i < 4u; ++i) {
        uint32_t shift = ((count - 1u - i) * 8u) & 31u;
        command[i + 1u] = (uint8_t)(address >> shift);
    }
}

int32_t gx8002_resident_flash_page_program_23c34(
    uint32_t address, const uint8_t *source, uint32_t bytes)
{
    if (bytes == 0u) return 0;
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    if (state[1] < address + bytes) return -22;
    gx8002_resident_flash_wait_ready_2375c();
    gx8002_resident_flash_write_enable_2374c();
    flash_program_fn write =
        (flash_program_fn)(uintptr_t)state[6];
    uint32_t page_offset = address & 0xffu;
    if (bytes + page_offset < 0x101u) {
        write(address, (const uint32_t *)(const void *)source, bytes);
        return 0;
    }
    uint32_t consumed = 0x100u - page_offset;
    write(address, (const uint32_t *)(const void *)source, consumed);
    while (consumed < bytes) {
        uint32_t chunk = bytes - consumed;
        if (chunk > 0x100u) chunk = 0x100u;
        gx8002_resident_flash_write_enable_2374c();
        write(address + consumed,
              (const uint32_t *)(const void *)(source + consumed), chunk);
        consumed += chunk;
    }
    return 0;
}

int32_t gx8002_resident_flash_erase_23d58(uint32_t address, uint32_t bytes)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    uint32_t flash_size = state[1];
    if (address >= flash_size) return -22;
    uint32_t end = address + bytes;
    if (end > flash_size) end = flash_size;
    uint32_t sector = address & ~UINT32_C(0xfff);
    uint32_t remaining = end - sector;
    uint8_t *const command = (uint8_t *)(uintptr_t)(UINT32_C(0x200264e4) + 0x10u);
    while (remaining != 0u) {
        uint32_t budget = remaining < 0x1000u ? 0x1000u : remaining;
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        gx8002_resident_flash_addr_to_command_23b8c(&state[2], sector, command);
        if ((sector & 0x7fffu) == 0u && budget >= 0x10000u) {
            gx8002_resident_flash_command_write_236dc(0xd8u, command + 1u, 3);
            gx8002_resident_flash_wait_ready_2375c();
            sector += 0x10000u;
            remaining = budget - 0x10000u;
        } else {
            gx8002_resident_flash_command_write_236dc(0x20u, command + 1u, 3);
            gx8002_resident_flash_wait_ready_2375c();
            sector += 0x1000u;
            remaining = budget - 0x1000u;
        }
    }
    return 0;
}

void gx8002_resident_flash_chip_erase_23e00(void)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    (void)gx8002_resident_flash_erase_23d58(0u, state[1]);
}
