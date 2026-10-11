#include <stdint.h>

typedef struct {
    uint32_t buf;
    uint32_t size;
    uint32_t reserved0;
    uint32_t reserved1;
    uint32_t saved_len;
} g2_flashdb_blob;
_Static_assert(sizeof(g2_flashdb_blob) == 20, "ARM FlashDB blob size");

extern uint32_t g2_flashdb_get_kv(uint32_t db, uint32_t key,
                                  uint32_t buf, uint32_t size,
                                  uint32_t *saved_len);
extern uint32_t g2_flashdb_db_path(uint32_t db);
extern void g2_flashdb_print(uint32_t format, ...);

static const char initialized_prefix[] = "[FlashDB][kv]";
static const char pair_format[] = "[%s][%s] ";
static const char init_error[] = "Error: KV (%s) isn't initialize OK.\n";

/* Pinned FlashDB fdb_kv_get_blob, bound to stock 0x54454a local ABI. */
uint32_t g2_flashdb_candidate_get_blob(uint32_t db, uint32_t key,
                                       g2_flashdb_blob *blob)
{
    if (*(volatile uint8_t *)(uintptr_t)(db + 24u) == 0u) {
        g2_flashdb_print((uint32_t)(uintptr_t)initialized_prefix);
        uint32_t db_type = g2_flashdb_db_path(db);
        uint32_t name = *(volatile uint32_t *)(uintptr_t)db;
        g2_flashdb_print((uint32_t)(uintptr_t)pair_format,
                         name, db_type);
        name = *(volatile uint32_t *)(uintptr_t)db;
        g2_flashdb_print((uint32_t)(uintptr_t)init_error, name);
        return 0u;
    }

    uint32_t lock = *(volatile uint32_t *)(uintptr_t)(db + 28u);
    if (lock)
        ((void (*)(uint32_t))(uintptr_t)lock)(db);
    uint32_t read_len = g2_flashdb_get_kv(db, key, blob->buf, blob->size,
                                          &blob->saved_len);
    uint32_t unlock = *(volatile uint32_t *)(uintptr_t)(db + 32u);
    if (unlock)
        ((void (*)(uint32_t))(uintptr_t)unlock)(db);
    return read_len;
}
