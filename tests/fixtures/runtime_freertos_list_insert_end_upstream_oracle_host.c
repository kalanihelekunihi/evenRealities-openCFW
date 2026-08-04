/*
 * SPDX-License-Identifier: MIT
 *
 * Host wrapper compiling pristine FreeRTOS-Kernel V10.5.1 list.c as the
 * independent oracle for the source-owned vListInsertEnd boundary.
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
    open_cfw_oracle_freertos_list_insert_end_vListInitialise
#define vListInitialiseItem \
    open_cfw_oracle_freertos_list_insert_end_vListInitialiseItem
#define vListInsertEnd \
    open_cfw_oracle_freertos_list_insert_end_vListInsertEnd
#define vListInsert \
    open_cfw_oracle_freertos_list_insert_end_vListInsert
#define uxListRemove \
    open_cfw_oracle_freertos_list_insert_end_uxListRemove

#include "../../third_party/freertos-kernel/list.c"

enum {
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_SENTINEL = 0,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_ITEM_COUNT = 4,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_NULL = 0xFFFFFFFFU
};

static List_t open_cfw_oracle_freertos_list_insert_end_list;
static ListItem_t open_cfw_oracle_freertos_list_insert_end_items[
    OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_ITEM_COUNT
];

static ListItem_t *open_cfw_oracle_freertos_list_insert_end_sentinel(void)
{
    return (ListItem_t *)(void *)
        &open_cfw_oracle_freertos_list_insert_end_list.xListEnd;
}

static ListItem_t *open_cfw_oracle_freertos_list_insert_end_node(
    uint32_t identifier
)
{
    if (identifier == OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_SENTINEL) {
        return open_cfw_oracle_freertos_list_insert_end_sentinel();
    }
    if (
        identifier >= 1U &&
        identifier <= OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_ITEM_COUNT
    ) {
        return &open_cfw_oracle_freertos_list_insert_end_items[
            identifier - 1U
        ];
    }
    return (ListItem_t *)0;
}

static uint32_t open_cfw_oracle_freertos_list_insert_end_identifier(
    const ListItem_t *node
)
{
    uint32_t index;

    if (node == (const ListItem_t *)0) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_NULL;
    }
    if (node == open_cfw_oracle_freertos_list_insert_end_sentinel()) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_SENTINEL;
    }
    for (
        index = 0U;
        index < OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_ITEM_COUNT;
        ++index
    ) {
        if (node == &open_cfw_oracle_freertos_list_insert_end_items[index]) {
            return index + 1U;
        }
    }
    return OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_NULL;
}

void open_cfw_oracle_freertos_list_insert_end_reset(void)
{
    uint32_t index;

    open_cfw_oracle_freertos_list_insert_end_vListInitialise(
        &open_cfw_oracle_freertos_list_insert_end_list
    );
    for (
        index = 0U;
        index < OPEN_CFW_ORACLE_FREERTOS_LIST_INSERT_END_ITEM_COUNT;
        ++index
    ) {
        ListItem_t *item =
            &open_cfw_oracle_freertos_list_insert_end_items[index];

        item->pxNext = (ListItem_t *)0;
        item->pxPrevious = (ListItem_t *)0;
        open_cfw_oracle_freertos_list_insert_end_vListInitialiseItem(item);
        item->xItemValue = 0x11110000U + index;
        item->pvOwner = (void *)(uintptr_t)(0x22220000U + index);
    }
}

void open_cfw_oracle_freertos_list_insert_end_append(uint32_t identifier)
{
    open_cfw_oracle_freertos_list_insert_end_vListInsertEnd(
        &open_cfw_oracle_freertos_list_insert_end_list,
        open_cfw_oracle_freertos_list_insert_end_node(identifier)
    );
}

void open_cfw_oracle_freertos_list_insert_end_set_index(
    uint32_t identifier
)
{
    open_cfw_oracle_freertos_list_insert_end_list.pxIndex =
        open_cfw_oracle_freertos_list_insert_end_node(identifier);
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_count(void)
{
    return open_cfw_oracle_freertos_list_insert_end_list.uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_index(void)
{
    return open_cfw_oracle_freertos_list_insert_end_identifier(
        open_cfw_oracle_freertos_list_insert_end_list.pxIndex
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_next(
    uint32_t identifier
)
{
    return open_cfw_oracle_freertos_list_insert_end_identifier(
        open_cfw_oracle_freertos_list_insert_end_node(identifier)->pxNext
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_previous(
    uint32_t identifier
)
{
    return open_cfw_oracle_freertos_list_insert_end_identifier(
        open_cfw_oracle_freertos_list_insert_end_node(
            identifier
        )->pxPrevious
    );
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_container(
    uint32_t identifier
)
{
    return (
        open_cfw_oracle_freertos_list_insert_end_node(
            identifier
        )->pxContainer ==
        &open_cfw_oracle_freertos_list_insert_end_list
    ) ? 1U : 0U;
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_value(
    uint32_t identifier
)
{
    return open_cfw_oracle_freertos_list_insert_end_node(
        identifier
    )->xItemValue;
}

uint32_t open_cfw_oracle_freertos_list_insert_end_get_owner(
    uint32_t identifier
)
{
    return (uint32_t)(uintptr_t)
        open_cfw_oracle_freertos_list_insert_end_node(
            identifier
        )->pvOwner;
}
