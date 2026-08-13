/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Shared, bounded freestanding port of the LFS_NO_INTRINSICS branches of
 * lfs_npw2(), lfs_ctz(), and lfs_popc() from littlefs v2.10.1 lfs_util.h
 * at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318, tree
 * 06dd0162169d3cb550cd24a3e34d0e4d02983ad3.
 *
 * Both official G2 images retain the same complete private leaves at
 * Apollo-main [0x004CA720, 0x004CA7B2) and bootloader
 * [0x00410428, 0x004104BA). Their bodies select the upstream fallback
 * expressions rather than compiler intrinsics. Keeping that selection
 * explicit also preserves the fallback's deterministic zero-input results:
 * lfs_npw2(0) == 32, lfs_ctz(0) == 0, and lfs_popc(0) == 0.
 *
 * The trio is mini-linked as one bounded source cluster: lfs_ctz retains its
 * exact upstream call expression and therefore its single internal Thumb
 * relocation to the source-owned lfs_npw2 provider. There are no external or
 * undefined dependencies. These helpers own no filesystem state,
 * configuration, callbacks, data, literal pool, or hardware access.
 */

typedef unsigned int open_cfw_littlefs_util_bitops_u32;

_Static_assert(
    sizeof(open_cfw_littlefs_util_bitops_u32) == 4U,
    "littlefs uint32_t width changed"
);

#define OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS 1

__attribute__((used, noinline))
open_cfw_littlefs_util_bitops_u32 open_cfw_littlefs_util_npw2(
    open_cfw_littlefs_util_bitops_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    open_cfw_littlefs_util_bitops_u32 r = 0U;
    open_cfw_littlefs_util_bitops_u32 s;

    a -= 1U;
    s = (a > 0xffffU) << 4; a >>= s; r |= s;
    s = (a > 0xffU) << 3; a >>= s; r |= s;
    s = (a > 0xfU) << 2; a >>= s; r |= s;
    s = (a > 0x3U) << 1; a >>= s; r |= s;
    return (r | (a >> 1)) + 1U;
#else
#error "The G2 production source must retain the official fallback branch"
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_util_bitops_u32 open_cfw_littlefs_util_ctz(
    open_cfw_littlefs_util_bitops_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    return open_cfw_littlefs_util_npw2(
        (a & (0U - a)) + 1U
    ) - 1U;
#else
#error "The G2 production source must retain the official fallback branch"
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_util_bitops_u32 open_cfw_littlefs_util_popc(
    open_cfw_littlefs_util_bitops_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    a = a - ((a >> 1) & 0x55555555U);
    a = (a & 0x33333333U) + ((a >> 2) & 0x33333333U);
    return (((a + (a >> 4)) & 0x0f0f0f0fU) * 0x01010101U) >> 24;
#else
#error "The G2 production source must retain the official fallback branch"
#endif
}
