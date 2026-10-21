/* Pinned FlashDB read_sector_info, with flash/cache/traversal children explicit. */
#include <stdbool.h>
#include <stdint.h>

struct sector_info {
    uint8_t check_ok;
    uint8_t store;
    uint8_t dirty;
    uint8_t pad;
    uint32_t addr;
    uint32_t magic;
    uint32_t combined;
    uint32_t remain;
    uint32_t empty_kv;
};
struct sector_header {
    uint8_t store[1];
    uint8_t dirty[1];
    uint8_t pad[2];
    uint32_t magic;
    uint32_t combined;
    uint32_t reserved;
};
struct kv_record {
    uint8_t status;
    uint8_t crc_is_ok;
    uint8_t body[6];
    uint32_t len;
    uint8_t tail[68];
    uint32_t start;
    uint32_t value;
};

extern const struct sector_info *g2_flashdb_sector_cache_lookup(uint32_t db, uint32_t address);
extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address, uint32_t buf, uint32_t size);
extern uint32_t g2_flashdb_get_status(const uint8_t *table, uint32_t count);
extern uint32_t g2_flashdb_read_kv(uint32_t db, struct kv_record *kv);
extern uint32_t g2_flashdb_next_kv_addr(uint32_t db, const struct sector_info *sector,
                                         const struct kv_record *kv);
extern uint32_t g2_flashdb_continue_ff_addr(uint32_t db, uint32_t start, uint32_t end);
extern void g2_flashdb_update_sector_cache(uint32_t db, const struct sector_info *sector);

uint32_t g2_flashdb_read_sector_info(uint32_t db, uint32_t address,
                                      struct sector_info *sector, bool traversal)
{
    uint32_t sec_size = *(const uint32_t *)(uintptr_t)(db + 12u);
    struct sector_header header = {0};
    uint32_t result = 0;
    /* Pinned FDB_ASSERT requires aligned address and nonnull sector. */
    const struct sector_info *cache = g2_flashdb_sector_cache_lookup(db, address);
    if (cache && (!traversal || cache->empty_kv != UINT32_MAX)) {
        const uint8_t *from = (const uint8_t *)cache;
        uint8_t *to = (uint8_t *)sector;
        for (uint32_t i = 0; i < 24u; ++i) to[i] = from[i];
        return result;
    }

    (void)g2_flashdb_flash_read(db, address, (uint32_t)(uintptr_t)&header, 16u);
    sector->store = 0;
    sector->dirty = 0;
    sector->addr = address;
    sector->magic = header.magic;
    if (sector->magic != UINT32_C(0x30424446) ||
        (header.combined != UINT32_MAX && header.combined != 0u)) {
        sector->check_ok = 0;
        sector->combined = UINT32_MAX;
        return 8u;
    }
    sector->check_ok = 1;
    sector->combined = header.combined;
    sector->store = (uint8_t)g2_flashdb_get_status(header.store, 4u);
    sector->dirty = (uint8_t)g2_flashdb_get_status(header.dirty, 4u);
    if (traversal) {
        sector->remain = 0;
        sector->empty_kv = sector->addr + 16u;
        if (sector->store == 1u) {
            sector->remain = sec_size - 16u;
        } else if (sector->store == 2u) {
            struct kv_record kv;
            sector->remain = sec_size - 16u;
            kv.start = sector->addr + 16u;
            do {
                (void)g2_flashdb_read_kv(db, &kv);
                if (!kv.crc_is_ok && kv.status != 1u && kv.status != 5u) {
                    sector->remain = 0;
                    result = 2u;
                    break;
                }
                sector->empty_kv += kv.len;
                sector->remain -= kv.len;
            } while ((kv.start = g2_flashdb_next_kv_addr(db, sector, &kv)) != UINT32_MAX);
            uint32_t ff = g2_flashdb_continue_ff_addr(db, sector->empty_kv,
                                                       sector->addr + sec_size);
            if (sector->empty_kv != ff) {
                sector->empty_kv = ff;
                sector->remain = sec_size - (ff - sector->addr);
            }
        }
        g2_flashdb_update_sector_cache(db, sector);
    } else {
        cache = g2_flashdb_sector_cache_lookup(db, sector->addr);
        if (!cache) {
            sector->empty_kv = UINT32_MAX;
            sector->remain = 0;
            g2_flashdb_update_sector_cache(db, sector);
        }
    }
    return result;
}
