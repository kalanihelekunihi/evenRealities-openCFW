/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_splice() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410BAE, 0x00410BB8) and
 * calls the already admitted lfs_tag_chunk() leaf at its stock entry. This
 * leaf owns no provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_tag_splice.h"
#include "runtime_littlefs_tag_chunk.h"

__attribute__((used, noinline))
int8_t open_cfw_littlefs_tag_splice(open_cfw_littlefs_splice_tag_t tag)
{
    return (int8_t)open_cfw_littlefs_tag_chunk((open_cfw_littlefs_tag_t)tag);
}
