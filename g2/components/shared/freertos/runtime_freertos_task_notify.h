/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_NOTIFY_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_NOTIFY_H

#include "runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_FREERTOS_NOTIFY_NOT_WAITING = 0U,
    OPEN_CFW_FREERTOS_NOTIFY_WAITING = 1U,
    OPEN_CFW_FREERTOS_NOTIFY_RECEIVED = 2U,
    OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_ADDRESS = 0x20074A34U
};

enum open_cfw_freertos_notify_action {
    OPEN_CFW_FREERTOS_NOTIFY_NO_ACTION = 0,
    OPEN_CFW_FREERTOS_NOTIFY_SET_BITS = 1,
    OPEN_CFW_FREERTOS_NOTIFY_INCREMENT = 2,
    OPEN_CFW_FREERTOS_NOTIFY_SET_VALUE_OVERWRITE = 3,
    OPEN_CFW_FREERTOS_NOTIFY_SET_VALUE_NO_OVERWRITE = 4
};

struct open_cfw_freertos_notify_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_queue_next_list_item state_list_item;
    struct open_cfw_freertos_queue_next_list_item event_list_item;
    open_cfw_freertos_queue_next_ubase_type priority;
    unsigned char before_notification[0x38U];
    open_cfw_freertos_queue_next_ubase_type notification_value;
    unsigned char notification_state;
    unsigned char statically_allocated;
    unsigned char tail[2];
};

#if defined(__arm__)
_Static_assert(sizeof(struct open_cfw_freertos_notify_tcb) == 0x70U,
               "G2 FreeRTOS TCB size changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_notify_tcb,
                                  state_list_item) == 0x04U,
               "G2 TCB state-list offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_notify_tcb,
                                  event_list_item) == 0x18U,
               "G2 TCB event-list offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_notify_tcb,
                                  priority) == 0x2CU,
               "G2 TCB priority offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_notify_tcb,
                                  notification_value) == 0x68U,
               "G2 TCB notification-value offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_notify_tcb,
                                  notification_state) == 0x6CU,
               "G2 TCB notification-state offset changed");
#endif

#ifndef OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_notify_tcb * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_READY_LIST
#define OPEN_CFW_FREERTOS_NOTIFY_READY_LIST(priority) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST(priority)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_LOAD
#define OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_LOAD() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD()
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_STORE
#define OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_STORE(value) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE(value)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_NOTIFY_SCHEDULER_SUSPENDED_LOAD() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD()
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_PENDING_READY_LIST
#define OPEN_CFW_FREERTOS_NOTIFY_PENDING_READY_LIST() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST()
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_NOTIFY_YIELD_PENDING_STORE(value) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE(value)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_LOAD
#define OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_tick_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_ADDRESS)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_SET_MASK
#define OPEN_CFW_FREERTOS_NOTIFY_SET_MASK() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK()
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_CLEAR_MASK
#define OPEN_CFW_FREERTOS_NOTIFY_CLEAR_MASK(mask) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(mask)
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_VALIDATE_INTERRUPT_PRIORITY
#define OPEN_CFW_FREERTOS_NOTIFY_VALIDATE_INTERRUPT_PRIORITY() \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY()
#endif
#ifndef OPEN_CFW_FREERTOS_NOTIFY_ASSERT
#define OPEN_CFW_FREERTOS_NOTIFY_ASSERT(condition) \
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition)
#endif

open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify_wait(
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type clear_on_entry,
    open_cfw_freertos_queue_next_ubase_type clear_on_exit,
    open_cfw_freertos_queue_next_ubase_type *notification_value,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
);
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type value,
    open_cfw_freertos_queue_next_base_type action,
    open_cfw_freertos_queue_next_ubase_type *previous_value
);
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify_from_isr(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type value,
    open_cfw_freertos_queue_next_base_type action,
    open_cfw_freertos_queue_next_ubase_type *previous_value,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken
);

#endif
