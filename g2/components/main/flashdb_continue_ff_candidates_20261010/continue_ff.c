/* Pinned FlashDB _fdb_continue_ff_addr, one-bit write granularity. */
#include <stdint.h>

extern uint32_t g2_flashdb_flash_read(uint32_t db, uint32_t address,
                                      uint32_t buffer, uint32_t size);

uint32_t g2_flashdb_continue_ff_addr(uint32_t db, uint32_t start, uint32_t end)
{
    uint8_t buf[32];
    uint8_t last_data = 0u;
    uint32_t addr = start;
    for (; start < end; start += 32u) {
        uint32_t read_size = start + 32u < end ? 32u : end - start;
        (void)g2_flashdb_flash_read(db, start, (uint32_t)(uintptr_t)buf, read_size);
        for (uint32_t i = 0; i < read_size; ++i) {
            if (last_data != 0xffu && buf[i] == 0xffu)
                addr = start + i;
            last_data = buf[i];
        }
    }
    return last_data == 0xffu ? addr : end;
}
