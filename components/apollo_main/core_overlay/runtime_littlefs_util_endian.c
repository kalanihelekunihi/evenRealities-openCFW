/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Shared, bounded freestanding port of lfs_fromle32(), lfs_tole32(),
 * lfs_frombe32(), and lfs_tobe32() from littlefs v2.10.1 lfs_util.h at
 * commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318, tree
 * 06dd0162169d3cb550cd24a3e34d0e4d02983ad3.
 *
 * Both official G2 images retain the same complete private leaves at
 * Apollo-main [0x004CA7B6, 0x004CA80A) and bootloader
 * [0x004104BE, 0x00410512). Apollo510 and both reviewed target profiles are
 * little-endian, selecting identity for little-endian conversion and a
 * 32-bit byte swap for big-endian conversion. The quartet owns no
 * filesystem state, configuration, callbacks, data, or hardware access.
 */

typedef unsigned int open_cfw_littlefs_util_endian_u32;

_Static_assert(
    sizeof(open_cfw_littlefs_util_endian_u32) == 4U,
    "littlefs uint32_t width changed"
);

#if !defined(__BYTE_ORDER__) || !defined(__ORDER_LITTLE_ENDIAN__)
#error "reviewed littlefs endian selection requires compiler byte-order macros"
#endif

_Static_assert(
    __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__,
    "Apollo510 littlefs target must remain little-endian"
);

__attribute__((used, noinline))
open_cfw_littlefs_util_endian_u32 open_cfw_littlefs_util_fromle32(
    open_cfw_littlefs_util_endian_u32 a
)
{
    return a;
}

__attribute__((used, noinline))
open_cfw_littlefs_util_endian_u32 open_cfw_littlefs_util_tole32(
    open_cfw_littlefs_util_endian_u32 a
)
{
    return open_cfw_littlefs_util_fromle32(a);
}

__attribute__((used, noinline))
open_cfw_littlefs_util_endian_u32 open_cfw_littlefs_util_frombe32(
    open_cfw_littlefs_util_endian_u32 a
)
{
    return __builtin_bswap32(a);
}

__attribute__((used, noinline))
open_cfw_littlefs_util_endian_u32 open_cfw_littlefs_util_tobe32(
    open_cfw_littlefs_util_endian_u32 a
)
{
    /*
     * Preserve upstream's inlined lfs_tobe32 -> lfs_frombe32 selection.
     * Calling the exported noinline provider would create a dependency that
     * does not exist after the upstream inline is selected.
     */
    return __builtin_bswap32(a);
}
