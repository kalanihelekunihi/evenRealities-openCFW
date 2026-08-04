/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Integrated, freestanding source replacements for
 * lfs_fs_disk_version_major() and lfs_fs_disk_version_minor() from littlefs
 * v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * Both helpers close over the already source-owned
 * open_cfw_littlefs_disk_version() implementation. LFS_MULTIVERSION is absent
 * from both authenticated G2 littlefs configuration objects, so neither
 * helper dereferences lfs_t or introduces a new target ABI dependency.
 */

typedef unsigned short open_cfw_littlefs_disk_version_u16;
typedef unsigned int open_cfw_littlefs_disk_version_u32;
struct open_cfw_littlefs_disk_version_lfs;

extern open_cfw_littlefs_disk_version_u32 open_cfw_littlefs_disk_version(
    struct open_cfw_littlefs_disk_version_lfs *lfs
);

_Static_assert(
    sizeof(open_cfw_littlefs_disk_version_u16) == 2U,
    "littlefs uint16_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_disk_version_u32) == 4U,
    "littlefs uint32_t width changed"
);

__attribute__((used, noinline))
open_cfw_littlefs_disk_version_u16 open_cfw_littlefs_disk_version_major(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    return (open_cfw_littlefs_disk_version_u16)(
        0xffffU & (open_cfw_littlefs_disk_version(lfs) >> 16)
    );
}

__attribute__((used, noinline))
open_cfw_littlefs_disk_version_u16 open_cfw_littlefs_disk_version_minor(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    return (open_cfw_littlefs_disk_version_u16)(
        0xffffU & (open_cfw_littlefs_disk_version(lfs) >> 0)
    );
}
