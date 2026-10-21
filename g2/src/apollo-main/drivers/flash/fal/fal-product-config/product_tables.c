/* SPDX-License-Identifier: MIT
 * Product FAL partition rows from authenticated Main flash at 0x6d5358.
 * The pinned RT-Thread FAL v1.0.0 definition fixes the ARM32 64-byte row
 * layout. It includes stdio.h, which this freestanding build does not use.
 */
#include <stddef.h>
#include <stdint.h>
#include "product_tables.h"

_Static_assert(sizeof(struct g2_fal_partition_row) == 64u, "FAL product row stride");
_Static_assert(offsetof(struct g2_fal_partition_row, flash_name) == 28u, "FAL device-name offset");
_Static_assert(offsetof(struct g2_fal_partition_row, offset) == 52u, "FAL flash offset field");

const struct g2_fal_partition_row g2_fal_partition_rows[2] = {
    { UINT32_C(0x45503130), "kvdb", "norflash", 0x01fc0000, 0x00038000u, 0u },
    { UINT32_C(0x45503130), "NVdb", "norflash", 0x01ff8000, 0x00008000u, 0u },
};

_Static_assert(sizeof(struct g2_fal_flash_device) == 56u, "FAL flash-device stride");
_Static_assert(offsetof(struct g2_fal_flash_device, read) == 40u, "FAL read callback offset");
_Static_assert(offsetof(struct g2_fal_flash_device, write_gran) == 52u, "FAL write granularity offset");

/* Original device callback pointers are 0x540ed1, 0x540ed5, 0x540f2d,
 * 0x540f85. Their named C bodies are separate unresolved source work. */
extern int g2_norflash_init_540ed0(void);
extern int g2_norflash_read_540ed4(int32_t offset, uint8_t *buf, uint32_t size);
extern int g2_norflash_write_540f2c(int32_t offset, const uint8_t *buf, uint32_t size);
extern int g2_norflash_erase_540f84(int32_t offset, uint32_t size);

const struct g2_fal_flash_device g2_fal_norflash = {
    "norflash", 0x01fc0000u, 0x02000000u, 0x1000u,
    g2_norflash_init_540ed0, g2_norflash_read_540ed4,
    g2_norflash_write_540f2c, g2_norflash_erase_540f84, 1u,
};

/* Product table at stock 0x78f0a4 and count at 0x78f0a8. */
const struct g2_fal_flash_device *const g2_fal_flash_device_table[1] = {
    &g2_fal_norflash,
};
const uint32_t g2_fal_flash_device_count = 1u;
