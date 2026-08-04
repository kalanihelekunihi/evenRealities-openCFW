/*
 * SPDX-License-Identifier: MIT
 *
 * Host harness for the source-owned FreeRTOS vListInsert boundary.
 */

#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_list_insert.c"

enum {
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_SENTINEL = 0,
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_ITEM_COUNT = 6,
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_NULL = 0xFFFFFFFFU
};

struct open_cfw_test_freertos_list_insert_wrapper {
    uint32_t before;
    struct open_cfw_freertos_list_insert_list list;
    uint32_t after;
};

static struct open_cfw_test_freertos_list_insert_wrapper
open_cfw_test_freertos_list_insert_state;
static struct open_cfw_freertos_list_insert_item
open_cfw_test_freertos_list_insert_items[
    OPEN_CFW_TEST_FREERTOS_LIST_INSERT_ITEM_COUNT
];

static struct open_cfw_freertos_list_insert_item *
open_cfw_test_freertos_list_insert_sentinel(void)
{
    return (struct open_cfw_freertos_list_insert_item *)(void *)
        &open_cfw_test_freertos_list_insert_state.list.end;
}

static struct open_cfw_freertos_list_insert_item *
open_cfw_test_freertos_list_insert_node(uint32_t identifier)
{
    if (identifier == OPEN_CFW_TEST_FREERTOS_LIST_INSERT_SENTINEL) {
        return open_cfw_test_freertos_list_insert_sentinel();
    }
    if (
        identifier >= 1U &&
        identifier <= OPEN_CFW_TEST_FREERTOS_LIST_INSERT_ITEM_COUNT
    ) {
        return &open_cfw_test_freertos_list_insert_items[identifier - 1U];
    }
    return (struct open_cfw_freertos_list_insert_item *)0;
}

static uint32_t open_cfw_test_freertos_list_insert_identifier(
    const struct open_cfw_freertos_list_insert_item *node
)
{
    uint32_t index;

    if (node == (const struct open_cfw_freertos_list_insert_item *)0) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_NULL;
    }
    if (node == open_cfw_test_freertos_list_insert_sentinel()) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_SENTINEL;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_INSERT_ITEM_COUNT;
        ++index
    ) {
        if (node == &open_cfw_test_freertos_list_insert_items[index]) {
            return index + 1U;
        }
    }
    return OPEN_CFW_TEST_FREERTOS_LIST_INSERT_NULL;
}

void open_cfw_test_freertos_list_insert_reset(void)
{
    struct open_cfw_freertos_list_insert_item *sentinel =
        open_cfw_test_freertos_list_insert_sentinel();
    uint32_t index;

    open_cfw_test_freertos_list_insert_state.before = 0xA5A5C3C3U;
    open_cfw_test_freertos_list_insert_state.list.item_count = 0U;
    open_cfw_test_freertos_list_insert_state.list.index = sentinel;
    open_cfw_test_freertos_list_insert_state.list.end.item_value =
        0xFFFFFFFFU;
    open_cfw_test_freertos_list_insert_state.list.end.next = sentinel;
    open_cfw_test_freertos_list_insert_state.list.end.previous = sentinel;
    open_cfw_test_freertos_list_insert_state.after = 0x5A5A3C3CU;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_FREERTOS_LIST_INSERT_ITEM_COUNT;
        ++index
    ) {
        struct open_cfw_freertos_list_insert_item *item =
            &open_cfw_test_freertos_list_insert_items[index];

        item->item_value = 0x11110000U + index;
        item->next = (struct open_cfw_freertos_list_insert_item *)0;
        item->previous =
            (struct open_cfw_freertos_list_insert_item *)0;
        item->owner = (void *)(uintptr_t)(0x22220000U + index);
        item->container =
            (struct open_cfw_freertos_list_insert_list *)0;
    }
}

void open_cfw_test_freertos_list_insert_set_value(
    uint32_t identifier,
    uint32_t value
)
{
    open_cfw_test_freertos_list_insert_node(identifier)->item_value = value;
}

void open_cfw_test_freertos_list_insert_execute(uint32_t identifier)
{
    open_cfw_freertos_list_insert(
        &open_cfw_test_freertos_list_insert_state.list,
        open_cfw_test_freertos_list_insert_node(identifier)
    );
}

uint32_t open_cfw_test_freertos_list_insert_get_before(void)
{
    return open_cfw_test_freertos_list_insert_state.before;
}

uint32_t open_cfw_test_freertos_list_insert_get_after(void)
{
    return open_cfw_test_freertos_list_insert_state.after;
}

uint32_t open_cfw_test_freertos_list_insert_get_count(void)
{
    return open_cfw_test_freertos_list_insert_state.list.item_count;
}

uint32_t open_cfw_test_freertos_list_insert_get_index(void)
{
    return open_cfw_test_freertos_list_insert_identifier(
        open_cfw_test_freertos_list_insert_state.list.index
    );
}

uint32_t open_cfw_test_freertos_list_insert_get_next(uint32_t identifier)
{
    return open_cfw_test_freertos_list_insert_identifier(
        open_cfw_test_freertos_list_insert_node(identifier)->next
    );
}

uint32_t open_cfw_test_freertos_list_insert_get_previous(
    uint32_t identifier
)
{
    return open_cfw_test_freertos_list_insert_identifier(
        open_cfw_test_freertos_list_insert_node(identifier)->previous
    );
}

uint32_t open_cfw_test_freertos_list_insert_get_container(
    uint32_t identifier
)
{
    return (
        open_cfw_test_freertos_list_insert_node(identifier)->container ==
        &open_cfw_test_freertos_list_insert_state.list
    ) ? 1U : 0U;
}

uint32_t open_cfw_test_freertos_list_insert_get_value(uint32_t identifier)
{
    return open_cfw_test_freertos_list_insert_node(identifier)->item_value;
}

uint32_t open_cfw_test_freertos_list_insert_get_owner(uint32_t identifier)
{
    return (uint32_t)(uintptr_t)
        open_cfw_test_freertos_list_insert_node(identifier)->owner;
}
