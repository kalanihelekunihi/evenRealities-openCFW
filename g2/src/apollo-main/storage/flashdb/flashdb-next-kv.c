/* Pinned FlashDB get_next_kv_addr, with magic scan kept as a lower provider. */
#include <stdint.h>

extern uint32_t g2_flashdb_find_next_kv_addr(uint32_t db, uint32_t start,
                                              uint32_t end);

uint32_t g2_flashdb_next_kv_addr(uint32_t db, const void *sector_ptr,
                                  const void *kv_ptr)
{
    const uint8_t *sector = sector_ptr;
    const uint8_t *kv = kv_ptr;
    uint32_t sector_addr = *(const uint32_t *)(const void *)(sector + 4u);
    uint32_t sector_size = *(const uint32_t *)(uintptr_t)(db + 12u);
    uint32_t start = *(const uint32_t *)(const void *)(kv + 80u);
    if (sector[1] == 1u) return UINT32_MAX;
    if (start == UINT32_MAX) return sector_addr + 16u;
    if (start > sector_addr + sector_size) return UINT32_MAX;
    uint32_t kv_len = *(const uint32_t *)(const void *)(kv + 8u);
    uint32_t scan_start = start + (kv[1] ? kv_len : 1u);
    uint32_t scan_end = sector_addr + sector_size - 16u;
    uint32_t next = g2_flashdb_find_next_kv_addr(db, scan_start, scan_end);
    if (next == UINT32_MAX || next > sector_addr + sector_size || kv_len == 0u)
        return UINT32_MAX;
    return next;
}
