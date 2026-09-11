/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_pair_issync() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410B1C, 0x00410B46). This
 * pure scalar leaf has no provider, global state, allocation, or hardware
 * path.
 */

#include "runtime_littlefs_pair_issync.h"

__attribute__((used, noinline))
bool open_cfw_littlefs_pair_issync(
    const open_cfw_littlefs_pair_issync_block_t paira[2],
    const open_cfw_littlefs_pair_issync_block_t pairb[2])
{
    return (paira[0] == pairb[0] && paira[1] == pairb[1]) ||
           (paira[0] == pairb[1] && paira[1] == pairb[0]);
}
