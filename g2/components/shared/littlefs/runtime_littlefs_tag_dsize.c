/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_tag_dsize() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410BC6, 0x00410BDC). It
 * calls the sibling lfs_tag_isdelete() leaf and the already admitted
 * lfs_tag_size() leaf at its stock entry. This leaf owns no provider,
 * global state, allocation, or hardware path.
 */

#include "runtime_littlefs_tag_dsize.h"
#include "runtime_littlefs_tag_isdelete.h"
#include "runtime_littlefs_tag_size.h"

__attribute__((used, noinline))
open_cfw_littlefs_dsize_t open_cfw_littlefs_tag_dsize(
    open_cfw_littlefs_dsize_tag_t tag)
{
    return (open_cfw_littlefs_dsize_t)sizeof(tag) +
        open_cfw_littlefs_tag_size(
            (open_cfw_littlefs_size_tag_t)(
                tag + open_cfw_littlefs_tag_isdelete(
                    (open_cfw_littlefs_isdelete_tag_t)tag
                )
            )
        );
}
