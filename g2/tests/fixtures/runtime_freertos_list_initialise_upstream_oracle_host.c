/*
 * SPDX-License-Identifier: MIT
 *
 * Host wrapper compiling pristine FreeRTOS-Kernel V10.5.1 list.c as the
 * independent oracle for the source-owned vListInitialise boundary.
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
    open_cfw_oracle_freertos_list_initialise_vListInitialise
#define vListInitialiseItem \
    open_cfw_oracle_freertos_list_initialise_vListInitialiseItem
#define vListInsertEnd \
    open_cfw_oracle_freertos_list_initialise_vListInsertEnd
#define vListInsert open_cfw_oracle_freertos_list_initialise_vListInsert
#define uxListRemove open_cfw_oracle_freertos_list_initialise_uxListRemove

#include "../../third_party/freertos-kernel/list.c"

enum {
    OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_SENTINEL = 0,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_POISON = 1,
    OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_NULL = 0xFFFFFFFFU
};

struct open_cfw_oracle_freertos_list_initialise_wrapper {
    uint32_t before;
    List_t list;
    uint32_t after;
};

static struct open_cfw_oracle_freertos_list_initialise_wrapper
open_cfw_oracle_freertos_list_initialise_state;
static ListItem_t open_cfw_oracle_freertos_list_initialise_poison;

static ListItem_t *open_cfw_oracle_freertos_list_initialise_sentinel(void)
{
    return (ListItem_t *)(void *)
        &open_cfw_oracle_freertos_list_initialise_state.list.xListEnd;
}

static uint32_t open_cfw_oracle_freertos_list_initialise_identifier(
    const ListItem_t *item
)
{
    if (item == open_cfw_oracle_freertos_list_initialise_sentinel()) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_SENTINEL;
    }
    if (item == &open_cfw_oracle_freertos_list_initialise_poison) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_POISON;
    }
    if (item == (const ListItem_t *)0) {
        return OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_NULL;
    }
    return OPEN_CFW_ORACLE_FREERTOS_LIST_INITIALISE_NULL;
}

void open_cfw_oracle_freertos_list_initialise_reset(uint32_t seed)
{
    open_cfw_oracle_freertos_list_initialise_state.before =
        0xA5A50000U | (seed & 0xFFFFU);
    open_cfw_oracle_freertos_list_initialise_state.list.uxNumberOfItems =
        0x11110000U | (seed & 0xFFFFU);
    open_cfw_oracle_freertos_list_initialise_state.list.pxIndex =
        &open_cfw_oracle_freertos_list_initialise_poison;
    open_cfw_oracle_freertos_list_initialise_state.list.xListEnd.xItemValue =
        0x22220000U | (seed & 0xFFFFU);
    open_cfw_oracle_freertos_list_initialise_state.list.xListEnd.pxNext =
        &open_cfw_oracle_freertos_list_initialise_poison;
    open_cfw_oracle_freertos_list_initialise_state.list.xListEnd.pxPrevious =
        &open_cfw_oracle_freertos_list_initialise_poison;
    open_cfw_oracle_freertos_list_initialise_state.after =
        0x5A5A0000U | (seed & 0xFFFFU);
}

void open_cfw_oracle_freertos_list_initialise_execute(void)
{
    open_cfw_oracle_freertos_list_initialise_vListInitialise(
        &open_cfw_oracle_freertos_list_initialise_state.list
    );
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_before(void)
{
    return open_cfw_oracle_freertos_list_initialise_state.before;
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_after(void)
{
    return open_cfw_oracle_freertos_list_initialise_state.after;
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_count(void)
{
    return
        open_cfw_oracle_freertos_list_initialise_state.list.uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_index(void)
{
    return open_cfw_oracle_freertos_list_initialise_identifier(
        open_cfw_oracle_freertos_list_initialise_state.list.pxIndex
    );
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_end_value(void)
{
    return
        open_cfw_oracle_freertos_list_initialise_state.list.xListEnd
            .xItemValue;
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_end_next(void)
{
    return open_cfw_oracle_freertos_list_initialise_identifier(
        open_cfw_oracle_freertos_list_initialise_state.list.xListEnd.pxNext
    );
}

uint32_t open_cfw_oracle_freertos_list_initialise_get_end_previous(void)
{
    return open_cfw_oracle_freertos_list_initialise_identifier(
        open_cfw_oracle_freertos_list_initialise_state.list.xListEnd
            .pxPrevious
    );
}
