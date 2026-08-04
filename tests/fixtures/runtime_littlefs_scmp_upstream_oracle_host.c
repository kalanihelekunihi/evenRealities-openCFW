/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs_util.h as the
 * independent oracle for the source-owned lfs_scmp boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs_util.h"

int32_t open_cfw_oracle_littlefs_scmp_call(uint32_t a, uint32_t b)
{
    return lfs_scmp(a, b);
}

size_t open_cfw_oracle_littlefs_scmp_uint32_size(void)
{
    return sizeof(uint32_t);
}

size_t open_cfw_oracle_littlefs_scmp_unsigned_size(void)
{
    return sizeof(unsigned);
}

size_t open_cfw_oracle_littlefs_scmp_int_size(void)
{
    return sizeof(int);
}
