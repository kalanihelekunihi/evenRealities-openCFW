/*
 * SPDX-License-Identifier: MIT
 *
 * Host harness for the source-owned FreeRTOS vListInsertEnd boundary.
 */

#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_list_insert_end.c"

enum {
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_SENTINEL = 0,
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_ITEM_COUNT = 4,
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_NULL = 0xFFFFFFFFU
};

static struct open_cfw_freertos_list_insert_end_list
open_cfw_test_freertos_list_insert_end_list;
static struct open_cfw_freertos_list_insert_end_item
open_cfw_test_freertos_list_insert_end_items[
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_ITEM_COUNT
];

static struct open_cfw_freertos_list_insert_end_item *
open_cfw_test_freertos_list_insert_end_sentinel(void)
{
    return (struct open_cfw_freertos_list_insert_end_item *)
        (void *)&open_cfw_test_freertos_list_insert_end_list.end;
}

static struct open_cfw_freertos_list_insert_end_item *
open_cfw_test_freertos_list_insert_end_node(uint32_t identifier)
{
    if (identifier == OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_SENTINEL) {
        return open_cfw_test_freertos_list_insert_end_sentinel();
    }
    if (
        identifier >= 1U &&
        identifier <= OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_ITEM_COUNT
    ) {
        return &open_cfw_test_freertos_list_insert_end_items[
            identifier - 1U
        ];
    }
    return (struct open_cfw_freertos_list_insert_end_item *)0;
}

static uint32_t open_cfw_test_freertos_list_insert_end_identifier(
    const struct open_cfw_freertos_list_insert_end_item *node
)
{
    uint32_t index;

    if (node == (const struct open_cfw_freertos_list_insert_end_item *)0) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_NULL;
    }
    if (node == open_cfw_test_freertos_list_insert_end_sentinel()) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_SENTINEL;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_ITEM_COUNT;
        ++index
    ) {
        if (node == &open_cfw_test_freertos_list_insert_end_items[index]) {
            return index + 1U;
        }
    }
    return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_NULL;
}

void open_cfw_test_freertos_list_insert_end_reset(void)
{
    struct open_cfw_freertos_list_insert_end_item *sentinel =
        open_cfw_test_freertos_list_insert_end_sentinel();
    uint32_t index;

    open_cfw_test_freertos_list_insert_end_list.item_count = 0U;
    open_cfw_test_freertos_list_insert_end_list.index = sentinel;
    open_cfw_test_freertos_list_insert_end_list.end.item_value =
        0xFFFFFFFFU;
    open_cfw_test_freertos_list_insert_end_list.end.next = sentinel;
    open_cfw_test_freertos_list_insert_end_list.end.previous = sentinel;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_INSERT_END_ITEM_COUNT;
        ++index
    ) {
        struct open_cfw_freertos_list_insert_end_item *item =
            &open_cfw_test_freertos_list_insert_end_items[index];

        item->item_value = 0x11110000U + index;
        item->next = (struct open_cfw_freertos_list_insert_end_item *)0;
        item->previous =
            (struct open_cfw_freertos_list_insert_end_item *)0;
        item->owner = (void *)(uintptr_t)(0x22220000U + index);
        item->container =
            (struct open_cfw_freertos_list_insert_end_list *)0;
    }
}

void open_cfw_test_freertos_list_insert_end_append(uint32_t identifier)
{
    open_cfw_freertos_list_insert_end(
        &open_cfw_test_freertos_list_insert_end_list,
        open_cfw_test_freertos_list_insert_end_node(identifier)
    );
}

void open_cfw_test_freertos_list_insert_end_set_index(uint32_t identifier)
{
    open_cfw_test_freertos_list_insert_end_list.index =
        open_cfw_test_freertos_list_insert_end_node(identifier);
}

uint32_t open_cfw_test_freertos_list_insert_end_get_count(void)
{
    return open_cfw_test_freertos_list_insert_end_list.item_count;
}

uint32_t open_cfw_test_freertos_list_insert_end_get_index(void)
{
    return open_cfw_test_freertos_list_insert_end_identifier(
        open_cfw_test_freertos_list_insert_end_list.index
    );
}

uint32_t open_cfw_test_freertos_list_insert_end_get_next(
    uint32_t identifier
)
{
    return open_cfw_test_freertos_list_insert_end_identifier(
        open_cfw_test_freertos_list_insert_end_node(identifier)->next
    );
}

uint32_t open_cfw_test_freertos_list_insert_end_get_previous(
    uint32_t identifier
)
{
    return open_cfw_test_freertos_list_insert_end_identifier(
        open_cfw_test_freertos_list_insert_end_node(identifier)->previous
    );
}

uint32_t open_cfw_test_freertos_list_insert_end_get_container(
    uint32_t identifier
)
{
    return (
        open_cfw_test_freertos_list_insert_end_node(identifier)->container ==
        &open_cfw_test_freertos_list_insert_end_list
    ) ? 1U : 0U;
}

uint32_t open_cfw_test_freertos_list_insert_end_get_value(
    uint32_t identifier
)
{
    return open_cfw_test_freertos_list_insert_end_node(
        identifier
    )->item_value;
}

uint32_t open_cfw_test_freertos_list_insert_end_get_owner(
    uint32_t identifier
)
{
    return (uint32_t)(uintptr_t)
        open_cfw_test_freertos_list_insert_end_node(identifier)->owner;
}
