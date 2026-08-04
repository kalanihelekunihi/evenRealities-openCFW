/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs_util.h as the
 * independent oracle for the isolated fallback bit-operation trio.
 */

#include <stdint.h>

#define LFS_NO_MALLOC
#define LFS_NO_ASSERT
#define LFS_NO_DEBUG
#define LFS_NO_WARN
#define LFS_NO_ERROR
#define LFS_NO_INTRINSICS
#include "../../third_party/littlefs/lfs_util.h"

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
