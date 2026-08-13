/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding port of lfs_scmp() from littlefs v2.10.1
 * lfs_util.h at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader contains this complete private leaf at
 * [0x004104BA, 0x004104BE). It performs one modulo-2^32 subtraction and
 * returns the signed interpretation of all 32 result bits. It owns no
 * pointers, configuration, callbacks, storage operations, or hardware state.
 */

typedef unsigned int open_cfw_littlefs_scmp_u32;

_Static_assert(
    sizeof(open_cfw_littlefs_scmp_u32) == 4U,
    "littlefs uint32_t width changed"
);
_Static_assert(sizeof(unsigned) == 4U, "littlefs unsigned width changed");
_Static_assert(sizeof(int) == 4U, "littlefs int width changed");

__attribute__((used, noinline))
int open_cfw_littlefs_scmp(
    open_cfw_littlefs_scmp_u32 a,
    open_cfw_littlefs_scmp_u32 b
)
{
    return (int)(unsigned)(a - b);
}
