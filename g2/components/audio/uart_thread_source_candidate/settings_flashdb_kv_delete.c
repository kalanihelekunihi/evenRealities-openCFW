/* Native FlashDB KV deletion 0x5448b4, reconstructed over the selected
 * FlashDB C provider set. The 88-byte KV descriptor layout is native. */
#include <stdint.h>

extern uint32_t g2_flashdb_find_kv(uint32_t db, uint32_t key, void *kv);
extern uint32_t g2_flashdb_write_status(uint32_t db, uint32_t address,
                                        uint8_t *table, uint32_t count,
                                        uint32_t status, uint32_t write_flag);
extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                                      uint32_t buffer, uint32_t size);
extern uint32_t g2_flashdb_get_status(const uint8_t *table, uint32_t count);
extern void g2_flashdb_cache_update(void *db, const char *name,
                                    uint32_t name_len, uint32_t address);
extern uint32_t g2_log_candidate_module_length(const uint8_t *text);
extern void *g2_flashdb_sector_cache_lookup(uint32_t db, uint32_t sector);

static uint32_t word_at(const void *p, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)p + offset);
}

uint32_t audio_flashdb_kv_delete(void *db, const char *key, void *kv,
                                 uint32_t final_status) {
    uint32_t local[22] = {0};
    if (kv == 0) {
        if (g2_flashdb_find_kv((uint32_t)(uintptr_t)db,
                               (uint32_t)(uintptr_t)key, local) == 0u)
            return 5u;
        kv = local;
    }
    uint8_t status_table[4];
    uint32_t address = word_at(kv, 0x50u);
    uint32_t result;
    if (final_status == 0u) {
        result = g2_flashdb_write_status((uint32_t)(uintptr_t)db, address,
                                         status_table, 6u, 3u, 0u);
        ((uint8_t *)db)[0xa4u] = 1u;
    } else {
        result = g2_flashdb_write_status((uint32_t)(uintptr_t)db, address,
                                         status_table, 6u, 4u, 1u);
        if (((uint8_t *)db)[0xa4u] == 0u && result == 0u) {
            const char *name = key ? key : (const char *)kv + 0x10u;
            uint32_t length = key ? g2_log_candidate_module_length((const uint8_t *)key)
                                  : ((const uint8_t *)kv)[2u];
            g2_flashdb_cache_update(db, name, length, UINT32_MAX);
        }
        ((uint8_t *)db)[0xa4u] = 0u;
    }
    uint32_t sector_size = word_at(db, 0xcu);
    uint32_t sector = sector_size * (address / sector_size);
    if (result == 0u) {
        (void)g2_flashdb_flash_read((uint32_t)(uintptr_t)db, sector + 1u,
                                    (uint32_t)(uintptr_t)status_table, 1u);
        if (g2_flashdb_get_status(status_table, 4u) == 1u) {
            result = g2_flashdb_write_status((uint32_t)(uintptr_t)db, sector + 1u,
                                             status_table, 4u, 2u, 1u);
            uint8_t *cache = g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)db, sector);
            if (cache) cache[2u] = 2u;
        }
    }
    return (uint8_t)result;
}
