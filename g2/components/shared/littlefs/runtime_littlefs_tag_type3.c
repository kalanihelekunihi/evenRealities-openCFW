/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_type3() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bodies occupy [0x004CAE98, 0x004CAEA0) in Apollo main and
 * [0x00410BA0, 0x00410BA8) in the bootloader. This pure scalar leaf has no
 * provider, global state, allocation, or hardware path. Both official bodies
 * are redirected atomically to this shared source-owned leaf.
 */

#include "runtime_littlefs_tag_type3.h"

__attribute__((used, noinline))
uint16_t open_cfw_littlefs_tag_type3(open_cfw_littlefs_type3_tag_t tag)
{
    return (uint16_t)((tag & UINT32_C(0x7ff00000)) >> 20U);
}
