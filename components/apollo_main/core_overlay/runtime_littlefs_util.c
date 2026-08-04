/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Shared, bounded freestanding port of lfs_max(), lfs_min(),
 * lfs_aligndown(), and lfs_alignup() from littlefs v2.10.1 lfs_util.h at
 * commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 images contain the same complete utility leaves at
 * Apollo-main [0x004CA6F8, 0x004CA720) and bootloader
 * [0x00410400, 0x00410428). These functions operate only on 32-bit unsigned
 * scalar arguments. The alignup leaf is source-closed over aligndown; neither
 * function owns filesystem state, configuration, callbacks, data, or
 * hardware access.
 */

typedef unsigned int open_cfw_littlefs_util_u32;

_Static_assert(
    sizeof(open_cfw_littlefs_util_u32) == 4U,
    "littlefs uint32_t width changed"
);

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_max(
    open_cfw_littlefs_util_u32 a,
    open_cfw_littlefs_util_u32 b
)
{
    return (a > b) ? a : b;
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_min(
    open_cfw_littlefs_util_u32 a,
    open_cfw_littlefs_util_u32 b
)
{
    return (a < b) ? a : b;
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_aligndown(
    open_cfw_littlefs_util_u32 a,
    open_cfw_littlefs_util_u32 alignment
)
{
    return a - (a % alignment);
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_alignup(
    open_cfw_littlefs_util_u32 a,
    open_cfw_littlefs_util_u32 alignment
)
{
    return open_cfw_littlefs_util_aligndown(
        a + alignment - 1U,
        alignment
    );
}
