/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_DELETE_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_DELETE_H

#include "runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_ADDRESS = 0x20074A24U,
    OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_ADDRESS = 0x20074A28U,
    OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT_ADDRESS = 0x20074A2CU,
    OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT_ADDRESS = 0x20074A30U,
    OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST_ADDRESS = 0x20073D38U,
    OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_ADDRESS = 0x20074A3CU,
    OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER_ADDRESS = 0x20074A4CU,
    OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST_ADDRESS = 0x20073D4CU,
    OPEN_CFW_FREERTOS_TASK_DELETE_NOTIFY_WAITING = 1U,
    OPEN_CFW_FREERTOS_TASK_DELETE_DYNAMIC_STACK_AND_TCB = 0U,
    OPEN_CFW_FREERTOS_TASK_DELETE_STATIC_STACK_ONLY = 1U,
    OPEN_CFW_FREERTOS_TASK_DELETE_STATIC_STACK_AND_TCB = 2U
};

enum open_cfw_freertos_task_state {
    OPEN_CFW_FREERTOS_TASK_RUNNING = 0,
    OPEN_CFW_FREERTOS_TASK_READY = 1,
    OPEN_CFW_FREERTOS_TASK_BLOCKED = 2,
    OPEN_CFW_FREERTOS_TASK_SUSPENDED = 3,
    OPEN_CFW_FREERTOS_TASK_DELETED = 4,
    OPEN_CFW_FREERTOS_TASK_INVALID = 5
};

struct open_cfw_freertos_task_delete_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_queue_next_list_item state_list_item;
    struct open_cfw_freertos_queue_next_list_item event_list_item;
    open_cfw_freertos_queue_next_ubase_type priority;
    void *stack;
    unsigned char before_notify_state[0x38U];
    unsigned char notify_state;
    unsigned char statically_allocated;
    unsigned char tail[2];
};

#if defined(__arm__)
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, state_list_item) == 0x04U, "G2 TCB state-list offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, event_list_item) == 0x18U, "G2 TCB event-list offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, priority) == 0x2CU, "G2 TCB priority offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, stack) == 0x30U, "G2 TCB stack offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, notify_state) == 0x6CU, "G2 TCB notify-state offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_delete_tcb, statically_allocated) == 0x6DU, "G2 TCB allocation-status offset changed");
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_task_delete_tcb * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_LOAD
#define OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_LOAD() \
    (*(struct open_cfw_freertos_queue_next_list * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_LOAD
#define OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_LOAD() \
    (*(struct open_cfw_freertos_queue_next_list * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST
#define OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST() \
    ((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST
#define OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST() \
    ((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT
#define OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT() \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT
#define OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT() \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER
#define OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER() \
    (*(volatile open_cfw_freertos_queue_next_ubase_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_LOAD
#define OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_base_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_SUSPENDED_LOAD() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD()
#endif
#ifndef OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT
#define OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT(condition) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition)
#endif

enum open_cfw_freertos_task_state open_cfw_freertos_task_get_state(
    const struct open_cfw_freertos_task_delete_tcb *task
);
void open_cfw_freertos_task_delete_tcb(
    struct open_cfw_freertos_task_delete_tcb *task
);
void open_cfw_freertos_task_delete(
    struct open_cfw_freertos_task_delete_tcb *task
);

#endif
