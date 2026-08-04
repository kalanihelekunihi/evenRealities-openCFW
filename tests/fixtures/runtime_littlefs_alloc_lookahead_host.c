/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the source-owned littlefs lfs_alloc_lookahead callback.
 */

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c"

#define OPEN_CFW_TEST_LOOKAHEAD_BUFFER_BYTES 512U

static struct open_cfw_littlefs_alloc_lookahead_lfs
open_cfw_test_littlefs_alloc_lookahead_lfs;
static uint8_t open_cfw_test_littlefs_alloc_lookahead_buffer[
    OPEN_CFW_TEST_LOOKAHEAD_BUFFER_BYTES
];

void open_cfw_test_littlefs_alloc_lookahead_reset(
    uint8_t pattern,
    uint32_t start,
    uint32_t size,
    uint32_t block_count
)
{
    memset(
        &open_cfw_test_littlefs_alloc_lookahead_lfs,
        pattern,
        sizeof(open_cfw_test_littlefs_alloc_lookahead_lfs)
    );
    memset(
        open_cfw_test_littlefs_alloc_lookahead_buffer,
        pattern,
        sizeof(open_cfw_test_littlefs_alloc_lookahead_buffer)
    );
    open_cfw_test_littlefs_alloc_lookahead_lfs.lookahead.start = start;
    open_cfw_test_littlefs_alloc_lookahead_lfs.lookahead.size = size;
    open_cfw_test_littlefs_alloc_lookahead_lfs.lookahead.buffer =
        open_cfw_test_littlefs_alloc_lookahead_buffer;
    open_cfw_test_littlefs_alloc_lookahead_lfs.block_count = block_count;
}

int open_cfw_test_littlefs_alloc_lookahead_call(uint32_t block)
{
    return open_cfw_littlefs_alloc_lookahead(
        &open_cfw_test_littlefs_alloc_lookahead_lfs,
        block
    );
}

uint8_t open_cfw_test_littlefs_alloc_lookahead_buffer_get(size_t index)
{
    if (index >= OPEN_CFW_TEST_LOOKAHEAD_BUFFER_BYTES) {
        return 0U;
    }
    return open_cfw_test_littlefs_alloc_lookahead_buffer[index];
}

uint32_t open_cfw_test_littlefs_alloc_lookahead_buffer_checksum(void)
{
    uint32_t checksum = 2166136261U;
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_alloc_lookahead_buffer);
        ++index
    ) {
        checksum ^= open_cfw_test_littlefs_alloc_lookahead_buffer[index];
        checksum *= 16777619U;
    }
    return checksum;
}

uint32_t open_cfw_test_littlefs_alloc_lookahead_start(void)
{
    return open_cfw_test_littlefs_alloc_lookahead_lfs.lookahead.start;
}

uint32_t open_cfw_test_littlefs_alloc_lookahead_size(void)
{
    return open_cfw_test_littlefs_alloc_lookahead_lfs.lookahead.size;
}

uint32_t open_cfw_test_littlefs_alloc_lookahead_block_count(void)
{
    return open_cfw_test_littlefs_alloc_lookahead_lfs.block_count;
}

size_t open_cfw_test_littlefs_alloc_lookahead_lfs_size(void)
{
    return sizeof(open_cfw_test_littlefs_alloc_lookahead_lfs);
}

size_t open_cfw_test_littlefs_alloc_lookahead_start_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) + offsetof(
        struct open_cfw_littlefs_alloc_lookahead_state,
        start
    );
}

size_t open_cfw_test_littlefs_alloc_lookahead_size_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) + offsetof(
        struct open_cfw_littlefs_alloc_lookahead_state,
        size
    );
}

size_t open_cfw_test_littlefs_alloc_lookahead_buffer_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) + offsetof(
        struct open_cfw_littlefs_alloc_lookahead_state,
        buffer
    );
}

size_t open_cfw_test_littlefs_alloc_lookahead_block_count_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        block_count
    );
}
