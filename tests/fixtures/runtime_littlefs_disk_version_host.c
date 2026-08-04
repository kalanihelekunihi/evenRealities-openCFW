/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the isolated littlefs lfs_fs_disk_version candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_disk_version.c"

uint32_t open_cfw_test_littlefs_disk_version_call(void)
{
    return open_cfw_littlefs_disk_version(NULL);
}

size_t open_cfw_test_littlefs_disk_version_u32_size(void)
{
    return sizeof(open_cfw_littlefs_disk_version_u32);
}
