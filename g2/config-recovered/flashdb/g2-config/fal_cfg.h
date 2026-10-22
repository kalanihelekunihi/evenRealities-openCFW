/*
 * Production-excluded G2 FAL configuration recovered from official firmware.
 * SPDX-License-Identifier: Apache-2.0
 *
 * FlashDB 2.1.1 (714d615) port/fal/inc/fal.h includes this file. Values are
 * from the authenticated Apollo main 2.2.6.10 image:
 *   - one flash device "norflash", base 0x01FC0000, length 0x02000000,
 *     4 KiB blocks, write granularity 1; device table at ROM 0x78F0A4,
 *     count at 0x78F0A8 (g2/src/apollo-main/drivers/flash/fal/
 *     fal-product-config/product_tables.c);
 *   - two partition rows at ROM 0x6D5358 (64-byte rows, so the default
 *     FAL_DEV_NAME_MAX of 24 applies): "kvdb" (FlashDB "sysenv") at
 *     0x01FC0000 + 0x38000 and "NVdb" (FlashDB "factory") at
 *     0x01FF8000 + 0x8000.
 * FAL_DEBUG stays at its default 0.
 */

#ifndef OPENCFW_G2_FAL_CFG_H
#define OPENCFW_G2_FAL_CFG_H

#define NOR_FLASH_DEV_NAME "norflash"

extern const struct fal_flash_dev g2_fal_norflash;

#define FAL_FLASH_DEV_TABLE \
{                           \
    &g2_fal_norflash,       \
}

#define FAL_PART_HAS_TABLE_CFG
#define FAL_PART_TABLE                                                               \
{                                                                                    \
    {FAL_PART_MAGIC_WORD, "kvdb", NOR_FLASH_DEV_NAME, 0x01fc0000, 0x00038000, 0},     \
    {FAL_PART_MAGIC_WORD, "NVdb", NOR_FLASH_DEV_NAME, 0x01ff8000, 0x00008000, 0},     \
}

#endif /* OPENCFW_G2_FAL_CFG_H */
