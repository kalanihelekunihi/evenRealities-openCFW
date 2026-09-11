/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_pair_isnull() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410AD8, 0x00410AF2). This
 * pure scalar leaf has no provider, global state, allocation, or hardware
 * path.
 */

#include "runtime_littlefs_pair_isnull.h"

#define OPEN_CFW_LITTLEFS_PAIR_ISNULL_BLOCK_NULL \
    ((open_cfw_littlefs_pair_isnull_block_t)-1)

__attribute__((used, noinline))
bool open_cfw_littlefs_pair_isnull(
    const open_cfw_littlefs_pair_isnull_block_t pair[2])
{
    return pair[0] == OPEN_CFW_LITTLEFS_PAIR_ISNULL_BLOCK_NULL
        || pair[1] == OPEN_CFW_LITTLEFS_PAIR_ISNULL_BLOCK_NULL;
}
