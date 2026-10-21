#include <stdint.h>

/* Pinned FlashDB fdb_utils.c _fdb_flash_read in FAL mode. */
extern int32_t g2_flashdb_partition_read(uint32_t partition, uint32_t address,
                                         uint32_t buffer, uint32_t size);

uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                               uint32_t buffer, uint32_t size)
{
    if (*(volatile uint8_t *)(uintptr_t)(db + 25u) != 0u)
        return 2u; /* FDB_READ_ERR: file mode disabled in this build. */
    uint32_t partition = *(volatile uint32_t *)(uintptr_t)(db + 8u);
    return g2_flashdb_partition_read(partition, address, buffer, size) < 0
               ? 2u : 0u;
}
