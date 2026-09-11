/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_gstate_hasmovehere() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410C64, 0x00410C8A). It
 * calls the already admitted lfs_tag_type1() leaf and the sibling
 * lfs_pair_cmp() leaf at their stock entries. This leaf owns no provider,
 * global state, allocation, or hardware path.
 */

#include "runtime_littlefs_gstate_hasmovehere.h"
#include "runtime_littlefs_tag_type1.h"
#include "runtime_littlefs_pair_cmp.h"

__attribute__((used, noinline))
bool open_cfw_littlefs_gstate_hasmovehere(
    const uint32_t gstate[3],
    const uint32_t pair[2])
{
    return open_cfw_littlefs_tag_type1(
               (open_cfw_littlefs_type1_tag_t)gstate[0]
           ) != 0U
        && open_cfw_littlefs_pair_cmp(
               (const open_cfw_littlefs_pair_cmp_block_t *)&gstate[1],
               (const open_cfw_littlefs_pair_cmp_block_t *)pair
           ) == 0;
}
