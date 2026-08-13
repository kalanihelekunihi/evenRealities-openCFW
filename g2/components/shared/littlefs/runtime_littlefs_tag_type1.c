/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_type1() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bodies occupy [0x004CAE88, 0x004CAE90) in Apollo main and
 * [0x00410B90, 0x00410B98) in the bootloader. This pure scalar leaf has no
 * provider, global state, allocation, or hardware path. Both official bodies
 * are redirected atomically to this shared source-owned leaf.
 */

#include "runtime_littlefs_tag_type1.h"

__attribute__((used, noinline))
uint16_t open_cfw_littlefs_tag_type1(open_cfw_littlefs_type1_tag_t tag)
{
    return (uint16_t)((tag & UINT32_C(0x70000000)) >> 20U);
}
