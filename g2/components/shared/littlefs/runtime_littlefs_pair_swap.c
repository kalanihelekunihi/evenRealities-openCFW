/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_pair_swap() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410ACE, 0x00410AD8). This
 * pure scalar leaf has no provider, global state, allocation, or hardware
 * path.
 */

#include "runtime_littlefs_pair_swap.h"

__attribute__((used, noinline))
void open_cfw_littlefs_pair_swap(open_cfw_littlefs_pair_swap_block_t pair[2])
{
    open_cfw_littlefs_pair_swap_block_t t = pair[0];
    pair[0] = pair[1];
    pair[1] = t;
}
