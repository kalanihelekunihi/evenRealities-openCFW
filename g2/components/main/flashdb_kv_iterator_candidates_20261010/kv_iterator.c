/* Pinned FlashDB kv_iterator routing, with lower sector/KV providers explicit. */
#include <stdbool.h>
#include <stdint.h>

struct kv_sector {
    uint8_t status0;
    uint8_t store;
    uint8_t bytes[2];
    uint32_t addr;
    uint8_t tail[16];
};
struct kv_record {
    uint8_t prefix[80];
    uint32_t start;
};

extern uint32_t g2_flashdb_read_sector_info(uint32_t db, uint32_t address,
                                             struct kv_sector *sector, bool traversal);
extern uint32_t g2_flashdb_read_kv(uint32_t db, struct kv_record *kv);
extern uint32_t g2_flashdb_next_kv_addr(uint32_t db, const struct kv_sector *sector,
                                         const struct kv_record *kv);
extern uint32_t g2_flashdb_next_sector_addr(uint32_t db, const struct kv_sector *sector,
                                             uint32_t traversed);

void g2_flashdb_kv_iterator(uint32_t db, struct kv_record *kv,
                            void *arg1, void *arg2,
                            bool (*callback)(void *, void *, void *))
{
    struct kv_sector sector;
    uint32_t sec_addr = *(const uint32_t *)(uintptr_t)(db + 20u);
    uint32_t traversed_len = 0;
    do {
        traversed_len += *(const uint32_t *)(uintptr_t)(db + 12u);
        if (g2_flashdb_read_sector_info(db, sec_addr, &sector, false) != 0)
            continue;
        if (callback == 0) continue;
        if (sector.store == 2u || sector.store == 3u) {
            kv->start = sector.addr + 16u;
            do {
                (void)g2_flashdb_read_kv(db, kv);
                if (callback(kv, arg1, arg2)) return;
            } while ((kv->start = g2_flashdb_next_kv_addr(db, &sector, kv)) != UINT32_MAX);
        }
    } while ((sec_addr = g2_flashdb_next_sector_addr(db, &sector, traversed_len)) != UINT32_MAX);
}
