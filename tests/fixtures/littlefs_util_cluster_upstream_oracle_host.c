/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 as the independent oracle
 * for the isolated utility-cluster candidate. LFS_NO_INTRINSICS deliberately
 * selects the same fallback branch retained by both official G2 images.
 */

#include <stddef.h>
#include <stdint.h>

#define LFS_NO_INTRINSICS
#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

uint32_t open_cfw_oracle_littlefs_util_max(uint32_t a, uint32_t b)
{
    return lfs_max(a, b);
}

uint32_t open_cfw_oracle_littlefs_util_min(uint32_t a, uint32_t b)
{
    return lfs_min(a, b);
}

uint32_t open_cfw_oracle_littlefs_util_aligndown(
    uint32_t a,
    uint32_t alignment
)
{
    return lfs_aligndown(a, alignment);
}

uint32_t open_cfw_oracle_littlefs_util_alignup(
    uint32_t a,
    uint32_t alignment
)
{
    return lfs_alignup(a, alignment);
}

uint32_t open_cfw_oracle_littlefs_util_npw2(uint32_t a)
{
    return lfs_npw2(a);
}

uint32_t open_cfw_oracle_littlefs_util_ctz(uint32_t a)
{
    return lfs_ctz(a);
}

uint32_t open_cfw_oracle_littlefs_util_popc(uint32_t a)
{
    return lfs_popc(a);
}

uint32_t open_cfw_oracle_littlefs_util_fromle32(uint32_t a)
{
    return lfs_fromle32(a);
}

uint32_t open_cfw_oracle_littlefs_util_tole32(uint32_t a)
{
    return lfs_tole32(a);
}

uint32_t open_cfw_oracle_littlefs_util_frombe32(uint32_t a)
{
    return lfs_frombe32(a);
}

uint32_t open_cfw_oracle_littlefs_util_tobe32(uint32_t a)
{
    return lfs_tobe32(a);
}

uint16_t open_cfw_oracle_littlefs_util_disk_version_major(void)
{
    return lfs_fs_disk_version_major((lfs_t *)0);
}

uint16_t open_cfw_oracle_littlefs_util_disk_version_minor(void)
{
    return lfs_fs_disk_version_minor((lfs_t *)0);
}

size_t open_cfw_oracle_littlefs_util_uint8_size(void)
{
    return sizeof(uint8_t);
}

size_t open_cfw_oracle_littlefs_util_uint16_size(void)
{
    return sizeof(uint16_t);
}

size_t open_cfw_oracle_littlefs_util_uint32_size(void)
{
    return sizeof(uint32_t);
}
