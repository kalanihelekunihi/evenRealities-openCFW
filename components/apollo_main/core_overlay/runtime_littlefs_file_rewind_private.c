/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Altered, freestanding adaptation of lfs_file_rewind_() from the
 * authenticated littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 Apollo-main image places the complete private function at
 * [0x004CE460, 0x004CE472). Its sole dependency is the retained private
 * lfs_file_seek_ at 0x004CE3BC. Negative seek results are preserved exactly;
 * every nonnegative seek result is normalized to zero.
 */

#include "runtime_littlefs_file_rewind_private.h"

__attribute__((used, noinline))
int open_cfw_littlefs_file_rewind_private(
    struct open_cfw_littlefs_file_rewind_private_lfs *lfs,
    struct open_cfw_littlefs_file_rewind_private_file *file
)
{
    open_cfw_littlefs_file_rewind_private_soff result =
        open_cfw_littlefs_file_seek_private(
            lfs,
            file,
            (open_cfw_littlefs_file_rewind_private_soff)0,
            OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_SET
        );
    if (result < 0) {
        return (int)result;
    }

    return 0;
}
