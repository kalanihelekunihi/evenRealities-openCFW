/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_gstate_getorphans() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410C2A, 0x00410C36). It
 * calls the already admitted lfs_tag_size() leaf at its stock entry. This
 * leaf owns no provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_gstate_getorphans.h"
#include "runtime_littlefs_tag_size.h"

__attribute__((used, noinline))
uint8_t open_cfw_littlefs_gstate_getorphans(const uint32_t *gstate_tag)
{
    return (uint8_t)(open_cfw_littlefs_tag_size(
        (open_cfw_littlefs_size_tag_t)*gstate_tag
    ) & 0x1ffU);
}
