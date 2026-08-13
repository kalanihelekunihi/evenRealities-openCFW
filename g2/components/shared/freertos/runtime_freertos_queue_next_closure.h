/*
 * SPDX-License-Identifier: MIT
 *
 * Isolated FreeRTOS queue/task ABI for the next Even Realities G2 source
 * closure.  Every fixed provider and RAM object is named through an
 * overridable macro so hosted tests can inject state without changing the
 * target ABI.  This header is not registered by a production overlay.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_QUEUE_NEXT_CLOSURE_H
#define OPEN_CFW_RUNTIME_FREERTOS_QUEUE_NEXT_CLOSURE_H

typedef __INT32_TYPE__ open_cfw_freertos_queue_next_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_queue_next_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_queue_next_tick_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_queue_next_uintptr;
typedef __UINT8_TYPE__ open_cfw_freertos_queue_next_uint8;
typedef __INT8_TYPE__ open_cfw_freertos_queue_next_int8;

enum {
    OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE = 0,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE = 1,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_PASS = 1,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL = 0,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED = -1,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_INT8_MAX = 127,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK_ADDRESS = 0x005FA0A4U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK_ADDRESS = 0x005FA0BAU,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_ADDRESS = 0x00454F10U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK_ADDRESS = 0x00455876U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TASK_COUNT_ADDRESS = 0x20074A30U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_ADDRESS = 0x20074A44U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_ADDRESS = 0x20074A58U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST_ADDRESS = 0x20073D24U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_MINI_LIST_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_QUEUE_SIZE = 0x50U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_STATE_ITEM_OFFSET = 0x04U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_EVENT_ITEM_OFFSET = 0x18U,
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_PRIORITY_OFFSET = 0x2CU
};

struct open_cfw_freertos_queue_next_list;

struct open_cfw_freertos_queue_next_list_item {
    open_cfw_freertos_queue_next_tick_type item_value;
    struct open_cfw_freertos_queue_next_list_item *next;
    struct open_cfw_freertos_queue_next_list_item *previous;
    void *owner;
    struct open_cfw_freertos_queue_next_list *container;
};

struct open_cfw_freertos_queue_next_mini_list_item {
    open_cfw_freertos_queue_next_tick_type item_value;
    struct open_cfw_freertos_queue_next_list_item *next;
    struct open_cfw_freertos_queue_next_list_item *previous;
};

struct open_cfw_freertos_queue_next_list {
    volatile open_cfw_freertos_queue_next_ubase_type item_count;
    struct open_cfw_freertos_queue_next_list_item *index;
    struct open_cfw_freertos_queue_next_mini_list_item end;
};

struct open_cfw_freertos_queue_next_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_queue_next_list_item state_list_item;
    struct open_cfw_freertos_queue_next_list_item event_list_item;
    open_cfw_freertos_queue_next_ubase_type priority;
};

struct open_cfw_freertos_queue_next_control {
    open_cfw_freertos_queue_next_int8 *head;
    open_cfw_freertos_queue_next_int8 *write_to;
    union {
        struct {
            open_cfw_freertos_queue_next_int8 *tail;
            open_cfw_freertos_queue_next_int8 *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_freertos_queue_next_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_freertos_queue_next_list tasks_waiting_to_send;
    struct open_cfw_freertos_queue_next_list tasks_waiting_to_receive;
    volatile open_cfw_freertos_queue_next_ubase_type messages_waiting;
    open_cfw_freertos_queue_next_ubase_type length;
    open_cfw_freertos_queue_next_ubase_type item_size;
    volatile open_cfw_freertos_queue_next_int8 receive_lock;
    volatile open_cfw_freertos_queue_next_int8 transmit_lock;
    open_cfw_freertos_queue_next_uint8 statically_allocated;
    open_cfw_freertos_queue_next_uint8 allocation_padding;
    open_cfw_freertos_queue_next_ubase_type queue_number;
    open_cfw_freertos_queue_next_uint8 queue_type;
    open_cfw_freertos_queue_next_uint8 trace_padding[3];
};

_Static_assert(
    sizeof(open_cfw_freertos_queue_next_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_next_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_next_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_next_int8) == 1U,
    "G2 FreeRTOS queue lock width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_next_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_next_mini_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_MINI_LIST_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_next_list) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_next_control) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_QUEUE_SIZE,
    "G2 FreeRTOS Queue_t size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_next_list_item,
        next
    ) == 0x04U,
    "G2 FreeRTOS ListItem_t next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_next_list_item,
        previous
    ) == 0x08U,
    "G2 FreeRTOS ListItem_t previous offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_next_list_item,
        owner
    ) == 0x0CU,
    "G2 FreeRTOS ListItem_t owner offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_next_list_item,
        container
    ) == 0x10U,
    "G2 FreeRTOS ListItem_t container offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_list, index) ==
        0x04U,
    "G2 FreeRTOS List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_list, end) ==
        0x08U,
    "G2 FreeRTOS List_t end offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_tcb,
                       state_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_STATE_ITEM_OFFSET,
    "G2 FreeRTOS TCB state-item offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_tcb,
                       event_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_EVENT_ITEM_OFFSET,
    "G2 FreeRTOS TCB event-item offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_tcb, priority) ==
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TCB_PRIORITY_OFFSET,
    "G2 FreeRTOS TCB priority offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control, head) ==
        0x00U,
    "G2 FreeRTOS Queue_t head offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       value.semaphore.mutex_holder) == 0x08U,
    "G2 FreeRTOS Queue_t mutex-holder offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       tasks_waiting_to_receive) == 0x24U,
    "G2 FreeRTOS Queue_t receive-list offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       messages_waiting) == 0x38U,
    "G2 FreeRTOS Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control, length) ==
        0x3CU,
    "G2 FreeRTOS Queue_t length offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       item_size) == 0x40U,
    "G2 FreeRTOS Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       receive_lock) == 0x44U,
    "G2 FreeRTOS Queue_t receive-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       transmit_lock) == 0x45U,
    "G2 FreeRTOS Queue_t transmit-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       statically_allocated) == 0x46U,
    "G2 FreeRTOS Queue_t allocation offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       queue_number) == 0x48U,
    "G2 FreeRTOS Queue_t trace-number offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_next_control,
                       queue_type) == 0x4CU,
    "G2 FreeRTOS Queue_t trace-type offset changed"
);
#endif

typedef open_cfw_freertos_queue_next_ubase_type
(*open_cfw_freertos_queue_next_set_mask_fn)(void);
typedef void (*open_cfw_freertos_queue_next_clear_mask_fn)(
    open_cfw_freertos_queue_next_ubase_type
);
typedef open_cfw_freertos_queue_next_ubase_type
(*open_cfw_freertos_queue_next_task_count_fn)(void);
typedef void (*open_cfw_freertos_queue_next_reset_unblock_fn)(void);

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK() \
    (((open_cfw_freertos_queue_next_set_mask_fn) \
        (open_cfw_freertos_queue_next_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(mask) \
    (((open_cfw_freertos_queue_next_clear_mask_fn) \
        (open_cfw_freertos_queue_next_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK_ADDRESS | 1U))((mask)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD() \
    (((open_cfw_freertos_queue_next_task_count_fn) \
        (open_cfw_freertos_queue_next_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_queue_next_tcb * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE(value) \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE(value) \
    (*(volatile open_cfw_freertos_queue_next_base_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST() \
    ((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST(priority) \
    (&((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LISTS_ADDRESS)[(priority)])
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK() \
    (((open_cfw_freertos_queue_next_reset_unblock_fn) \
        (open_cfw_freertos_queue_next_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK(); \
            *(volatile open_cfw_freertos_queue_next_ubase_type *) \
                (open_cfw_freertos_queue_next_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY() \
    do { \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR(queue) \
    do { \
        (void)(queue); \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED(queue) \
    do { \
        (void)(queue); \
    } while (0)
#endif

open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_remove_from_event_list(
    const struct open_cfw_freertos_queue_next_list *event_list
);

open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_give_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken
);

#endif
