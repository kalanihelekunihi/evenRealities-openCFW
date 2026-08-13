/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the source-owned littlefs lfs_alloc_drop boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_alloc_drop.c"

static struct open_cfw_littlefs_alloc_drop_lfs
open_cfw_test_littlefs_alloc_drop_lfs;

void open_cfw_test_littlefs_alloc_drop_reset(
    uint8_t pattern,
    uint32_t size,
    uint32_t next,
    uint32_t checkpoint,
    uint32_t block_count
)
{
    uint8_t *bytes = (uint8_t *)(void *)
        &open_cfw_test_littlefs_alloc_drop_lfs;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_drop_lfs);
        ++index
    ) {
        bytes[index] = pattern;
    }
    open_cfw_test_littlefs_alloc_drop_lfs.lookahead.size = size;
    open_cfw_test_littlefs_alloc_drop_lfs.lookahead.next = next;
    open_cfw_test_littlefs_alloc_drop_lfs.lookahead.checkpoint = checkpoint;
    open_cfw_test_littlefs_alloc_drop_lfs.block_count = block_count;
}

void open_cfw_test_littlefs_alloc_drop_call(void)
{
    open_cfw_littlefs_alloc_drop(&open_cfw_test_littlefs_alloc_drop_lfs);
}

uint32_t open_cfw_test_littlefs_alloc_drop_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_test_littlefs_alloc_drop_lfs;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_drop_lfs);
        ++index
    ) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_alloc_drop_outside_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_test_littlefs_alloc_drop_lfs;
    const size_t size_offset =
        offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead) +
        offsetof(struct open_cfw_littlefs_alloc_drop_lookahead, size);
    const size_t end_offset =
        offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead) +
        offsetof(struct open_cfw_littlefs_alloc_drop_lookahead, checkpoint) +
        sizeof(uint32_t);
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_drop_lfs);
        ++index
    ) {
        if (index < size_offset || index >= end_offset) {
            checksum ^= bytes[index];
            checksum *= 16777619U;
        }
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_alloc_drop_size(void)
{
    return open_cfw_test_littlefs_alloc_drop_lfs.lookahead.size;
}

uint32_t open_cfw_test_littlefs_alloc_drop_next(void)
{
    return open_cfw_test_littlefs_alloc_drop_lfs.lookahead.next;
}

uint32_t open_cfw_test_littlefs_alloc_drop_checkpoint(void)
{
    return open_cfw_test_littlefs_alloc_drop_lfs.lookahead.checkpoint;
}

uint32_t open_cfw_test_littlefs_alloc_drop_block_count(void)
{
    return open_cfw_test_littlefs_alloc_drop_lfs.block_count;
}

size_t open_cfw_test_littlefs_alloc_drop_lfs_size(void)
{
    return sizeof(open_cfw_test_littlefs_alloc_drop_lfs);
}

size_t open_cfw_test_littlefs_alloc_drop_lookahead_offset(void)
{
    return offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead);
}

size_t open_cfw_test_littlefs_alloc_drop_size_offset(void)
{
    return offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead) +
        offsetof(struct open_cfw_littlefs_alloc_drop_lookahead, size);
}

size_t open_cfw_test_littlefs_alloc_drop_next_offset(void)
{
    return offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead) +
        offsetof(struct open_cfw_littlefs_alloc_drop_lookahead, next);
}

size_t open_cfw_test_littlefs_alloc_drop_checkpoint_offset(void)
{
    return offsetof(struct open_cfw_littlefs_alloc_drop_lfs, lookahead) +
        offsetof(struct open_cfw_littlefs_alloc_drop_lookahead, checkpoint);
}

size_t open_cfw_test_littlefs_alloc_drop_block_count_offset(void)
{
    return offsetof(struct open_cfw_littlefs_alloc_drop_lfs, block_count);
}
