/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Production isolated adaptation of xQueueSemaphoreTake() from the
 * authenticated FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 */

#include "runtime_freertos_queue_semaphore_take_upstream_candidate.h"

static void open_cfw_freertos_semaphore_take_lock_queue(
    struct open_cfw_semaphore_take_queue *queue
)
{
    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL();
    if (
        queue->receive_lock ==
        (signed char)OPEN_CFW_SEMAPHORE_TAKE_QUEUE_UNLOCKED
    ) {
        queue->receive_lock = 0;
    }
    if (
        queue->transmit_lock ==
        (signed char)OPEN_CFW_SEMAPHORE_TAKE_QUEUE_UNLOCKED
    ) {
        queue->transmit_lock = 0;
    }
    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();
}

__attribute__((used, noinline))
open_cfw_semaphore_take_base_type
open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    struct open_cfw_semaphore_take_queue *queue,
    open_cfw_semaphore_take_tick_type ticks_to_wait
)
{
    open_cfw_semaphore_take_base_type entry_time_set =
        OPEN_CFW_SEMAPHORE_TAKE_FALSE;
    struct open_cfw_semaphore_take_timeout timeout;
    open_cfw_semaphore_take_base_type inheritance_occurred =
        OPEN_CFW_SEMAPHORE_TAKE_FALSE;

    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT(queue->item_size == 0U);
    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT(
        !(
            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SCHEDULER_STATE() ==
                OPEN_CFW_SEMAPHORE_TAKE_SCHEDULER_SUSPENDED &&
            ticks_to_wait != 0U
        )
    );

    for (;;) {
        open_cfw_semaphore_take_ubase_type semaphore_count;

        OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL();
        semaphore_count = queue->messages_waiting;
        if (semaphore_count > 0U) {
            queue->messages_waiting = semaphore_count - 1U;

            /* queue.c aliases uxQueueType to pcHead; NULL marks a mutex. */
            if (queue->head == 0) {
                queue->value.semaphore.mutex_holder =
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_INCREMENT_MUTEX_HELD();
            }

            if (queue->tasks_waiting_to_send.item_count != 0U) {
                if (
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_REMOVE_EVENT(
                        &queue->tasks_waiting_to_send
                    ) != OPEN_CFW_SEMAPHORE_TAKE_FALSE
                ) {
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_YIELD();
                }
            }

            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();
            return OPEN_CFW_SEMAPHORE_TAKE_PASS;
        }

        if (ticks_to_wait == 0U) {
            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();
            return OPEN_CFW_SEMAPHORE_TAKE_EMPTY;
        }

        if (entry_time_set == OPEN_CFW_SEMAPHORE_TAKE_FALSE) {
            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SET_TIMEOUT(&timeout);
            entry_time_set = OPEN_CFW_SEMAPHORE_TAKE_TRUE;
        }
        OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();

        OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SUSPEND_ALL();
        open_cfw_freertos_semaphore_take_lock_queue(queue);

        if (
            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_CHECK_TIMEOUT(
                &timeout,
                &ticks_to_wait
            ) == OPEN_CFW_SEMAPHORE_TAKE_FALSE
        ) {
            if (
                OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_IS_EMPTY(queue) !=
                OPEN_CFW_SEMAPHORE_TAKE_FALSE
            ) {
                if (queue->head == 0) {
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL();
                    inheritance_occurred =
                        OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PRIORITY_INHERIT(
                            queue->value.semaphore.mutex_holder
                        );
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();
                }

                OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PLACE_ON_EVENT(
                    &queue->tasks_waiting_to_receive,
                    ticks_to_wait
                );
                OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK(queue);
                if (
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL() ==
                    OPEN_CFW_SEMAPHORE_TAKE_FALSE
                ) {
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_YIELD();
                }
            } else {
                OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK(queue);
                (void)OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL();
            }
        } else {
            OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK(queue);
            (void)OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL();

            if (
                OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_IS_EMPTY(queue) !=
                OPEN_CFW_SEMAPHORE_TAKE_FALSE
            ) {
                if (
                    inheritance_occurred !=
                    OPEN_CFW_SEMAPHORE_TAKE_FALSE
                ) {
                    open_cfw_semaphore_take_ubase_type
                        highest_waiting_priority;

                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL();
                    highest_waiting_priority =
                        OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_PRIORITY(
                            queue
                        );
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_AFTER_TIMEOUT(
                        queue->value.semaphore.mutex_holder,
                        highest_waiting_priority
                    );
                    OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL();
                }
                return OPEN_CFW_SEMAPHORE_TAKE_EMPTY;
            }
        }
    }
}
