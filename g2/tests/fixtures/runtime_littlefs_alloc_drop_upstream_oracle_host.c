/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs.c as the independent
 * oracle for the source-owned lfs_alloc_drop boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

static lfs_t open_cfw_oracle_littlefs_alloc_drop_lfs;

void open_cfw_oracle_littlefs_alloc_drop_reset(
    uint8_t pattern,
    uint32_t size,
    uint32_t next,
    uint32_t checkpoint,
    uint32_t block_count
)
{
    uint8_t *bytes = (uint8_t *)(void *)
        &open_cfw_oracle_littlefs_alloc_drop_lfs;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_alloc_drop_lfs);
        ++index
    ) {
        bytes[index] = pattern;
    }
    open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.size = size;
    open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.next = next;
    open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.ckpoint = checkpoint;
    open_cfw_oracle_littlefs_alloc_drop_lfs.block_count = block_count;
}

void open_cfw_oracle_littlefs_alloc_drop_call(void)
{
    lfs_alloc_drop(&open_cfw_oracle_littlefs_alloc_drop_lfs);
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_oracle_littlefs_alloc_drop_lfs;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_alloc_drop_lfs);
        ++index
    ) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_outside_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)
        &open_cfw_oracle_littlefs_alloc_drop_lfs;
    const size_t size_offset = offsetof(lfs_t, lookahead) +
        offsetof(struct lfs_lookahead, size);
    const size_t end_offset = offsetof(lfs_t, lookahead) +
        offsetof(struct lfs_lookahead, ckpoint) +
        sizeof(uint32_t);
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_alloc_drop_lfs);
        ++index
    ) {
        if (index < size_offset || index >= end_offset) {
            checksum ^= bytes[index];
            checksum *= 16777619U;
        }
    }
    return checksum;
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_size(void)
{
    return open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.size;
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_next(void)
{
    return open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.next;
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_checkpoint(void)
{
    return open_cfw_oracle_littlefs_alloc_drop_lfs.lookahead.ckpoint;
}

uint32_t open_cfw_oracle_littlefs_alloc_drop_block_count(void)
{
    return open_cfw_oracle_littlefs_alloc_drop_lfs.block_count;
}

size_t open_cfw_oracle_littlefs_alloc_drop_lfs_size(void)
{
    return sizeof(open_cfw_oracle_littlefs_alloc_drop_lfs);
}

size_t open_cfw_oracle_littlefs_alloc_drop_lookahead_offset(void)
{
    return offsetof(lfs_t, lookahead);
}

size_t open_cfw_oracle_littlefs_alloc_drop_size_offset(void)
{
    return offsetof(lfs_t, lookahead) +
        offsetof(struct lfs_lookahead, size);
}

size_t open_cfw_oracle_littlefs_alloc_drop_next_offset(void)
{
    return offsetof(lfs_t, lookahead) +
        offsetof(struct lfs_lookahead, next);
}

size_t open_cfw_oracle_littlefs_alloc_drop_checkpoint_offset(void)
{
    return offsetof(lfs_t, lookahead) +
        offsetof(struct lfs_lookahead, ckpoint);
}

size_t open_cfw_oracle_littlefs_alloc_drop_block_count_offset(void)
{
    return offsetof(lfs_t, block_count);
}
