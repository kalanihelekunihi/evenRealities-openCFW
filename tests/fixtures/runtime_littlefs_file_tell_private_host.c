/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the source-owned littlefs lfs_file_tell_ boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_file_tell_private.c"

static struct open_cfw_littlefs_file_tell_private_file
open_cfw_test_littlefs_file_tell_private_file;

void open_cfw_test_littlefs_file_tell_private_reset(
    uint8_t pattern,
    uint32_t position
)
{
    uint8_t *bytes = (uint8_t *)(void *)
        &open_cfw_test_littlefs_file_tell_private_file;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_file_tell_private_file);
        ++index
    ) {
        bytes[index] = pattern;
    }
    open_cfw_test_littlefs_file_tell_private_file.position = position;
}

int32_t open_cfw_test_littlefs_file_tell_private_call(
    uintptr_t lfs_address
)
{
    return open_cfw_littlefs_file_tell_private(
        (struct open_cfw_littlefs_file_tell_private_lfs *)
            lfs_address,
        &open_cfw_test_littlefs_file_tell_private_file
    );
}

uint32_t open_cfw_test_littlefs_file_tell_private_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_test_littlefs_file_tell_private_file;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_file_tell_private_file);
        ++index
    ) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_file_tell_private_position(void)
{
    return open_cfw_test_littlefs_file_tell_private_file.position;
}

size_t open_cfw_test_littlefs_file_tell_private_file_size(void)
{
    return sizeof(open_cfw_test_littlefs_file_tell_private_file);
}

size_t open_cfw_test_littlefs_file_tell_private_position_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_file_tell_private_file,
        position
    );
}
