/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production adaptation of lfs_cache_zero() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x0041052A, 0x00410544). It
 * calls the already admitted open_cfw_bootloader_aeabi_memset() at its
 * stock entry. This leaf owns no provider, global state, allocation, or
 * hardware path.
 */

#include "runtime_littlefs_cache_zero.h"
#include "runtime_aeabi_memset.h"

#define OPEN_CFW_BOOTLOADER_LITTLEFS_CACHE_ZERO_BLOCK_NULL \
    ((open_cfw_bootloader_littlefs_cache_zero_u32)-1)

__attribute__((used, noinline))
void open_cfw_bootloader_littlefs_cache_zero(
    const struct open_cfw_bootloader_littlefs_cache_zero_lfs *lfs,
    struct open_cfw_bootloader_littlefs_cache_zero_cache *pcache)
{
    open_cfw_bootloader_aeabi_memset(
        pcache->buffer,
        (open_cfw_bootloader_memset_size)lfs->cfg->cache_size,
        0xff
    );
    pcache->block = OPEN_CFW_BOOTLOADER_LITTLEFS_CACHE_ZERO_BLOCK_NULL;
}
