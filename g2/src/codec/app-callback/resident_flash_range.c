/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash range adapter, stock 0x10023a90 and 0x10023ab8.
 */
#include <stdint.h>

extern int32_t gx8002_resident_flash_block_bounds_238a4(
    uint32_t address, uint32_t *begin, uint32_t *end);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);

/* Stock 0x10023A90 (gx8002_flash_block_range) */
void gx8002_resident_flash_block_range_23a90(
    uint32_t address, uint32_t bytes, uint32_t *begin, uint32_t *end)
{
    uint32_t first_end;
    if (gx8002_resident_flash_block_bounds_238a4(
            address, begin, &first_end) == 0) {
        (void)gx8002_resident_flash_block_bounds_238a4(
            address + bytes - 1u, &first_end, end);
    }
}

/* Stock 0x10023AB8 (gx8002_flash_sync) */
void gx8002_resident_flash_sync_23ab8(void)
{
    gx8002_resident_flash_wait_ready_2375c();
}
