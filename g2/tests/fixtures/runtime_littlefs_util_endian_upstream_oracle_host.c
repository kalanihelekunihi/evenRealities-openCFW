/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs_util.h as the
 * independent oracle for the isolated endian-conversion quartet.
 */

#include <stdint.h>

#define LFS_NO_MALLOC
#define LFS_NO_ASSERT
#define LFS_NO_DEBUG
#define LFS_NO_WARN
#define LFS_NO_ERROR
#include "../../third_party/littlefs/lfs_util.h"

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
