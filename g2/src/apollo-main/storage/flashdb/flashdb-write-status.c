/* Pinned FlashDB one-bit _fdb_set_status/_fdb_write_status valid-input path. */
#include <stddef.h>
#include <stdint.h>

extern uint32_t g2_flashdb_flash_write(uint32_t db, uint32_t addr,
                                        uint32_t data, uint32_t size,
                                        uint32_t sync);

uint32_t g2_flashdb_set_status(uint8_t *table, uint32_t count, uint32_t index)
{
    uint32_t bytes = (count + 7u) >> 3;
    for (uint32_t i = 0; i < bytes; ++i) table[i] = 0xffu;
    if (index == 0u) return UINT32_MAX;
    uint32_t at = (index - 1u) >> 3;
    table[at] &= (uint8_t)(0xffu >> (index & 7u));
    return at;
}

uint32_t g2_flashdb_write_status(uint32_t db, uint32_t addr,
                                  uint8_t *table, uint32_t count,
                                  uint32_t index, uint32_t sync)
{
    /* The pinned FDB_ASSERT gate requires index < count and nonnull table. */
    uint32_t at = g2_flashdb_set_status(table, count, index);
    if (at == UINT32_MAX) return 0u;
    return (uint8_t)g2_flashdb_flash_write(db, addr + at,
                                            (uint32_t)(uintptr_t)&table[at], 1u, sync);
}
