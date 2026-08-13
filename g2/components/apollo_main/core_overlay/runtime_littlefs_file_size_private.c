/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding adaptation of lfs_file_size_() from littlefs v2.10.1
 * lfs.c at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 Apollo-main image places this complete private function at
 * [0x004CE472, 0x004CE48A). Its 24-byte body confirms that LFS_READONLY is
 * unset: LFS_F_WRITING selects lfs_max(file->pos, file->ctz.size), while the
 * non-writing path returns file->ctz.size. The only call is to the complete,
 * already source-owned lfs_max leaf whose stock entry is 0x004CA6F8.
 */

#include "runtime_littlefs_file_size_private.h"

__attribute__((used, noinline))
open_cfw_littlefs_file_size_private_s32
open_cfw_littlefs_file_size_private(
    struct open_cfw_littlefs_file_size_private_lfs *lfs,
    struct open_cfw_littlefs_file_size_private_file *file
)
{
    (void)lfs;

    if (
        (file->flags & OPEN_CFW_LITTLEFS_FILE_SIZE_PRIVATE_WRITING) != 0U
    ) {
        return open_cfw_littlefs_util_max(
            file->position,
            file->ctz.size
        );
    }

    return file->ctz.size;
}
