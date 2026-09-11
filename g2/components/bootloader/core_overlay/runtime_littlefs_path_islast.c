/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production adaptation of lfs_path_islast() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410A88, 0x00410AB4),
 * including the embedded "/" separator literal it shares with the sibling
 * lfs_path_namelen() leaf immediately before it. It calls the sibling
 * open_cfw_bootloader_littlefs_path_namelen() and the already admitted
 * open_cfw_bootloader_strspn() at their stock entries. This leaf owns no
 * provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_path_islast.h"
#include "runtime_littlefs_path_namelen.h"
#include "runtime_string_spans.h"

__attribute__((used, noinline))
bool open_cfw_bootloader_littlefs_path_islast(const char *path)
{
    open_cfw_bootloader_littlefs_size_t namelen =
        open_cfw_bootloader_littlefs_path_namelen(path);
    return path[namelen + open_cfw_bootloader_strspn(path + namelen, "/")]
        == '\0';
}
