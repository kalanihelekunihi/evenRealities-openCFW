/* Pinned FlashDB find_kv_no_cache and find_kv_cb routing bodies. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

struct kv_record {
    uint8_t status;
    uint8_t crc_is_ok;
    uint8_t name_len;
    uint8_t pad[13];
    char name[64];
};

extern size_t g2_log_candidate_module_length(const char *text);
extern void g2_flashdb_kv_iterator(uint32_t db, void *kv, void *arg1,
                                    void *arg2,
                                    bool (*callback)(void *, void *, void *));

bool g2_flashdb_find_cb(void *record, void *arg1, void *arg2)
{
    struct kv_record *kv = record;
    const char *key = arg1;
    bool *found = arg2;
    size_t key_len = g2_log_candidate_module_length(key);
    if (key_len != kv->name_len) return false;
    if (kv->crc_is_ok && kv->status == 2) {
        for (size_t i = 0; i < key_len; ++i) {
            if ((uint8_t)kv->name[i] != (uint8_t)key[i]) return false;
            if (key[i] == '\0') break;
        }
        *found = true;
        return true;
    }
    return false;
}

bool g2_flashdb_find_no_cache(uint32_t db, const char *key, void *kv)
{
    bool found = false;
    g2_flashdb_kv_iterator(db, kv, (void *)key, &found, g2_flashdb_find_cb);
    return found;
}
