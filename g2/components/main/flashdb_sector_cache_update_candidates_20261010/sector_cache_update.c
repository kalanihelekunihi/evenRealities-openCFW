/* Pinned FlashDB update_sector_cache, 64-entry table at DB offset 680. */
#include <stdint.h>

void g2_flashdb_update_sector_cache(uint32_t db, const void *sector_ptr)
{
    const uint8_t *sector = sector_ptr;
    uint8_t *table = (uint8_t *)(uintptr_t)(db + 680u);
    uint32_t address = *(const uint32_t *)(const void *)(sector + 4u);
    uint32_t empty_index = 64u;
    for (uint32_t i = 0; i < 64u; ++i) {
        uint8_t *entry = table + i * 24u;
        uint32_t entry_address = *(const uint32_t *)(const void *)(entry + 4u);
        if (entry_address == address) {
            if (sector[0]) {
                for (uint32_t j = 0; j < 24u; ++j) entry[j] = sector[j];
            } else {
                *(uint32_t *)(void *)(entry + 4u) = UINT32_MAX;
            }
            return;
        } else if (entry_address == UINT32_MAX) {
            empty_index = i;
        }
    }
    if (sector[0] && empty_index < 64u) {
        uint8_t *entry = table + empty_index * 24u;
        for (uint32_t j = 0; j < 24u; ++j) entry[j] = sector[j];
    }
}
