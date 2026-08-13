/*
 * SPDX-License-Identifier: MIT
 *
 * Host harness for the source-owned FreeRTOS uxListRemove boundary.
 */

#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_list_remove.c"

enum {
    OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_SENTINEL = 0,
    OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_ITEM_COUNT = 4,
    OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_NULL = 0xFFFFFFFFU
};

static struct open_cfw_freertos_list_remove_list
open_cfw_test_freertos_list_remove_list;
static struct open_cfw_freertos_list_remove_item
open_cfw_test_freertos_list_remove_items[
    OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_ITEM_COUNT
];

static struct open_cfw_freertos_list_remove_item *
open_cfw_test_freertos_list_remove_sentinel(void)
{
    return (struct open_cfw_freertos_list_remove_item *)(void *)
        &open_cfw_test_freertos_list_remove_list.end;
}

static struct open_cfw_freertos_list_remove_item *
open_cfw_test_freertos_list_remove_node(uint32_t identifier)
{
    if (identifier == OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_SENTINEL) {
        return open_cfw_test_freertos_list_remove_sentinel();
    }
    if (
        identifier >= 1U &&
        identifier <= OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_ITEM_COUNT
    ) {
        return &open_cfw_test_freertos_list_remove_items[identifier - 1U];
    }
    return (struct open_cfw_freertos_list_remove_item *)0;
}

static uint32_t open_cfw_test_freertos_list_remove_identifier(
    const struct open_cfw_freertos_list_remove_item *node
)
{
    uint32_t index;

    if (node == (const struct open_cfw_freertos_list_remove_item *)0) {
        return OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_NULL;
    }
    if (node == open_cfw_test_freertos_list_remove_sentinel()) {
        return OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_SENTINEL;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_ITEM_COUNT;
        ++index
    ) {
        if (node == &open_cfw_test_freertos_list_remove_items[index]) {
            return index + 1U;
        }
    }
    return OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_NULL;
}

void open_cfw_test_freertos_list_remove_reset(void)
{
    struct open_cfw_freertos_list_remove_item *sentinel =
        open_cfw_test_freertos_list_remove_sentinel();
    uint32_t index;

    open_cfw_test_freertos_list_remove_list.item_count = 0U;
    open_cfw_test_freertos_list_remove_list.index = sentinel;
    open_cfw_test_freertos_list_remove_list.end.item_value = 0xFFFFFFFFU;
    open_cfw_test_freertos_list_remove_list.end.next = sentinel;
    open_cfw_test_freertos_list_remove_list.end.previous = sentinel;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_REMOVE_ITEM_COUNT;
        ++index
    ) {
        struct open_cfw_freertos_list_remove_item *item =
            &open_cfw_test_freertos_list_remove_items[index];

        item->item_value = 0x11110000U + index;
        item->next = (struct open_cfw_freertos_list_remove_item *)0;
        item->previous = (struct open_cfw_freertos_list_remove_item *)0;
        item->owner = (void *)(uintptr_t)(0x22220000U + index);
        item->container = (struct open_cfw_freertos_list_remove_list *)0;
    }
}

void open_cfw_test_freertos_list_remove_append(uint32_t identifier)
{
    struct open_cfw_freertos_list_remove_item *item =
        open_cfw_test_freertos_list_remove_node(identifier);
    struct open_cfw_freertos_list_remove_item *index =
        open_cfw_test_freertos_list_remove_list.index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = &open_cfw_test_freertos_list_remove_list;
    open_cfw_test_freertos_list_remove_list.item_count++;
}

void open_cfw_test_freertos_list_remove_set_index(uint32_t identifier)
{
    open_cfw_test_freertos_list_remove_list.index =
        open_cfw_test_freertos_list_remove_node(identifier);
}

uint32_t open_cfw_test_freertos_list_remove_remove(uint32_t identifier)
{
    return open_cfw_freertos_list_remove(
        open_cfw_test_freertos_list_remove_node(identifier)
    );
}

uint32_t open_cfw_test_freertos_list_remove_get_count(void)
{
    return open_cfw_test_freertos_list_remove_list.item_count;
}

uint32_t open_cfw_test_freertos_list_remove_get_index(void)
{
    return open_cfw_test_freertos_list_remove_identifier(
        open_cfw_test_freertos_list_remove_list.index
    );
}

uint32_t open_cfw_test_freertos_list_remove_get_next(uint32_t identifier)
{
    return open_cfw_test_freertos_list_remove_identifier(
        open_cfw_test_freertos_list_remove_node(identifier)->next
    );
}

uint32_t open_cfw_test_freertos_list_remove_get_previous(
    uint32_t identifier
)
{
    return open_cfw_test_freertos_list_remove_identifier(
        open_cfw_test_freertos_list_remove_node(identifier)->previous
    );
}

uint32_t open_cfw_test_freertos_list_remove_get_container(
    uint32_t identifier
)
{
    return (
        open_cfw_test_freertos_list_remove_node(identifier)->container ==
        &open_cfw_test_freertos_list_remove_list
    ) ? 1U : 0U;
}

uint32_t open_cfw_test_freertos_list_remove_get_value(uint32_t identifier)
{
    return open_cfw_test_freertos_list_remove_node(identifier)->item_value;
}

uint32_t open_cfw_test_freertos_list_remove_get_owner(uint32_t identifier)
{
    return (uint32_t)(uintptr_t)
        open_cfw_test_freertos_list_remove_node(identifier)->owner;
}
