/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production adaptation of lfs_path_isdir() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410AB4, 0x00410ACE). It
 * calls the sibling open_cfw_bootloader_littlefs_path_namelen() at its
 * stock entry. This leaf owns no provider, global state, allocation, or
 * hardware path.
 */

#include "runtime_littlefs_path_isdir.h"
#include "runtime_littlefs_path_namelen.h"

__attribute__((used, noinline))
bool open_cfw_bootloader_littlefs_path_isdir(const char *path)
{
    return path[open_cfw_bootloader_littlefs_path_namelen(path)] != '\0';
}
