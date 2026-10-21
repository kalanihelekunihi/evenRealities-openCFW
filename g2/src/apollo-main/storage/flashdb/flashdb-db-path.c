#include <stdint.h>

/* Stock 0x585c94: pinned FlashDB _fdb_db_path local FAL-mode layout. */
uint32_t g2_flashdb_db_path(uint32_t db)
{
    if (*(volatile uint8_t *)(uintptr_t)(db + 25u) != 0u)
        return 0u;
    return *(volatile uint32_t *)(uintptr_t)(db + 8u) + 4u;
}
