/* Pinned FlashDB get_next_sector_addr, including uint32_t wrap semantics. */
#include <stdint.h>

uint32_t g2_flashdb_next_sector_addr(uint32_t db, const void *previous,
                                      uint32_t traversed_len)
{
    const uint8_t *sector = previous;
    uint32_t combined = *(const uint32_t *)(const void *)(sector + 12u);
    uint32_t sector_size = *(const uint32_t *)(uintptr_t)(db + 12u);
    uint32_t max_size = *(const uint32_t *)(uintptr_t)(db + 16u);
    uint32_t current_size = combined == UINT32_MAX ? sector_size
                                                   : combined * sector_size;
    if (traversed_len + current_size <= max_size) {
        uint32_t next = *(const uint32_t *)(const void *)(sector + 4u) + current_size;
        return next < max_size ? next : 0u;
    }
    return UINT32_MAX;
}
