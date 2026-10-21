/* Pinned FlashDB _fdb_get_status for one-bit write granularity. */
#include <stddef.h>
#include <stdint.h>

uint32_t g2_flashdb_get_status(const uint8_t *table, size_t status_num)
{
    size_t i = 0;
    size_t backup = --status_num;
    while (status_num--) {
        if ((table[status_num / 8u] & (0x80u >> (status_num % 8u))) == 0u)
            break;
        i++;
    }
    return (uint32_t)(backup - i);
}
