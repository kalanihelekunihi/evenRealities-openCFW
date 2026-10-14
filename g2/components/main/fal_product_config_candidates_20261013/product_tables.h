/* SPDX-License-Identifier: MIT */
#ifndef G2_MAIN_FAL_PRODUCT_TABLES_H
#define G2_MAIN_FAL_PRODUCT_TABLES_H
#include <stdint.h>

enum { G2_FAL_NAME_BYTES = 24 };

struct g2_fal_partition_row {
    uint32_t magic_word;
    char name[G2_FAL_NAME_BYTES];
    char flash_name[G2_FAL_NAME_BYTES];
    int32_t offset;
    uint32_t len;
    uint32_t reserved;
};

struct g2_fal_flash_device {
    char name[G2_FAL_NAME_BYTES];
    uint32_t addr;
    uint32_t len;
    uint32_t blk_size;
    int (*init)(void);
    int (*read)(int32_t offset, uint8_t *buf, uint32_t size);
    int (*write)(int32_t offset, const uint8_t *buf, uint32_t size);
    int (*erase)(int32_t offset, uint32_t size);
    uint32_t write_gran;
};

extern const struct g2_fal_partition_row g2_fal_partition_rows[2];
extern const struct g2_fal_flash_device g2_fal_norflash;
extern const struct g2_fal_flash_device *const g2_fal_flash_device_table[1];
extern const uint32_t g2_fal_flash_device_count;
#endif
