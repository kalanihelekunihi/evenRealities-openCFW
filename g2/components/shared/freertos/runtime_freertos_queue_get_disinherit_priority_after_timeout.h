/*
 * SPDX-License-Identifier: MIT
 *
 * Production FreeRTOS queue/list ABI for the Even Realities G2
 * Apollo-main image.  The fixed-width address fields describe the 32-bit
 * target layout; the access macros remain overridable for hosted validation.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_QUEUE_GET_DISINHERIT_PRIORITY_AFTER_TIMEOUT_H
#define OPEN_CFW_RUNTIME_FREERTOS_QUEUE_GET_DISINHERIT_PRIORITY_AFTER_TIMEOUT_H

typedef __UINT8_TYPE__ open_cfw_freertos_disinherit_byte;
typedef __UINT32_TYPE__ open_cfw_freertos_disinherit_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_disinherit_address;
typedef __UINTPTR_TYPE__ open_cfw_freertos_disinherit_uintptr;

struct open_cfw_freertos_disinherit_list_item_layout {
    open_cfw_freertos_disinherit_ubase_type item_value;
    open_cfw_freertos_disinherit_address next;
    open_cfw_freertos_disinherit_address previous;
    open_cfw_freertos_disinherit_address owner;
    open_cfw_freertos_disinherit_address container;
};

struct open_cfw_freertos_disinherit_mini_list_item_layout {
    open_cfw_freertos_disinherit_ubase_type item_value;
    open_cfw_freertos_disinherit_address next;
    open_cfw_freertos_disinherit_address previous;
};

struct open_cfw_freertos_disinherit_list_layout {
    open_cfw_freertos_disinherit_ubase_type number_of_items;
    open_cfw_freertos_disinherit_address index;
    struct open_cfw_freertos_disinherit_mini_list_item_layout end;
};

struct open_cfw_freertos_disinherit_queue_receive_wait_layout {
    open_cfw_freertos_disinherit_byte prefix[0x24];
    struct open_cfw_freertos_disinherit_list_layout tasks_waiting_to_receive;
};

enum {
    OPEN_CFW_FREERTOS_DISINHERIT_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_DISINHERIT_IDLE_PRIORITY = 0U,
    OPEN_CFW_FREERTOS_DISINHERIT_RECEIVE_WAIT_OFFSET = 0x24U,
    OPEN_CFW_FREERTOS_DISINHERIT_HEAD_POINTER_OFFSET = 0x30U
};

_Static_assert(
    sizeof(open_cfw_freertos_disinherit_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_disinherit_list_item_layout) == 20U,
    "G2 FreeRTOS ListItem_t layout changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_disinherit_list_item_layout) == 4U,
    "G2 FreeRTOS ListItem_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_disinherit_list_item_layout,
        item_value
    ) == 0U,
    "G2 FreeRTOS ListItem_t value offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_disinherit_mini_list_item_layout) == 12U,
    "G2 FreeRTOS MiniListItem_t layout changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_disinherit_list_layout) == 20U,
    "G2 FreeRTOS List_t layout changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_disinherit_list_layout) == 4U,
    "G2 FreeRTOS List_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_disinherit_list_layout,
        end.next
    ) == 0x0CU,
    "G2 FreeRTOS List_t head pointer offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_disinherit_queue_receive_wait_layout,
        tasks_waiting_to_receive
    ) == OPEN_CFW_FREERTOS_DISINHERIT_RECEIVE_WAIT_OFFSET,
    "G2 Queue_t receive-wait list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_disinherit_queue_receive_wait_layout,
        tasks_waiting_to_receive.end.next
    ) == OPEN_CFW_FREERTOS_DISINHERIT_HEAD_POINTER_OFFSET,
    "G2 Queue_t receive-wait head pointer offset changed"
);

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_LIST_LENGTH
#define OPEN_CFW_FREERTOS_DISINHERIT_LIST_LENGTH(queue) \
    (*(const volatile open_cfw_freertos_disinherit_ubase_type *) \
        ((const open_cfw_freertos_disinherit_byte *)(queue) + \
         OPEN_CFW_FREERTOS_DISINHERIT_RECEIVE_WAIT_OFFSET))
#endif

#ifndef OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE
#define OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE(queue) \
    (*(const volatile open_cfw_freertos_disinherit_ubase_type *) \
        (open_cfw_freertos_disinherit_uintptr) \
        (*(const volatile open_cfw_freertos_disinherit_address *) \
            ((const open_cfw_freertos_disinherit_byte *)(queue) + \
             OPEN_CFW_FREERTOS_DISINHERIT_HEAD_POINTER_OFFSET)))
#endif

open_cfw_freertos_disinherit_ubase_type
open_cfw_freertos_queue_get_disinherit_priority_after_timeout(
    const void *queue
);

#endif
