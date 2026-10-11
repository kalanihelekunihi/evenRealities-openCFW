#include <stdint.h>

struct g2_flashdb_kv;
extern uint32_t g2_log_candidate_module_length(const uint8_t *text);
extern uint32_t g2_flashdb_cache_lookup(uint32_t db, uint32_t key,
                                        uint32_t length, uint32_t *address);
extern void g2_flashdb_read_kv(uint32_t db, struct g2_flashdb_kv *kv);
extern uint32_t g2_flashdb_find_no_cache(uint32_t db, uint32_t key,
                                          struct g2_flashdb_kv *kv);
extern void g2_flashdb_cache_update(uint32_t db, uint32_t key,
                                     uint32_t length, uint32_t address);

/* Pinned FlashDB find_kv local body at stock 0x54449a. */
uint32_t g2_flashdb_find_kv(uint32_t db, uint32_t key,
                            struct g2_flashdb_kv *kv)
{
    uint32_t key_length = g2_log_candidate_module_length((const uint8_t *)(uintptr_t)key);
    uint32_t *address = (uint32_t *)(void *)((uint8_t *)kv + 80u);
    if (g2_flashdb_cache_lookup(db, key, key_length, address)) {
        g2_flashdb_read_kv(db, kv);
        return 1u;
    }
    uint32_t found = g2_flashdb_find_no_cache(db, key, kv) & 0xffu;
    if (found)
        g2_flashdb_cache_update(db, key, key_length, *address);
    return found;
}
