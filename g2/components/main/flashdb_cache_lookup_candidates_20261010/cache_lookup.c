/* Pinned FlashDB get_kv_from_cache, 64-row stock KV cache layout. */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

struct kv_cache_node {
    uint16_t name_crc;
    uint16_t active;
    uint32_t addr;
};
struct kv_cache_db {
    uint8_t prefix[168];
    struct kv_cache_node kv_cache_table[64];
};

extern uint32_t g2_flashdb_crc32(uint32_t seed, const void *data, size_t size);
extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                                      uint32_t buffer, uint32_t size);

static int equal_name(const char *name, const uint8_t *saved, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        uint8_t a = (uint8_t)name[i], b = saved[i];
        if (a != b) return 0;
        if (a == 0) return 1;
    }
    return 1;
}

bool g2_flashdb_cache_lookup(struct kv_cache_db *db, const char *name,
                             size_t name_len, uint32_t *addr)
{
    uint16_t name_crc = (uint16_t)(g2_flashdb_crc32(0, name, name_len) >> 16);
    for (size_t i = 0; i < 64; ++i) {
        struct kv_cache_node *row = &db->kv_cache_table[i];
        if (row->addr != UINT32_MAX && row->name_crc == name_crc) {
            uint8_t saved_name[64];
            volatile uint8_t *zero = saved_name;
            for (size_t j = 0; j < 64; ++j) zero[j] = 0;
            (void)g2_flashdb_flash_read((uint32_t)(uintptr_t)db,
                                        row->addr + 24u,
                                        (uint32_t)(uintptr_t)saved_name, 64);
            if (equal_name(name, saved_name, name_len)) {
                *addr = row->addr;
                row->active = row->active >= 0xffbfu ? 0xffffu
                                                     : (uint16_t)(row->active + 64u);
                return true;
            }
        }
    }
    return false;
}
