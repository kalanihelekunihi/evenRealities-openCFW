/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs.c as the independent
 * oracle for the isolated lfs_fs_disk_version candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

uint32_t open_cfw_oracle_littlefs_disk_version_call(void)
{
    return lfs_fs_disk_version(NULL);
}

size_t open_cfw_oracle_littlefs_disk_version_u32_size(void)
{
    return sizeof(uint32_t);
}
