/* Pinned FlashDB read_kv, with status, flash and diagnostic providers explicit. */
#include <stdint.h>
#include <stddef.h>

struct kv_header {
    uint8_t status_table[4];
    uint32_t magic;
    uint32_t len;
    uint32_t crc32;
    uint8_t name_len;
    uint8_t padding[3];
    uint32_t value_len;
};
struct kv_record {
    uint8_t status;
    uint8_t crc_is_ok;
    uint8_t name_len;
    uint8_t padding0[5];
    uint32_t len;
    uint32_t value_len;
    char name[64];
    uint32_t start;
    uint32_t value;
};

extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t addr, uint32_t buf, uint32_t size);
extern uint32_t g2_flashdb_get_status(const uint8_t *table, uint32_t status_count);
extern uint32_t g2_flashdb_write_status(uint32_t db, uint32_t addr, const uint8_t *table,
                                         uint32_t count, uint32_t status, uint32_t sync);
extern uint32_t g2_flashdb_crc32(uint32_t crc, const void *buf, size_t size);
extern uint32_t g2_flashdb_db_path(uint32_t db);
extern void g2_flashdb_print(uint32_t format, ...);

static const char prefix[] = "[FlashDB][kv]";
static const char pair[] = "[%s][%s] ";
static const char length_error[] = "Error: The KV @0x%08X length has an error.\n";
static const char crc_error[] = "Error: Read the KV (%.*s@0x%08X) CRC32 check failed!\n";

static void report_prefix(uint32_t db)
{
    g2_flashdb_print((uint32_t)(uintptr_t)prefix);
    uint32_t path = g2_flashdb_db_path(db);
    g2_flashdb_print((uint32_t)(uintptr_t)pair,
                     *(const uint32_t *)(uintptr_t)db, path);
}

uint32_t g2_flashdb_read_kv(uint32_t db, struct kv_record *kv)
{
    struct kv_header header;
    uint8_t buf[32];
    uint32_t crc = 0;
    uint32_t result = 0;
    (void)g2_flashdb_flash_read(db, kv->start, (uint32_t)(uintptr_t)&header, 24);
    kv->status = (uint8_t)g2_flashdb_get_status(header.status_table, 6);
    kv->len = header.len;
    uint32_t max_size = *(const uint32_t *)(uintptr_t)(db + 16u);
    if (kv->len == UINT32_MAX || kv->len > max_size || kv->len < 24u) {
        kv->len = 24u;
        if (kv->status != 5u) {
            kv->status = 5u;
            report_prefix(db);
            g2_flashdb_print((uint32_t)(uintptr_t)length_error, kv->start);
            (void)g2_flashdb_write_status(db, kv->start, header.status_table, 6, 5, 1);
        }
        kv->crc_is_ok = 0;
        return 2;
    }

    crc = g2_flashdb_crc32(crc, &header.name_len, 4);
    crc = g2_flashdb_crc32(crc, &header.value_len, 4);
    uint32_t payload_len = kv->len - 24u;
    for (uint32_t pos = 0; pos < payload_len;) {
        uint32_t size = pos + 32u < payload_len ? 32u : payload_len - pos;
        (void)g2_flashdb_flash_read(db, kv->start + 24u + pos,
                                     (uint32_t)(uintptr_t)buf, size);
        crc = g2_flashdb_crc32(crc, buf, size);
        pos += size;
    }
    uint32_t name_addr = kv->start + 24u;
    if (crc != header.crc32) {
        uint32_t name_len = header.name_len > 64u ? 64u : header.name_len;
        kv->crc_is_ok = 0;
        result = 2;
        (void)g2_flashdb_flash_read(db, name_addr,
                                     (uint32_t)(uintptr_t)kv->name, name_len);
        report_prefix(db);
        g2_flashdb_print((uint32_t)(uintptr_t)crc_error,
                         name_len, (uint32_t)(uintptr_t)kv->name, kv->start);
    } else {
        kv->crc_is_ok = 1;
        (void)g2_flashdb_flash_read(db, name_addr,
                                     (uint32_t)(uintptr_t)kv->name, header.name_len);
        kv->value = name_addr + header.name_len;
        kv->value_len = header.value_len;
        kv->name_len = header.name_len;
        uint32_t termination = header.name_len >= 64u ? 63u : header.name_len;
        kv->name[termination] = '\0';
    }
    return result;
}
