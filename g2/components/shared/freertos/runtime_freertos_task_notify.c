/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 * Bounded xTaskGenericNotifyWait(), xTaskGenericNotify(), and
 * xTaskGenericNotifyFromISR() adaptations from commit
 * def7d2df2b0506d3d249334974f51e427c17a41c; stock G2 physical bodies
 * [0x00455B84,0x00455C48), [0x00455C48,0x00455DB8), and
 * [0x00455DC0,0x00455F5C).
 */

#include "runtime_freertos_task_notify.h"

extern void open_cfw_freertos_port_enter_critical(void);
extern void open_cfw_freertos_port_exit_critical(void);
extern void open_cfw_freertos_port_yield(void);
extern open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
);
extern void open_cfw_freertos_list_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
);
extern void open_cfw_freertos_task_reset_next_task_unblock_time(void);
extern void open_cfw_freertos_task_add_current_to_delayed_list(
    open_cfw_freertos_queue_next_tick_type ticks_to_wait,
    open_cfw_freertos_queue_next_base_type can_block_indefinitely
);

#if !defined(OPEN_CFW_BUILD_TASK_NOTIFY_WAIT) && \
    !defined(OPEN_CFW_BUILD_TASK_NOTIFY) && \
    !defined(OPEN_CFW_BUILD_TASK_NOTIFY_FROM_ISR)
#define OPEN_CFW_BUILD_TASK_NOTIFY_ALL 1
#endif

#if !defined(OPEN_CFW_BUILD_TASK_NOTIFY_WAIT)
static __attribute__((always_inline)) inline void
open_cfw_freertos_notify_add_to_ready(
    struct open_cfw_freertos_notify_tcb *task
)
{
    if (task->priority > OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_LOAD()) {
        OPEN_CFW_FREERTOS_NOTIFY_TOP_READY_STORE(task->priority);
    }
    open_cfw_freertos_list_insert_end(
        OPEN_CFW_FREERTOS_NOTIFY_READY_LIST(task->priority),
        &task->state_list_item
    );
}

static __attribute__((always_inline)) inline
open_cfw_freertos_queue_next_base_type open_cfw_freertos_notify_apply(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_freertos_queue_next_ubase_type value,
    open_cfw_freertos_queue_next_base_type action,
    unsigned char original_state
)
{
    open_cfw_freertos_queue_next_base_type result =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_PASS;

    switch (action) {
    case OPEN_CFW_FREERTOS_NOTIFY_SET_BITS:
        task->notification_value |= value;
        break;
    case OPEN_CFW_FREERTOS_NOTIFY_INCREMENT:
        ++task->notification_value;
        break;
    case OPEN_CFW_FREERTOS_NOTIFY_SET_VALUE_OVERWRITE:
        task->notification_value = value;
        break;
    case OPEN_CFW_FREERTOS_NOTIFY_SET_VALUE_NO_OVERWRITE:
        if (original_state != OPEN_CFW_FREERTOS_NOTIFY_RECEIVED) {
            task->notification_value = value;
        } else {
            result = OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL;
        }
        break;
    case OPEN_CFW_FREERTOS_NOTIFY_NO_ACTION:
        break;
    default:
        OPEN_CFW_FREERTOS_NOTIFY_ASSERT(
            OPEN_CFW_FREERTOS_NOTIFY_TICK_COUNT_LOAD() == 0U
        );
        break;
    }
    return result;
}
#endif

#if defined(OPEN_CFW_BUILD_TASK_NOTIFY_ALL) || \
    defined(OPEN_CFW_BUILD_TASK_NOTIFY_WAIT)
__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify_wait(
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type clear_on_entry,
    open_cfw_freertos_queue_next_ubase_type clear_on_exit,
    open_cfw_freertos_queue_next_ubase_type *notification_value,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
)
{
    struct open_cfw_freertos_notify_tcb *current;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_NOTIFY_ASSERT(index < 1U);
    current = OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD();
    open_cfw_freertos_port_enter_critical();
    if (current->notification_state != OPEN_CFW_FREERTOS_NOTIFY_RECEIVED) {
        current->notification_value &= ~clear_on_entry;
        current->notification_state = OPEN_CFW_FREERTOS_NOTIFY_WAITING;
        if (ticks_to_wait > 0U) {
            open_cfw_freertos_task_add_current_to_delayed_list(
                ticks_to_wait, OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE
            );
            open_cfw_freertos_port_yield();
        }
    }
    open_cfw_freertos_port_exit_critical();

    open_cfw_freertos_port_enter_critical();
    if (notification_value != 0) {
        *notification_value = current->notification_value;
    }
    if (current->notification_state != OPEN_CFW_FREERTOS_NOTIFY_RECEIVED) {
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE;
    } else {
        current->notification_value &= ~clear_on_exit;
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE;
    }
    current->notification_state = OPEN_CFW_FREERTOS_NOTIFY_NOT_WAITING;
    open_cfw_freertos_port_exit_critical();
    return result;
}
#endif

#if defined(OPEN_CFW_BUILD_TASK_NOTIFY_ALL) || defined(OPEN_CFW_BUILD_TASK_NOTIFY)
__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type value,
    open_cfw_freertos_queue_next_base_type action,
    open_cfw_freertos_queue_next_ubase_type *previous_value
)
{
    struct open_cfw_freertos_notify_tcb *current;
    unsigned char original_state;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_NOTIFY_ASSERT(index < 1U);
    OPEN_CFW_FREERTOS_NOTIFY_ASSERT(task != 0);
    current = OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD();
    open_cfw_freertos_port_enter_critical();
    if (previous_value != 0) *previous_value = task->notification_value;
    original_state = task->notification_state;
    task->notification_state = OPEN_CFW_FREERTOS_NOTIFY_RECEIVED;
    result = open_cfw_freertos_notify_apply(task, value, action, original_state);
    if (original_state == OPEN_CFW_FREERTOS_NOTIFY_WAITING) {
        (void)open_cfw_freertos_list_remove(&task->state_list_item);
        open_cfw_freertos_notify_add_to_ready(task);
        OPEN_CFW_FREERTOS_NOTIFY_ASSERT(task->event_list_item.container == 0);
        open_cfw_freertos_task_reset_next_task_unblock_time();
        if (task->priority > current->priority) {
            open_cfw_freertos_port_yield();
        }
    }
    open_cfw_freertos_port_exit_critical();
    return result;
}
#endif

#if defined(OPEN_CFW_BUILD_TASK_NOTIFY_ALL) || \
    defined(OPEN_CFW_BUILD_TASK_NOTIFY_FROM_ISR)
__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_notify_from_isr(
    struct open_cfw_freertos_notify_tcb *task,
    open_cfw_freertos_queue_next_ubase_type index,
    open_cfw_freertos_queue_next_ubase_type value,
    open_cfw_freertos_queue_next_base_type action,
    open_cfw_freertos_queue_next_ubase_type *previous_value,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken
)
{
    struct open_cfw_freertos_notify_tcb *current;
    open_cfw_freertos_queue_next_ubase_type saved_mask;
    unsigned char original_state;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_NOTIFY_ASSERT(task != 0);
    OPEN_CFW_FREERTOS_NOTIFY_ASSERT(index < 1U);
    OPEN_CFW_FREERTOS_NOTIFY_VALIDATE_INTERRUPT_PRIORITY();
    current = OPEN_CFW_FREERTOS_NOTIFY_CURRENT_TCB_LOAD();
    saved_mask = OPEN_CFW_FREERTOS_NOTIFY_SET_MASK();
    if (previous_value != 0) *previous_value = task->notification_value;
    original_state = task->notification_state;
    task->notification_state = OPEN_CFW_FREERTOS_NOTIFY_RECEIVED;
    result = open_cfw_freertos_notify_apply(task, value, action, original_state);
    if (original_state == OPEN_CFW_FREERTOS_NOTIFY_WAITING) {
        OPEN_CFW_FREERTOS_NOTIFY_ASSERT(task->event_list_item.container == 0);
        if (OPEN_CFW_FREERTOS_NOTIFY_SCHEDULER_SUSPENDED_LOAD() == 0U) {
            (void)open_cfw_freertos_list_remove(&task->state_list_item);
            open_cfw_freertos_notify_add_to_ready(task);
        } else {
            open_cfw_freertos_list_insert_end(
                OPEN_CFW_FREERTOS_NOTIFY_PENDING_READY_LIST(),
                &task->event_list_item
            );
        }
        if (task->priority > current->priority) {
            if (higher_priority_task_woken != 0) {
                *higher_priority_task_woken = OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE;
            }
            OPEN_CFW_FREERTOS_NOTIFY_YIELD_PENDING_STORE(
                OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE
            );
        }
    }
    OPEN_CFW_FREERTOS_NOTIFY_CLEAR_MASK(saved_mask);
    return result;
}
#endif
