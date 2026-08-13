/*
 * lfs utility functions
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Isolated, non-production candidate for the source-closed lfs_util.h
 * scalar cluster and lfs_fs_disk_version_major/minor from littlefs v2.10.1
 * at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The selected expressions come from the authenticated pristine snapshot at
 * third_party/littlefs. Both official G2 images contain the same retained
 * utility cluster. The official IAR build selected the LFS_NO_INTRINSICS
 * fallback expressions for lfs_npw2, lfs_ctz, and lfs_popc, so this candidate
 * makes that source-build selection unconditional and reviewable.
 *
 * This file is deliberately not registered by either production overlay.
 * All exported names are project-prefixed to keep the experiment separate
 * from the pristine upstream snapshot and future production ownership.
 */

typedef unsigned char open_cfw_littlefs_util_u8;
typedef unsigned short open_cfw_littlefs_util_u16;
typedef unsigned int open_cfw_littlefs_util_u32;

_Static_assert(
    sizeof(open_cfw_littlefs_util_u8) == 1U,
    "littlefs uint8_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_util_u16) == 2U,
    "littlefs uint16_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_util_u32) == 4U,
    "littlefs uint32_t width changed"
);

/*
 * This marker is intentionally fixed inside the candidate. It documents that
 * the following bit helpers select the same basic-C branch as upstream
 * lfs_util.h under LFS_NO_INTRINSICS.
 */
#define OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS 1

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

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_npw2(
    open_cfw_littlefs_util_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    open_cfw_littlefs_util_u32 r = 0U;
    open_cfw_littlefs_util_u32 s;

    a -= 1U;
    s = (a > 0xffffU) << 4; a >>= s; r |= s;
    s = (a > 0xffU) << 3; a >>= s; r |= s;
    s = (a > 0xfU) << 2; a >>= s; r |= s;
    s = (a > 0x3U) << 1; a >>= s; r |= s;
    return (r | (a >> 1)) + 1U;
#else
#error "The G2 source candidate must retain the official fallback branch"
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_ctz(
    open_cfw_littlefs_util_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    return open_cfw_littlefs_util_npw2((a & -a) + 1U) - 1U;
#else
#error "The G2 source candidate must retain the official fallback branch"
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_popc(
    open_cfw_littlefs_util_u32 a
)
{
#if OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
    a = a - ((a >> 1) & 0x55555555U);
    a = (a & 0x33333333U) + ((a >> 2) & 0x33333333U);
    return (((a + (a >> 4)) & 0x0f0f0f0fU) * 0x01010101U) >> 24;
#else
#error "The G2 source candidate must retain the official fallback branch"
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_fromle32(
    open_cfw_littlefs_util_u32 a
)
{
    return a;
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_tole32(
    open_cfw_littlefs_util_u32 a
)
{
    return open_cfw_littlefs_util_fromle32(a);
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_frombe32(
    open_cfw_littlefs_util_u32 a
)
{
    return (((open_cfw_littlefs_util_u8 *)&a)[0] << 24) |
           (((open_cfw_littlefs_util_u8 *)&a)[1] << 16) |
           (((open_cfw_littlefs_util_u8 *)&a)[2] << 8) |
           (((open_cfw_littlefs_util_u8 *)&a)[3] << 0);
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u32 open_cfw_littlefs_util_tobe32(
    open_cfw_littlefs_util_u32 a
)
{
    return open_cfw_littlefs_util_frombe32(a);
}

struct open_cfw_littlefs_disk_version_lfs;

extern open_cfw_littlefs_util_u32 open_cfw_littlefs_disk_version(
    struct open_cfw_littlefs_disk_version_lfs *lfs
);

__attribute__((used, noinline))
open_cfw_littlefs_util_u16 open_cfw_littlefs_disk_version_major(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    return (open_cfw_littlefs_util_u16)(
        0xffffU & (open_cfw_littlefs_disk_version(lfs) >> 16)
    );
}

__attribute__((used, noinline))
open_cfw_littlefs_util_u16 open_cfw_littlefs_disk_version_minor(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    return (open_cfw_littlefs_util_u16)(
        0xffffU & (open_cfw_littlefs_disk_version(lfs) >> 0)
    );
}

#undef OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS
