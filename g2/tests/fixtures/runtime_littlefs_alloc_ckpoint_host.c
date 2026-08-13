/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the source-owned littlefs lfs_alloc_ckpoint boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_alloc_ckpoint.c"

static struct open_cfw_littlefs_alloc_ckpoint_lfs
open_cfw_test_littlefs_alloc_ckpoint_lfs;

static size_t open_cfw_test_littlefs_alloc_ckpoint_checkpoint_offset_(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        lookahead
    ) + offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lookahead,
        checkpoint
    );
}

void open_cfw_test_littlefs_alloc_ckpoint_reset(
    uint8_t pattern,
    uint32_t block_count
)
{
    uint8_t *bytes = (uint8_t *)(void *)
        &open_cfw_test_littlefs_alloc_ckpoint_lfs;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_ckpoint_lfs);
        ++index
    ) {
        bytes[index] = pattern;
    }
    open_cfw_test_littlefs_alloc_ckpoint_lfs.block_count = block_count;
}

void open_cfw_test_littlefs_alloc_ckpoint_call(void)
{
    open_cfw_littlefs_alloc_ckpoint(
        &open_cfw_test_littlefs_alloc_ckpoint_lfs
    );
}

uint32_t open_cfw_test_littlefs_alloc_ckpoint_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_test_littlefs_alloc_ckpoint_lfs;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_ckpoint_lfs);
        ++index
    ) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_alloc_ckpoint_outside_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_test_littlefs_alloc_ckpoint_lfs;
    const size_t checkpoint =
        open_cfw_test_littlefs_alloc_ckpoint_checkpoint_offset_();
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_ckpoint_lfs);
        ++index
    ) {
        if (index < checkpoint || index >= checkpoint + sizeof(uint32_t)) {
            checksum ^= bytes[index];
            checksum *= 16777619U;
        }
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_alloc_ckpoint_checkpoint(void)
{
    return open_cfw_test_littlefs_alloc_ckpoint_lfs.lookahead.checkpoint;
}

uint32_t open_cfw_test_littlefs_alloc_ckpoint_block_count(void)
{
    return open_cfw_test_littlefs_alloc_ckpoint_lfs.block_count;
}

size_t open_cfw_test_littlefs_alloc_ckpoint_lfs_size(void)
{
    return sizeof(open_cfw_test_littlefs_alloc_ckpoint_lfs);
}

size_t open_cfw_test_littlefs_alloc_ckpoint_lookahead_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        lookahead
    );
}

size_t open_cfw_test_littlefs_alloc_ckpoint_checkpoint_offset(void)
{
    return open_cfw_test_littlefs_alloc_ckpoint_checkpoint_offset_();
}

size_t open_cfw_test_littlefs_alloc_ckpoint_block_count_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        block_count
    );
}
