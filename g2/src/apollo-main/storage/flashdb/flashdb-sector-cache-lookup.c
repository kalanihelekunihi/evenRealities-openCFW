/* Pinned FlashDB get_sector_from_cache, recovered 64 x 24-byte layout. */
#include <stdint.h>

const void *g2_flashdb_sector_cache_lookup(uint32_t db, uint32_t sec_addr)
{
    const uint8_t *table = (const uint8_t *)(uintptr_t)(db + 680u);
    for (uint32_t i = 0; i < 64u; ++i) {
        const uint8_t *entry = table + i * 24u;
        if (*(const uint32_t *)(const void *)(entry + 4u) == sec_addr)
            return entry;
    }
    return 0;
}
