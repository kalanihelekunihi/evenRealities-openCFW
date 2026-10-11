/* Pinned FlashDB _fdb_flash_write in FAL mode. */
#include <stdint.h>

extern int32_t g2_flashdb_partition_write(uint32_t partition, uint32_t address,
                                           uint32_t buffer, uint32_t size);

uint32_t g2_flashdb_flash_write(uint32_t db, uint32_t address,
                                 uint32_t buffer, uint32_t size, uint32_t sync)
{
    (void)sync; /* The pinned FAL-mode body ignores sync. */
    if (*(const uint8_t *)(uintptr_t)(db + 25u) != 0u) return 3u;
    uint32_t partition = *(const uint32_t *)(uintptr_t)(db + 8u);
    return g2_flashdb_partition_write(partition, address, buffer, size) < 0
               ? 3u : 0u;
}
