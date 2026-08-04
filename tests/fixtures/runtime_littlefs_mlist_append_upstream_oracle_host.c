/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs.c as the independent
 * oracle for the isolated lfs_mlist_append candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

static lfs_t open_cfw_oracle_littlefs_mlist_append_lfs;
static struct lfs_mlist open_cfw_oracle_littlefs_mlist_append_nodes[3];

static uint32_t open_cfw_oracle_littlefs_mlist_append_node_id_(
    const struct lfs_mlist *node
)
{
    return node ? node->id : UINT32_MAX;
}

void open_cfw_oracle_littlefs_mlist_append_reset(uint32_t initial)
{
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_oracle_littlefs_mlist_append_lfs);
        ++index
    ) {
        ((uint8_t *)(void *)&open_cfw_oracle_littlefs_mlist_append_lfs)[
            index
        ] = 0xA5U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_oracle_littlefs_mlist_append_nodes[index].next = NULL;
        open_cfw_oracle_littlefs_mlist_append_nodes[index].id =
            (uint16_t)(0x110U + index);
        open_cfw_oracle_littlefs_mlist_append_nodes[index].type =
            (uint8_t)(0x20U + index);
    }

    open_cfw_oracle_littlefs_mlist_append_lfs.mlist =
        initial ? &open_cfw_oracle_littlefs_mlist_append_nodes[0] : NULL;
    open_cfw_oracle_littlefs_mlist_append_lfs.seed = 0x13579BDFU;
    open_cfw_oracle_littlefs_mlist_append_lfs.block_count = 3008U;
}

void open_cfw_oracle_littlefs_mlist_append_call(uint32_t index)
{
    lfs_mlist_append(
        &open_cfw_oracle_littlefs_mlist_append_lfs,
        &open_cfw_oracle_littlefs_mlist_append_nodes[index]
    );
}

uint32_t open_cfw_oracle_littlefs_mlist_append_head_id(void)
{
    return open_cfw_oracle_littlefs_mlist_append_node_id_(
        open_cfw_oracle_littlefs_mlist_append_lfs.mlist
    );
}

uint32_t open_cfw_oracle_littlefs_mlist_append_next_id(uint32_t index)
{
    return open_cfw_oracle_littlefs_mlist_append_node_id_(
        open_cfw_oracle_littlefs_mlist_append_nodes[index].next
    );
}

uint32_t open_cfw_oracle_littlefs_mlist_append_node_id(uint32_t index)
{
    return open_cfw_oracle_littlefs_mlist_append_nodes[index].id;
}

uint32_t open_cfw_oracle_littlefs_mlist_append_node_type(uint32_t index)
{
    return open_cfw_oracle_littlefs_mlist_append_nodes[index].type;
}

uint32_t open_cfw_oracle_littlefs_mlist_append_seed(void)
{
    return open_cfw_oracle_littlefs_mlist_append_lfs.seed;
}

uint32_t open_cfw_oracle_littlefs_mlist_append_block_count(void)
{
    return open_cfw_oracle_littlefs_mlist_append_lfs.block_count;
}

size_t open_cfw_oracle_littlefs_mlist_append_lfs_size(void)
{
    return sizeof(open_cfw_oracle_littlefs_mlist_append_lfs);
}

size_t open_cfw_oracle_littlefs_mlist_append_mlist_offset(void)
{
    return offsetof(lfs_t, mlist);
}

size_t open_cfw_oracle_littlefs_mlist_append_next_offset(void)
{
    return offsetof(struct lfs_mlist, next);
}

size_t open_cfw_oracle_littlefs_mlist_append_id_offset(void)
{
    return offsetof(struct lfs_mlist, id);
}

size_t open_cfw_oracle_littlefs_mlist_append_type_offset(void)
{
    return offsetof(struct lfs_mlist, type);
}
