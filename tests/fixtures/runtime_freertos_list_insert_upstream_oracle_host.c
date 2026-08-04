/*
 * SPDX-License-Identifier: MIT
 *
 * Host wrapper compiling pristine FreeRTOS-Kernel V10.5.1 list.c as the
 * independent oracle for the source-owned vListInsert boundary.
 */

#include <stdint.h>

typedef uint32_t TickType_t;
typedef uint32_t UBaseType_t;

struct xLIST;
struct xLIST_ITEM {
    TickType_t xItemValue;
    struct xLIST_ITEM *pxNext;
    struct xLIST_ITEM *pxPrevious;
    void *pvOwner;
    struct xLIST *pxContainer;
};
typedef struct xLIST_ITEM ListItem_t;

struct xMINI_LIST_ITEM {
    TickType_t xItemValue;
    struct xLIST_ITEM *pxNext;
    struct xLIST_ITEM *pxPrevious;
};
typedef struct xMINI_LIST_ITEM MiniListItem_t;

typedef struct xLIST {
    volatile UBaseType_t uxNumberOfItems;
    ListItem_t *pxIndex;
    MiniListItem_t xListEnd;
} List_t;

#define INC_FREERTOS_H
#define LIST_H
#define configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES 0
#define configUSE_MINI_LIST_ITEM 1
#define portMAX_DELAY ((TickType_t)0xFFFFFFFFU)
#define listSET_FIRST_LIST_ITEM_INTEGRITY_CHECK_VALUE(item)
#define listSET_SECOND_LIST_ITEM_INTEGRITY_CHECK_VALUE(item)
#define listSET_LIST_INTEGRITY_CHECK_1_VALUE(list)
#define listSET_LIST_INTEGRITY_CHECK_2_VALUE(list)
#define listTEST_LIST_ITEM_INTEGRITY(item)
#define listTEST_LIST_INTEGRITY(list)
#define mtCOVERAGE_TEST_DELAY()
#define mtCOVERAGE_TEST_MARKER()

#define vListInitialise \
    open_cfw_oracle_freertos_list_insert_vListInitialise
#define vListInitialiseItem \
    open_cfw_oracle_freertos_list_insert_vListInitialiseItem
#define vListInsertEnd \
    open_cfw_oracle_freertos_list_insert_vListInsertEnd
#define vListInsert \
    open_cfw_oracle_freertos_list_insert_vListInsert
#define uxListRemove \
    open_cfw_oracle_freertos_list_insert_uxListRemove

#include "../../third_party/freertos-kernel/list.c"

enum {
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_SENTINEL = 0,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_ITEM_COUNT = 6,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_NULL = 0xFFFFFFFFU
};

struct open_cfw_oracle_freertos_list_insert_wrapper {
    uint32_t before;
    List_t list;
    uint32_t after;
};

static struct open_cfw_oracle_freertos_list_insert_wrapper
open_cfw_oracle_freertos_list_insert_state;
static ListItem_t open_cfw_oracle_freertos_list_insert_items[
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_ITEM_COUNT
];

static ListItem_t *open_cfw_oracle_freertos_list_insert_sentinel(void)
{
    return (ListItem_t *)(void *)
        &open_cfw_oracle_freertos_list_insert_state.list.xListEnd;
}

static ListItem_t *open_cfw_oracle_freertos_list_insert_node(
    uint32_t identifier
)
{
    if (identifier == OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_SENTINEL) {
        return open_cfw_oracle_freertos_list_insert_sentinel();
    }
    if (
        identifier >= 1U &&
        identifier <= OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_ITEM_COUNT
    ) {
        return &open_cfw_oracle_freertos_list_insert_items[identifier - 1U];
    }
    return (ListItem_t *)0;
}

static uint32_t open_cfw_oracle_freertos_list_insert_identifier(
    const ListItem_t *node
)
{
    uint32_t index;

    if (node == (const ListItem_t *)0) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_NULL;
    }
    if (node == open_cfw_oracle_freertos_list_insert_sentinel()) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_SENTINEL;
    }
    for (
        index = 0U;
        index < OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_ITEM_COUNT;
        ++index
    ) {
        if (node == &open_cfw_oracle_freertos_list_insert_items[index]) {
            return index + 1U;
        }
    }
    return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_NULL;
}

void open_cfw_oracle_freertos_list_insert_reset(void)
{
    uint32_t index;

    open_cfw_oracle_freertos_list_insert_state.before = 0xA5A5C3C3U;
    open_cfw_oracle_freertos_list_insert_vListInitialise(
        &open_cfw_oracle_freertos_list_insert_state.list
    );
    open_cfw_oracle_freertos_list_insert_state.after = 0x5A5A3C3CU;

    for (
        index = 0U;
        index < OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_ITEM_COUNT;
        ++index
    ) {
        ListItem_t *item =
            &open_cfw_oracle_freertos_list_insert_items[index];

        item->xItemValue = 0x11110000U + index;
        item->pxNext = (ListItem_t *)0;
        item->pxPrevious = (ListItem_t *)0;
        item->pvOwner = (void *)(uintptr_t)(0x22220000U + index);
        open_cfw_oracle_freertos_list_insert_vListInitialiseItem(item);
    }
}

void open_cfw_oracle_freertos_list_insert_set_value(
    uint32_t identifier,
    uint32_t value
)
{
    open_cfw_oracle_freertos_list_insert_node(identifier)->xItemValue =
        value;
}

void open_cfw_oracle_freertos_list_insert_execute(uint32_t identifier)
{
    open_cfw_oracle_freertos_list_insert_vListInsert(
        &open_cfw_oracle_freertos_list_insert_state.list,
        open_cfw_oracle_freertos_list_insert_node(identifier)
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_get_before(void)
{
    return open_cfw_oracle_freertos_list_insert_state.before;
}

uint32_t open_cfw_oracle_freertos_list_insert_get_after(void)
{
    return open_cfw_oracle_freertos_list_insert_state.after;
}

uint32_t open_cfw_oracle_freertos_list_insert_get_count(void)
{
    return open_cfw_oracle_freertos_list_insert_state.list.uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_list_insert_get_index(void)
{
    return open_cfw_oracle_freertos_list_insert_identifier(
        open_cfw_oracle_freertos_list_insert_state.list.pxIndex
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_get_next(uint32_t identifier)
{
    return open_cfw_oracle_freertos_list_insert_identifier(
        open_cfw_oracle_freertos_list_insert_node(identifier)->pxNext
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_get_previous(
    uint32_t identifier
)
{
    return open_cfw_oracle_freertos_list_insert_identifier(
        open_cfw_oracle_freertos_list_insert_node(identifier)->pxPrevious
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_get_container(
    uint32_t identifier
)
{
    return (
        open_cfw_oracle_freertos_list_insert_node(identifier)->pxContainer ==
        &open_cfw_oracle_freertos_list_insert_state.list
    ) ? 1U : 0U;
}

uint32_t open_cfw_oracle_freertos_list_insert_get_value(
    uint32_t identifier
)
{
    return open_cfw_oracle_freertos_list_insert_node(
        identifier
    )->xItemValue;
}

uint32_t open_cfw_oracle_freertos_list_insert_get_owner(
    uint32_t identifier
)
{
    return (uint32_t)(uintptr_t)
        open_cfw_oracle_freertos_list_insert_node(identifier)->pvOwner;
}
