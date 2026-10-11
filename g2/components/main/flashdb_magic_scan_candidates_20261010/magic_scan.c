/* Pinned FlashDB find_next_kv_addr, with cache and flash I/O explicit. */
#include <stdint.h>

extern const void *g2_flashdb_sector_cache_lookup(uint32_t db, uint32_t sector_addr);
extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                                      uint32_t buffer, uint32_t size);

uint32_t g2_flashdb_find_next_kv_addr(uint32_t db, uint32_t start, uint32_t end)
{
    uint8_t buf[32];
    uint32_t original = start;
    uint32_t sector_size = *(const uint32_t *)(uintptr_t)(db + 12u);
    const uint8_t *sector = g2_flashdb_sector_cache_lookup(
        db, (start / sector_size) * sector_size);
    if (sector && start == *(const uint32_t *)(const void *)(sector + 20u))
        return UINT32_MAX;

    for (; start < end && start + 32u < end; start += 28u) {
        if (g2_flashdb_flash_read(db, start, (uint32_t)(uintptr_t)buf, 32u) != 0u)
            return UINT32_MAX;
        for (uint32_t i = 0; i < 28u && start + i < end; ++i) {
            uint32_t magic = (uint32_t)buf[i] | ((uint32_t)buf[i+1] << 8) |
                             ((uint32_t)buf[i+2] << 16) | ((uint32_t)buf[i+3] << 24);
            if (magic == UINT32_C(0x3030564b) && start + i - 4u >= original)
                return start + i - 4u;
        }
    }
    return UINT32_MAX;
}
