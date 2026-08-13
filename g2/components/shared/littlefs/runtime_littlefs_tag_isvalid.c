/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_isvalid() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bodies occupy [0x004CAE6A, 0x004CAE74) in Apollo main and
 * [0x00410B72, 0x00410B7C) in the bootloader. This pure scalar leaf has no
 * provider, global state, allocation, or hardware path. Both official bodies
 * are redirected atomically to this shared source-owned leaf.
 */

#include "runtime_littlefs_tag_isvalid.h"

__attribute__((used, noinline))
bool open_cfw_littlefs_tag_isvalid(open_cfw_littlefs_isvalid_tag_t tag)
{
    return (tag & UINT32_C(0x80000000)) == 0U;
}
