/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the isolated littlefs lfs_mlist_remove candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_mlist_remove.c"

static struct open_cfw_littlefs_mlist_remove_lfs
open_cfw_test_littlefs_mlist_remove_lfs;
static struct open_cfw_littlefs_mlist_remove_node
open_cfw_test_littlefs_mlist_remove_nodes[4];

static uint32_t open_cfw_test_littlefs_mlist_remove_node_id_(
    const struct open_cfw_littlefs_mlist_remove_node *node
)
{
    return node ? node->id : UINT32_MAX;
}

void open_cfw_test_littlefs_mlist_remove_reset(uint32_t length)
{
    size_t index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_littlefs_mlist_remove_lfs);
        ++index
    ) {
        ((uint8_t *)(void *)&open_cfw_test_littlefs_mlist_remove_lfs)[
            index
        ] = 0x5AU;
    }
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_littlefs_mlist_remove_nodes[index].next =
            index + 1U < length
                ? &open_cfw_test_littlefs_mlist_remove_nodes[index + 1U]
                : NULL;
        open_cfw_test_littlefs_mlist_remove_nodes[index].id =
            (uint16_t)(0x210U + index);
        open_cfw_test_littlefs_mlist_remove_nodes[index].type =
            (uint8_t)(0x30U + index);
    }

    open_cfw_test_littlefs_mlist_remove_lfs.open_list =
        length ? &open_cfw_test_littlefs_mlist_remove_nodes[0] : NULL;
    open_cfw_test_littlefs_mlist_remove_lfs.seed = 0x2468ACE0U;
    open_cfw_test_littlefs_mlist_remove_lfs.block_count = 3008U;
}

void open_cfw_test_littlefs_mlist_remove_call(uint32_t index)
{
    open_cfw_littlefs_mlist_remove(
        &open_cfw_test_littlefs_mlist_remove_lfs,
        &open_cfw_test_littlefs_mlist_remove_nodes[index]
    );
}

uint32_t open_cfw_test_littlefs_mlist_remove_head_id(void)
{
    return open_cfw_test_littlefs_mlist_remove_node_id_(
        open_cfw_test_littlefs_mlist_remove_lfs.open_list
    );
}

uint32_t open_cfw_test_littlefs_mlist_remove_next_id(uint32_t index)
{
    return open_cfw_test_littlefs_mlist_remove_node_id_(
        open_cfw_test_littlefs_mlist_remove_nodes[index].next
    );
}

uint32_t open_cfw_test_littlefs_mlist_remove_node_id(uint32_t index)
{
    return open_cfw_test_littlefs_mlist_remove_nodes[index].id;
}

uint32_t open_cfw_test_littlefs_mlist_remove_node_type(uint32_t index)
{
    return open_cfw_test_littlefs_mlist_remove_nodes[index].type;
}

uint32_t open_cfw_test_littlefs_mlist_remove_seed(void)
{
    return open_cfw_test_littlefs_mlist_remove_lfs.seed;
}

uint32_t open_cfw_test_littlefs_mlist_remove_block_count(void)
{
    return open_cfw_test_littlefs_mlist_remove_lfs.block_count;
}

size_t open_cfw_test_littlefs_mlist_remove_lfs_size(void)
{
    return sizeof(open_cfw_test_littlefs_mlist_remove_lfs);
}

size_t open_cfw_test_littlefs_mlist_remove_mlist_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_mlist_remove_lfs,
        open_list
    );
}

size_t open_cfw_test_littlefs_mlist_remove_next_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_mlist_remove_node,
        next
    );
}

size_t open_cfw_test_littlefs_mlist_remove_id_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_mlist_remove_node,
        id
    );
}

size_t open_cfw_test_littlefs_mlist_remove_type_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_mlist_remove_node,
        type
    );
}
