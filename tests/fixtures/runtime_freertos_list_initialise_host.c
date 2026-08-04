/*
 * SPDX-License-Identifier: MIT
 *
 * Host harness for the source-owned FreeRTOS vListInitialise boundary.
 */

#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_freertos_list_initialise.c"

enum {
    OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_SENTINEL = 0,
    OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_POISON = 1,
    OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_NULL = 0xFFFFFFFFU
};

struct open_cfw_test_freertos_list_initialise_wrapper {
    uint32_t before;
    struct open_cfw_freertos_list_initialise_list list;
    uint32_t after;
};

static struct open_cfw_test_freertos_list_initialise_wrapper
open_cfw_test_freertos_list_initialise_state;
static struct open_cfw_freertos_list_initialise_item
open_cfw_test_freertos_list_initialise_poison;

static struct open_cfw_freertos_list_initialise_item *
open_cfw_test_freertos_list_initialise_sentinel(void)
{
    return (struct open_cfw_freertos_list_initialise_item *)(void *)
        &open_cfw_test_freertos_list_initialise_state.list.end;
}

static uint32_t open_cfw_test_freertos_list_initialise_identifier(
    const struct open_cfw_freertos_list_initialise_item *item
)
{
    if (item == open_cfw_test_freertos_list_initialise_sentinel()) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_SENTINEL;
    }
    if (item == &open_cfw_test_freertos_list_initialise_poison) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_POISON;
    }
    if (
        item ==
        (const struct open_cfw_freertos_list_initialise_item *)0
    ) {
        return OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_NULL;
    }
    return OPEN_CFW_TEST_FREERTOS_LIST_INITIALISE_NULL;
}

void open_cfw_test_freertos_list_initialise_reset(uint32_t seed)
{
    open_cfw_test_freertos_list_initialise_state.before =
        0xA5A50000U | (seed & 0xFFFFU);
    open_cfw_test_freertos_list_initialise_state.list.item_count =
        0x11110000U | (seed & 0xFFFFU);
    open_cfw_test_freertos_list_initialise_state.list.index =
        &open_cfw_test_freertos_list_initialise_poison;
    open_cfw_test_freertos_list_initialise_state.list.end.item_value =
        0x22220000U | (seed & 0xFFFFU);
    open_cfw_test_freertos_list_initialise_state.list.end.next =
        &open_cfw_test_freertos_list_initialise_poison;
    open_cfw_test_freertos_list_initialise_state.list.end.previous =
        &open_cfw_test_freertos_list_initialise_poison;
    open_cfw_test_freertos_list_initialise_state.after =
        0x5A5A0000U | (seed & 0xFFFFU);
}

void open_cfw_test_freertos_list_initialise_execute(void)
{
    open_cfw_freertos_list_initialise(
        &open_cfw_test_freertos_list_initialise_state.list
    );
}

uint32_t open_cfw_test_freertos_list_initialise_get_before(void)
{
    return open_cfw_test_freertos_list_initialise_state.before;
}

uint32_t open_cfw_test_freertos_list_initialise_get_after(void)
{
    return open_cfw_test_freertos_list_initialise_state.after;
}

uint32_t open_cfw_test_freertos_list_initialise_get_count(void)
{
    return open_cfw_test_freertos_list_initialise_state.list.item_count;
}

uint32_t open_cfw_test_freertos_list_initialise_get_index(void)
{
    return open_cfw_test_freertos_list_initialise_identifier(
        open_cfw_test_freertos_list_initialise_state.list.index
    );
}

uint32_t open_cfw_test_freertos_list_initialise_get_end_value(void)
{
    return open_cfw_test_freertos_list_initialise_state.list.end.item_value;
}

uint32_t open_cfw_test_freertos_list_initialise_get_end_next(void)
{
    return open_cfw_test_freertos_list_initialise_identifier(
        open_cfw_test_freertos_list_initialise_state.list.end.next
    );
}

uint32_t open_cfw_test_freertos_list_initialise_get_end_previous(void)
{
    return open_cfw_test_freertos_list_initialise_identifier(
        open_cfw_test_freertos_list_initialise_state.list.end.previous
    );
}
