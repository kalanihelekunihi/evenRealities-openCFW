/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production adaptation of lfs_path_namelen() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410A7E, 0x00410A88), and
 * shares the embedded "/" separator literal with the sibling
 * lfs_path_islast() leaf immediately after it. It calls the already
 * admitted open_cfw_bootloader_strcspn() at its stock entry. This leaf owns
 * no provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_path_namelen.h"
#include "runtime_string_spans.h"

__attribute__((used, noinline))
open_cfw_bootloader_littlefs_size_t open_cfw_bootloader_littlefs_path_namelen(
    const char *path)
{
    return (open_cfw_bootloader_littlefs_size_t)
        open_cfw_bootloader_strcspn(path, "/");
}
