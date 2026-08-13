/*
 * SPDX-License-Identifier: MIT
 *
 * Shared FreeRTOS next-task-unblock-time ABI for the Even Realities G2
 * Apollo-main image. The recovered kernel globals and List_t layout remain
 * explicit so this private scheduler helper is independently testable and
 * relocation-free.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_RESET_NEXT_TASK_UNBLOCK_TIME_H
#define OPEN_CFW_RUNTIME_FREERTOS_RESET_NEXT_TASK_UNBLOCK_TIME_H

typedef __UINT32_TYPE__ open_cfw_freertos_reset_unblock_tick_type;
typedef __UINT32_TYPE__ open_cfw_freertos_reset_unblock_ubase_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_reset_unblock_uintptr;

enum {
    OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_ADDRESS = 0x20074A24U,
    OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_ADDRESS = 0x20074A50U,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_MINI_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_COUNT_OFFSET = 0x00U,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_END_OFFSET = 0x08U,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_END_NEXT_OFFSET = 0x0CU,
    OPEN_CFW_FREERTOS_RESET_UNBLOCK_ITEM_VALUE_OFFSET = 0x00U
};

struct open_cfw_freertos_reset_unblock_list;

struct open_cfw_freertos_reset_unblock_item {
    open_cfw_freertos_reset_unblock_tick_type item_value;
    struct open_cfw_freertos_reset_unblock_item *next;
    struct open_cfw_freertos_reset_unblock_item *previous;
    void *owner;
    struct open_cfw_freertos_reset_unblock_list *container;
};

struct open_cfw_freertos_reset_unblock_mini_item {
    open_cfw_freertos_reset_unblock_tick_type item_value;
    struct open_cfw_freertos_reset_unblock_item *next;
    struct open_cfw_freertos_reset_unblock_item *previous;
};

struct open_cfw_freertos_reset_unblock_list {
    volatile open_cfw_freertos_reset_unblock_ubase_type item_count;
    struct open_cfw_freertos_reset_unblock_item *index;
    struct open_cfw_freertos_reset_unblock_mini_item end;
};

_Static_assert(
    sizeof(open_cfw_freertos_reset_unblock_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_reset_unblock_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_reset_unblock_item) ==
        OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_reset_unblock_mini_item) ==
        OPEN_CFW_FREERTOS_RESET_UNBLOCK_MINI_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_reset_unblock_list) ==
        OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_reset_unblock_list,
        item_count
    ) == OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_COUNT_OFFSET,
    "G2 FreeRTOS List_t count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_reset_unblock_list,
        end
    ) == OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_END_OFFSET,
    "G2 FreeRTOS List_t end offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_reset_unblock_list,
        end.next
    ) == OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_END_NEXT_OFFSET,
    "G2 FreeRTOS List_t end-next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_reset_unblock_item,
        item_value
    ) == OPEN_CFW_FREERTOS_RESET_UNBLOCK_ITEM_VALUE_OFFSET,
    "G2 FreeRTOS ListItem_t value offset changed"
);
#endif

#ifndef OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD
#define OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD() \
    (*(struct open_cfw_freertos_reset_unblock_list * volatile *) \
        (open_cfw_freertos_reset_unblock_uintptr) \
        OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_DELAYED_LIST_COUNT_READ
#define OPEN_CFW_FREERTOS_DELAYED_LIST_COUNT_READ(list) \
    ((list)->item_count)
#endif

#ifndef OPEN_CFW_FREERTOS_DELAYED_LIST_HEAD_VALUE_READ
#define OPEN_CFW_FREERTOS_DELAYED_LIST_HEAD_VALUE_READ(list) \
    ((list)->end.next->item_value)
#endif

#ifndef OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_STORE
#define OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_STORE(value) \
    (*(volatile open_cfw_freertos_reset_unblock_tick_type *) \
        (open_cfw_freertos_reset_unblock_uintptr) \
        OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_ADDRESS = (value))
#endif

void open_cfw_freertos_task_reset_next_task_unblock_time(void);

#endif
