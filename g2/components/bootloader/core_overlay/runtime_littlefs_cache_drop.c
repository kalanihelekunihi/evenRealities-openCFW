/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production adaptation of lfs_cache_drop() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410522, 0x0041052A). This
 * leaf owns no provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_cache_drop.h"

#define OPEN_CFW_BOOTLOADER_LITTLEFS_CACHE_DROP_BLOCK_NULL \
    ((open_cfw_bootloader_littlefs_cache_drop_u32)-1)

__attribute__((used, noinline))
void open_cfw_bootloader_littlefs_cache_drop(
    void *lfs,
    struct open_cfw_bootloader_littlefs_cache_drop_cache *rcache)
{
    (void)lfs;
    rcache->block = OPEN_CFW_BOOTLOADER_LITTLEFS_CACHE_DROP_BLOCK_NULL;
}
