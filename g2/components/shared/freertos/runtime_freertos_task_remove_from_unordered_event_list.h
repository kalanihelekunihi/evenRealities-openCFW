/*
 * SPDX-License-Identifier: MIT
 *
 * Isolated G2 ABI for the FreeRTOS-Kernel V10.5.1
 * vTaskRemoveFromUnorderedEventList() production source leaf.  Recovered
 * scheduler globals and the reset-next provider remain explicit and
 * host-overridable.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_REMOVE_FROM_UNORDERED_EVENT_LIST_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_REMOVE_FROM_UNORDERED_EVENT_LIST_H

typedef __INT32_TYPE__ open_cfw_freertos_unordered_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_unordered_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_unordered_tick_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_unordered_uintptr;

enum {
    OPEN_CFW_FREERTOS_UNORDERED_FALSE = 0,
    OPEN_CFW_FREERTOS_UNORDERED_TRUE = 1,
    OPEN_CFW_FREERTOS_UNORDERED_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_UNORDERED_VALUE_IN_USE = 0x80000000U,
    OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK_ADDRESS = 0x005FA0A4U,
    OPEN_CFW_FREERTOS_UNORDERED_RESET_UNBLOCK_ADDRESS = 0x00455876U,
    OPEN_CFW_FREERTOS_UNORDERED_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_ADDRESS = 0x20074A44U,
    OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_ADDRESS = 0x20074A58U,
    OPEN_CFW_FREERTOS_UNORDERED_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_UNORDERED_MINI_LIST_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_UNORDERED_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_UNORDERED_TCB_STATE_ITEM_OFFSET = 0x04U,
    OPEN_CFW_FREERTOS_UNORDERED_TCB_EVENT_ITEM_OFFSET = 0x18U,
    OPEN_CFW_FREERTOS_UNORDERED_TCB_PRIORITY_OFFSET = 0x2CU,
    OPEN_CFW_FREERTOS_UNORDERED_TCB_SIZE = 0x70U
};

struct open_cfw_freertos_unordered_list;

struct open_cfw_freertos_unordered_list_item {
    open_cfw_freertos_unordered_tick_type item_value;
    struct open_cfw_freertos_unordered_list_item *next;
    struct open_cfw_freertos_unordered_list_item *previous;
    void *owner;
    struct open_cfw_freertos_unordered_list *container;
};

struct open_cfw_freertos_unordered_mini_list_item {
    open_cfw_freertos_unordered_tick_type item_value;
    struct open_cfw_freertos_unordered_list_item *next;
    struct open_cfw_freertos_unordered_list_item *previous;
};

struct open_cfw_freertos_unordered_list {
    volatile open_cfw_freertos_unordered_ubase_type item_count;
    struct open_cfw_freertos_unordered_list_item *index;
    struct open_cfw_freertos_unordered_mini_list_item end;
};

struct open_cfw_freertos_unordered_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_unordered_list_item state_list_item;
    struct open_cfw_freertos_unordered_list_item event_list_item;
    open_cfw_freertos_unordered_ubase_type priority;
    void *stack_base;
    char task_name[32];
    open_cfw_freertos_unordered_ubase_type stack_depth;
    open_cfw_freertos_unordered_ubase_type tcb_number;
    open_cfw_freertos_unordered_ubase_type task_number;
    open_cfw_freertos_unordered_ubase_type base_priority;
    open_cfw_freertos_unordered_ubase_type mutexes_held;
    open_cfw_freertos_unordered_ubase_type notification_value;
    unsigned char notification_state;
    unsigned char statically_allocated;
    unsigned char padding[2];
};

_Static_assert(
    sizeof(open_cfw_freertos_unordered_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_unordered_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_unordered_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_unordered_list_item) ==
        OPEN_CFW_FREERTOS_UNORDERED_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_unordered_mini_list_item) ==
        OPEN_CFW_FREERTOS_UNORDERED_MINI_LIST_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_unordered_list) ==
        OPEN_CFW_FREERTOS_UNORDERED_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_unordered_tcb) ==
        OPEN_CFW_FREERTOS_UNORDERED_TCB_SIZE,
    "G2 FreeRTOS TCB_t size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_list_item,
        next
    ) == 0x04U,
    "G2 FreeRTOS ListItem_t next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_list_item,
        previous
    ) == 0x08U,
    "G2 FreeRTOS ListItem_t previous offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_list_item,
        owner
    ) == 0x0CU,
    "G2 FreeRTOS ListItem_t owner offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_list_item,
        container
    ) == 0x10U,
    "G2 FreeRTOS ListItem_t container offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_unordered_list, index) ==
        0x04U,
    "G2 FreeRTOS List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_unordered_list, end) ==
        0x08U,
    "G2 FreeRTOS List_t end offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_tcb,
        state_list_item
    ) == OPEN_CFW_FREERTOS_UNORDERED_TCB_STATE_ITEM_OFFSET,
    "G2 FreeRTOS TCB state-item offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_unordered_tcb,
        event_list_item
    ) == OPEN_CFW_FREERTOS_UNORDERED_TCB_EVENT_ITEM_OFFSET,
    "G2 FreeRTOS TCB event-item offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_unordered_tcb, priority) ==
        OPEN_CFW_FREERTOS_UNORDERED_TCB_PRIORITY_OFFSET,
    "G2 FreeRTOS TCB priority offset changed"
);
#endif

typedef open_cfw_freertos_unordered_ubase_type
(*open_cfw_freertos_unordered_assert_mask_fn)(void);
typedef void (*open_cfw_freertos_unordered_reset_fn)(void);

#ifndef OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK
#define OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK() \
    (((open_cfw_freertos_unordered_assert_mask_fn) \
        (open_cfw_freertos_unordered_uintptr) \
        (OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_ASSERT
#define OPEN_CFW_FREERTOS_UNORDERED_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)OPEN_CFW_FREERTOS_UNORDERED_ASSERT_MASK(); \
            *(volatile open_cfw_freertos_unordered_ubase_type *) \
                (open_cfw_freertos_unordered_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_RESET_NEXT_UNBLOCK
#define OPEN_CFW_FREERTOS_UNORDERED_RESET_NEXT_UNBLOCK() \
    (((open_cfw_freertos_unordered_reset_fn) \
        (open_cfw_freertos_unordered_uintptr) \
        (OPEN_CFW_FREERTOS_UNORDERED_RESET_UNBLOCK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_LOAD() \
    (*(volatile open_cfw_freertos_unordered_ubase_type *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_unordered_tcb * volatile *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_LOAD
#define OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_LOAD() \
    (*(volatile open_cfw_freertos_unordered_ubase_type *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_STORE
#define OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_STORE(value) \
    (*(volatile open_cfw_freertos_unordered_ubase_type *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_STORE(value) \
    (*(volatile open_cfw_freertos_unordered_base_type *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_READY_LIST
#define OPEN_CFW_FREERTOS_UNORDERED_READY_LIST(priority) \
    (&((struct open_cfw_freertos_unordered_list *) \
        (open_cfw_freertos_unordered_uintptr) \
        OPEN_CFW_FREERTOS_UNORDERED_READY_LISTS_ADDRESS)[(priority)])
#endif

#ifndef OPEN_CFW_FREERTOS_UNORDERED_TRACE_MOVED_TO_READY
#define OPEN_CFW_FREERTOS_UNORDERED_TRACE_MOVED_TO_READY(task) \
    do { \
        (void)(task); \
    } while (0)
#endif

void open_cfw_freertos_task_remove_from_unordered_event_list(
    struct open_cfw_freertos_unordered_list_item *event_list_item,
    open_cfw_freertos_unordered_tick_type item_value
);

#endif
