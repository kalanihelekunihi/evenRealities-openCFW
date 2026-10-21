/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash protection lookup, stock 0x100238ec.
 * The selected product flash catalog and its protection map live in SRAM;
 * their entries are inputs, not reconstructed defaults.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern uint8_t gx8002_resident_flash_read_status_23734(void);
extern uint8_t gx8002_resident_flash_read_status2_23770(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t command, const uint8_t *data, int32_t bytes);

struct protect_entry {
    uint8_t status_value;
    uint8_t status_mask;
    uint8_t status2_value;
    uint8_t status2_mask;
    uint32_t protected_bytes;
};
_Static_assert(sizeof(struct protect_entry) == 8, "resident protect ABI");

struct protect_map {
    const struct protect_entry *entries;
    uint32_t count;
};

struct flash_selected {
    uint32_t field0;
    uint32_t jedec_id;
    uint32_t field8;
    uint32_t field12;
    const struct protect_map *protection;
};
_Static_assert(__builtin_offsetof(struct flash_selected, protection) == 16,
               "resident selected flash ABI");

/* 0x10023980: report whether the selected device has an active protection
 * map. Direct native instructions load state[3], then selected + 0x10,
 * then the map's first word; absent or zero returns UINT32_MAX. */
uint32_t gx8002_resident_flash_write_protect_mode_23980(void)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct flash_selected *const selected =
        (const volatile struct flash_selected *)(uintptr_t)state[3];
    const volatile struct protect_map *const map = selected->protection;
    if (map == 0) return UINT32_MAX;
    return *(const volatile uint32_t *)map == 0u ? UINT32_MAX : 1u;
}

int32_t gx8002_resident_flash_block_bounds_238a4(
    uint32_t address, uint32_t *begin, uint32_t *end)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    *begin = 0u;
    *end = 0u;
    if ((int32_t)state[0] < 0) return -1;
    uint32_t flash_size = state[1] & UINT32_C(0xfffff000);
    for (uint32_t block = 0u; block != flash_size; block += 0x1000u) {
        uint32_t next = block + 0x1000u;
        if (address >= block && address < next) {
            *begin = block;
            *end = next;
            return 0;
        }
    }
    return -1;
}

int32_t gx8002_resident_flash_write_protect_status_238ec(
    uint32_t *protected_bytes)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct flash_selected *const selected =
        (const volatile struct flash_selected *)(uintptr_t)state[3];
    *protected_bytes = 0u;
    const volatile struct protect_map *map = selected->protection;
    if (map != 0 && map->entries != 0) {
        gx8002_resident_flash_wait_ready_2375c();
        uint16_t type = (uint16_t)(selected->jedec_id >> 16);
        if (type == 0x5eu || type == 0x85u) {
            uint8_t status = gx8002_resident_flash_read_status_23734();
            uint8_t status2 = gx8002_resident_flash_read_status2_23770();
            map = selected->protection;
            for (uint32_t i = 0; i < map->count; ++i) {
                const volatile struct protect_entry *entry = &map->entries[i];
                if (entry->status_value == (status & entry->status_mask) &&
                    entry->status2_value == (status2 & entry->status2_mask)) {
                    *protected_bytes = entry->protected_bytes;
                    return 0;
                }
            }
        }
    }
    *protected_bytes = UINT32_MAX;
    return -1;
}

int32_t gx8002_resident_flash_write_protect_set_239a4(
    uint32_t requested_bytes, uint32_t *actual_bytes)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x200264e4);
    const volatile struct flash_selected *const selected =
        (const volatile struct flash_selected *)(uintptr_t)state[3];
    *actual_bytes = 0u;
    const volatile struct protect_map *map = selected->protection;
    if (map == 0 || map->entries == 0)
        return requested_bytes == 0u ? 0 : -1;
    gx8002_resident_flash_wait_ready_2375c();
    uint8_t desired_status = 0u;
    uint8_t mask_status = 0u;
    uint8_t desired_status2 = 0u;
    uint8_t mask_status2 = 0u;
    const volatile struct protect_entry *entry = map->entries;
    for (uint32_t i = 0; i < map->count &&
         entry->protected_bytes <= requested_bytes; ++i, ++entry) {
        desired_status = entry->status_value;
        mask_status = entry->status_mask;
        desired_status2 = entry->status2_value;
        mask_status2 = entry->status2_mask;
    }
    uint16_t type = (uint16_t)(selected->jedec_id >> 16);
    if (type != 0x5eu && type != 0x85u) return -1;
    uint8_t statuses[2];
    statuses[0] = desired_status |
        (gx8002_resident_flash_read_status_23734() & (uint8_t)~mask_status);
    statuses[1] = desired_status2 |
        (gx8002_resident_flash_read_status2_23770() & (uint8_t)~mask_status2);
    gx8002_resident_flash_wait_ready_2375c();
    gx8002_resident_flash_write_enable_2374c();
    gx8002_resident_flash_command_write_236dc(1u, statuses, 2);
    gx8002_resident_flash_wait_ready_2375c();
    uint32_t observed;
    if (gx8002_resident_flash_write_protect_status_238ec(&observed) == -1)
        return -1;
    *actual_bytes = observed;
    return 0;
}

void gx8002_resident_flash_write_protect_lock_23a70(uint32_t bytes)
{
    uint32_t observed;
    (void)gx8002_resident_flash_write_protect_set_239a4(bytes, &observed);
}

void gx8002_resident_flash_write_protect_unlock_23a80(void)
{
    uint32_t observed;
    (void)gx8002_resident_flash_write_protect_set_239a4(0u, &observed);
}
