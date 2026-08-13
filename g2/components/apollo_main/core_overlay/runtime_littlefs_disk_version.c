/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Integrated, freestanding source replacement for lfs_fs_disk_version() from
 * littlefs v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * LFS_MULTIVERSION is absent from the official G2 configuration ABI. Both
 * official images therefore retain the same constant-return leaf at
 * Apollo-main [0x004CB0C4, 0x004CB0CA) and bootloader
 * [0x00410DCC, 0x00410DD2). This source closes the stock out-of-line literal
 * dependency by emitting its own source-generated LFS_DISK_VERSION word.
 * It has no structure dereference, callback, allocator, flash, or MSPI
 * dependency.
 */

typedef unsigned int open_cfw_littlefs_disk_version_u32;
struct open_cfw_littlefs_disk_version_lfs;

#define OPEN_CFW_LFS_DISK_VERSION 0x00020001U

_Static_assert(
    sizeof(open_cfw_littlefs_disk_version_u32) == 4U,
    "littlefs uint32_t width changed"
);
_Static_assert(
    OPEN_CFW_LFS_DISK_VERSION == 0x00020001U,
    "littlefs v2.1 disk version changed"
);

__attribute__((used, noinline))
open_cfw_littlefs_disk_version_u32 open_cfw_littlefs_disk_version(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    (void)lfs;
    return OPEN_CFW_LFS_DISK_VERSION;
}

#undef OPEN_CFW_LFS_DISK_VERSION
