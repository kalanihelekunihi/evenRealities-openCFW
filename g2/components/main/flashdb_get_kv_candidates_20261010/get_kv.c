#include <stddef.h>
#include <stdint.h>

/* Pinned FlashDB fdb_kv layout under the recovered 64-byte name/short-enum
 * configuration. Only fields consumed by this body are semantic here. */
struct g2_flashdb_kv {
    uint8_t status, crc_is_ok, name_len, padding;
    uint32_t magic, len, value_len;
    char name[64];
    uint32_t addr_start, addr_value;
};
_Static_assert(sizeof(struct g2_flashdb_kv) == 88, "FlashDB KV ABI");
_Static_assert(offsetof(struct g2_flashdb_kv, value_len) == 12, "value length ABI");
_Static_assert(offsetof(struct g2_flashdb_kv, addr_value) == 84, "value address ABI");

extern uint32_t g2_flashdb_find_kv(uint32_t db, uint32_t key,
                                    struct g2_flashdb_kv *kv);
extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                                      uint32_t buffer, uint32_t length);

uint32_t g2_flashdb_get_kv(uint32_t db, uint32_t key, uint32_t buffer,
                           uint32_t length, uint32_t *value_length)
{
    struct g2_flashdb_kv kv;
    uint32_t read_length = 0u;
    if (g2_flashdb_find_kv(db, key, &kv)) {
        if (value_length)
            *value_length = kv.value_len;
        read_length = length > kv.value_len ? kv.value_len : length;
        if (buffer)
            (void)g2_flashdb_flash_read(db, kv.addr_value, buffer, read_length);
    } else if (value_length) {
        *value_length = 0u;
    }
    return read_length;
}
