/* FlashDB 714d6159 update_kv_cache, with the recovered 64-entry KV layout. */
#include <stddef.h>
#include <stdint.h>

#define FDB_KV_CACHE_TABLE_SIZE 64u
#define FDB_DATA_UNUSED UINT32_MAX

struct kv_cache_node {
    uint16_t name_crc;
    uint16_t active;
    uint32_t addr;
};

struct kv_cache_db {
    uint8_t prefix[168];
    struct kv_cache_node kv_cache_table[FDB_KV_CACHE_TABLE_SIZE];
};

extern uint32_t g2_flashdb_crc32(uint32_t seed, const void *data, size_t size);

void g2_flashdb_cache_update(struct kv_cache_db *db, const char *name,
                             size_t name_len, uint32_t addr)
{
    size_t i, empty_index = FDB_KV_CACHE_TABLE_SIZE;
    size_t min_activity_index = FDB_KV_CACHE_TABLE_SIZE;
    uint16_t name_crc = (uint16_t)(g2_flashdb_crc32(0, name, name_len) >> 16);
    uint16_t min_activity = UINT16_MAX;

    for (i = 0; i < FDB_KV_CACHE_TABLE_SIZE; i++) {
        if (addr != FDB_DATA_UNUSED) {
            if (db->kv_cache_table[i].name_crc == name_crc) {
                db->kv_cache_table[i].addr = addr;
                return;
            } else if (db->kv_cache_table[i].addr == FDB_DATA_UNUSED &&
                       empty_index == FDB_KV_CACHE_TABLE_SIZE) {
                empty_index = i;
            } else if (db->kv_cache_table[i].addr != FDB_DATA_UNUSED) {
                if (db->kv_cache_table[i].active > 0)
                    db->kv_cache_table[i].active--;
                if (db->kv_cache_table[i].active < min_activity) {
                    min_activity_index = i;
                    min_activity = db->kv_cache_table[i].active;
                }
            }
        } else if (db->kv_cache_table[i].name_crc == name_crc) {
            db->kv_cache_table[i].addr = FDB_DATA_UNUSED;
            db->kv_cache_table[i].active = 0;
            return;
        }
    }
    if (empty_index < FDB_KV_CACHE_TABLE_SIZE) {
        db->kv_cache_table[empty_index].addr = addr;
        db->kv_cache_table[empty_index].name_crc = name_crc;
        db->kv_cache_table[empty_index].active = FDB_KV_CACHE_TABLE_SIZE;
    } else if (min_activity_index < FDB_KV_CACHE_TABLE_SIZE) {
        db->kv_cache_table[min_activity_index].addr = addr;
        db->kv_cache_table[min_activity_index].name_crc = name_crc;
        db->kv_cache_table[min_activity_index].active = FDB_KV_CACHE_TABLE_SIZE;
    }
}
