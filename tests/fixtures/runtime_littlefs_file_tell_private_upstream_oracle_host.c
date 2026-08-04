/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs.c as the independent
 * oracle for the source-owned lfs_file_tell_ boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

static lfs_file_t open_cfw_oracle_littlefs_file_tell_private_file;

void open_cfw_oracle_littlefs_file_tell_private_reset(
    uint8_t pattern,
    uint32_t position
)
{
    uint8_t *bytes = (uint8_t *)(void *)
        &open_cfw_oracle_littlefs_file_tell_private_file;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_file_tell_private_file);
        ++index
    ) {
        bytes[index] = pattern;
    }
    open_cfw_oracle_littlefs_file_tell_private_file.pos = position;
}

int32_t open_cfw_oracle_littlefs_file_tell_private_call(
    uintptr_t lfs_address
)
{
    return lfs_file_tell_(
        (lfs_t *)lfs_address,
        &open_cfw_oracle_littlefs_file_tell_private_file
    );
}

uint32_t open_cfw_oracle_littlefs_file_tell_private_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_oracle_littlefs_file_tell_private_file;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_file_tell_private_file);
        ++index
    ) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_oracle_littlefs_file_tell_private_position(void)
{
    return open_cfw_oracle_littlefs_file_tell_private_file.pos;
}

size_t open_cfw_oracle_littlefs_file_tell_private_file_size(void)
{
    return sizeof(open_cfw_oracle_littlefs_file_tell_private_file);
}

size_t open_cfw_oracle_littlefs_file_tell_private_position_offset(void)
{
    return offsetof(lfs_file_t, pos);
}
