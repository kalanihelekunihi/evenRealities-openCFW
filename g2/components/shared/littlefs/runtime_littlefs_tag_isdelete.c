/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_isdelete() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410B7C, 0x00410B90). This
 * pure scalar leaf has no provider, global state, allocation, or hardware
 * path.
 */

#include "runtime_littlefs_tag_isdelete.h"

__attribute__((used, noinline))
bool open_cfw_littlefs_tag_isdelete(open_cfw_littlefs_isdelete_tag_t tag)
{
    return ((int32_t)(tag << 22) >> 22) == -1;
}
