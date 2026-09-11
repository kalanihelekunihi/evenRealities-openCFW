/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_cache_drop().
 * The recovered lfs_cache_t ABI is {block, off, size, buffer}; this leaf
 * only writes the block field at offset 0 and ignores the unused lfs_t
 * parameter, exactly as the upstream body does.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_CACHE_DROP_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_CACHE_DROP_H

typedef unsigned int open_cfw_bootloader_littlefs_cache_drop_u32;

struct open_cfw_bootloader_littlefs_cache_drop_cache {
    open_cfw_bootloader_littlefs_cache_drop_u32 block;
    open_cfw_bootloader_littlefs_cache_drop_u32 off;
    open_cfw_bootloader_littlefs_cache_drop_u32 size;
    unsigned char *buffer;
};

_Static_assert(
    __builtin_offsetof(
        struct open_cfw_bootloader_littlefs_cache_drop_cache,
        block
    ) == 0U,
    "littlefs lfs_cache_t block offset changed"
);

/* lfs is unused, matching the upstream (void)lfs cast. */
void open_cfw_bootloader_littlefs_cache_drop(
    void *lfs,
    struct open_cfw_bootloader_littlefs_cache_drop_cache *rcache
);

#endif
