/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptations of xQueueReceive(), prvUnlockQueue(),
 * vTaskPlaceOnEventList(), and prvAddCurrentTaskToDelayedList() from commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The stock G2 bodies are
 * [0x00441B0A,0x00441C44), [0x00441F88,0x00441FF6),
 * [0x00455282,0x004552AE), and [0x00455FA8,0x0045601E).
 */

#include "runtime_freertos_queue_receive.h"

#if !defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_DELAYED) && \
    !defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_PLACE) && \
    !defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_UNLOCK) && \
    !defined(OPEN_CFW_BUILD_QUEUE_RECEIVE)
#define OPEN_CFW_BUILD_QUEUE_RECEIVE_ALL 1
#endif

#if defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_ALL) || \
    defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_DELAYED)
static __attribute__((always_inline)) inline void
open_cfw_freertos_queue_receive_list_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    struct open_cfw_freertos_queue_next_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

__attribute__((used, noinline))
void open_cfw_freertos_task_add_current_to_delayed_list(
    open_cfw_freertos_queue_next_tick_type ticks_to_wait,
    open_cfw_freertos_queue_next_base_type can_block_indefinitely
)
{
    struct open_cfw_freertos_queue_next_tcb *current =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD();
    const open_cfw_freertos_queue_next_tick_type tick_count =
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_LOAD();
    open_cfw_freertos_queue_next_tick_type time_to_wake;

    (void)open_cfw_freertos_list_remove(&current->state_list_item);

    if (
        ticks_to_wait == OPEN_CFW_FREERTOS_QUEUE_RECEIVE_PORT_MAX_DELAY &&
        can_block_indefinitely != OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
    ) {
        open_cfw_freertos_queue_receive_list_insert_end(
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST(),
            &current->state_list_item
        );
        return;
    }

    time_to_wake = tick_count + ticks_to_wait;
    current->state_list_item.item_value = time_to_wake;
    if (time_to_wake < tick_count) {
        open_cfw_freertos_list_insert(
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_LOAD(),
            &current->state_list_item
        );
    } else {
        open_cfw_freertos_list_insert(
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_LOAD(),
            &current->state_list_item
        );
        if (time_to_wake < OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_LOAD()) {
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_STORE(time_to_wake);
        }
    }
}
#endif

#if defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_ALL) || \
    defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_PLACE)
__attribute__((used, noinline))
void open_cfw_freertos_task_place_on_event_list(
    struct open_cfw_freertos_queue_next_list *event_list,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
)
{
    struct open_cfw_freertos_queue_next_tcb *current;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(event_list != 0);
    current = OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD();
    open_cfw_freertos_list_insert(event_list, &current->event_list_item);
    open_cfw_freertos_task_add_current_to_delayed_list(
        ticks_to_wait,
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE
    );
}
#endif

#if defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_ALL) || \
    defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_UNLOCK)
__attribute__((used, noinline))
void open_cfw_freertos_queue_unlock(
    struct open_cfw_freertos_queue_next_control *queue
)
{
    open_cfw_freertos_queue_next_int8 lock;

    open_cfw_freertos_port_enter_critical();
    lock = queue->transmit_lock;
    while (lock > 0) {
        if (queue->tasks_waiting_to_receive.item_count == 0U) {
            break;
        }
        if (
            open_cfw_freertos_task_remove_from_event_list(
                &queue->tasks_waiting_to_receive
            ) != OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
        ) {
            open_cfw_freertos_task_missed_yield();
        }
        --lock;
    }
    queue->transmit_lock = OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED;
    open_cfw_freertos_port_exit_critical();

    open_cfw_freertos_port_enter_critical();
    lock = queue->receive_lock;
    while (lock > 0) {
        if (queue->tasks_waiting_to_send.item_count == 0U) {
            break;
        }
        if (
            open_cfw_freertos_task_remove_from_event_list(
                &queue->tasks_waiting_to_send
            ) != OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
        ) {
            open_cfw_freertos_task_missed_yield();
        }
        --lock;
    }
    queue->receive_lock = OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED;
    open_cfw_freertos_port_exit_critical();
}
#endif

#if defined(OPEN_CFW_BUILD_QUEUE_RECEIVE_ALL) || \
    defined(OPEN_CFW_BUILD_QUEUE_RECEIVE)
__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type open_cfw_freertos_queue_receive(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
)
{
    struct open_cfw_freertos_queue_receive_timeout timeout;
    open_cfw_freertos_queue_next_base_type entry_time_set =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((buffer == 0) && (queue->item_size != 0U))
    );
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((open_cfw_freertos_task_get_scheduler_state() == 0) &&
          (ticks_to_wait != 0U))
    );

    for (;;) {
        open_cfw_freertos_port_enter_critical();
        if (queue->messages_waiting > 0U) {
            const open_cfw_freertos_queue_next_ubase_type waiting =
                queue->messages_waiting;
            open_cfw_freertos_queue_copy_data_from_queue(queue, buffer);
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE(queue);
            queue->messages_waiting = waiting - 1U;
            if (queue->tasks_waiting_to_send.item_count != 0U) {
                if (
                    open_cfw_freertos_task_remove_from_event_list(
                        &queue->tasks_waiting_to_send
                    ) != OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
                ) {
                    open_cfw_freertos_port_yield();
                }
            }
            open_cfw_freertos_port_exit_critical();
            return OPEN_CFW_FREERTOS_QUEUE_NEXT_PASS;
        }

        if (ticks_to_wait == 0U) {
            open_cfw_freertos_port_exit_critical();
            OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue);
            return OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL;
        }
        if (entry_time_set == OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE) {
            open_cfw_freertos_task_internal_set_timeout_state(&timeout);
            entry_time_set = OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE;
        }
        open_cfw_freertos_port_exit_critical();

        open_cfw_freertos_task_suspend_all();
        if (queue->receive_lock == OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED) {
            queue->receive_lock = 0;
        }
        if (queue->transmit_lock == OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED) {
            queue->transmit_lock = 0;
        }

        if (
            open_cfw_freertos_task_check_for_timeout(
                &timeout,
                &ticks_to_wait
            ) == OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
        ) {
            if (open_cfw_freertos_queue_is_empty(queue) != 0) {
                open_cfw_freertos_task_place_on_event_list(
                    &queue->tasks_waiting_to_receive,
                    ticks_to_wait
                );
                open_cfw_freertos_queue_unlock(queue);
                if (open_cfw_freertos_task_resume_all() == 0) {
                    open_cfw_freertos_port_yield();
                }
            } else {
                open_cfw_freertos_queue_unlock(queue);
                (void)open_cfw_freertos_task_resume_all();
            }
        } else {
            open_cfw_freertos_queue_unlock(queue);
            (void)open_cfw_freertos_task_resume_all();
            if (open_cfw_freertos_queue_is_empty(queue) != 0) {
                OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue);
                return OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL;
            }
        }
    }
}
#endif
