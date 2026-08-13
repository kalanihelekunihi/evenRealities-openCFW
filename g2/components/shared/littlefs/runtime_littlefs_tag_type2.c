/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Altered production adaptation of lfs_tag_type2() from the
 * authenticated littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 Apollo-main body occupies [0x004CAE90, 0x004CAE98).
 * This pure leaf has no provider, global state, allocation, or hardware path.
 * Its two authenticated stock callers are redirected at the stock entry.
 */

#include "runtime_littlefs_tag_type2.h"

__attribute__((used, noinline))
uint16_t open_cfw_littlefs_tag_type2(open_cfw_littlefs_tag_t tag)
{
    return (uint16_t)((tag & UINT32_C(0x78000000)) >> 20U);
}
