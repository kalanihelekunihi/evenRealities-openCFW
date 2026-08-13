/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_PRIORITY_SET_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_PRIORITY_SET_H

#include "runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_FREERTOS_PRIORITY_SET_BASE_PRIORITY_OFFSET = 0x60U,
    OPEN_CFW_FREERTOS_PRIORITY_SET_EVENT_VALUE_IN_USE = 0x80000000U
};

struct open_cfw_freertos_priority_set_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_queue_next_list_item state_list_item;
    struct open_cfw_freertos_queue_next_list_item event_list_item;
    open_cfw_freertos_queue_next_ubase_type priority;
    unsigned char before_base_priority[0x30U];
    open_cfw_freertos_queue_next_ubase_type base_priority;
};

#if defined(__arm__)
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_priority_set_tcb, base_priority) == 0x60U, "G2 TCB base-priority offset changed");
#endif

#ifndef OPEN_CFW_FREERTOS_PRIORITY_SET_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_PRIORITY_SET_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_priority_set_tcb * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST
#define OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST(priority) \
    (&((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LISTS_ADDRESS)[(priority)])
#endif
#ifndef OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_LOAD
#define OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_LOAD() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD()
#endif
#ifndef OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_STORE
#define OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_STORE(value) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE(value)
#endif

void open_cfw_freertos_task_priority_set(
    struct open_cfw_freertos_priority_set_tcb *task,
    open_cfw_freertos_queue_next_ubase_type new_priority
);

#endif
