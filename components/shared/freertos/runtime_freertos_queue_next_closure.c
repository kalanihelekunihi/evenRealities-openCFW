/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Bounded, freestanding adaptations of xQueueGiveFromISR() and
 * xTaskRemoveFromEventList() from authenticated FreeRTOS-Kernel V10.5.1
 * commit def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2
 * bodies are [0x00441A42,0x00441B0A) and [0x00455370,0x00455466).
 *
 * This candidate is intentionally not registered by a production overlay.
 */

#include "runtime_freertos_queue_next_closure.h"

static __attribute__((always_inline)) inline void
open_cfw_freertos_queue_next_list_remove_inline(
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    struct open_cfw_freertos_queue_next_list *list = item->container;

    item->next->previous = item->previous;
    item->previous->next = item->next;
    if (list->index == item) {
        list->index = item->previous;
    }
    item->container = (struct open_cfw_freertos_queue_next_list *)0;
    --list->item_count;
}

static __attribute__((always_inline)) inline void
open_cfw_freertos_queue_next_list_insert_end_inline(
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
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_remove_from_event_list(
    const struct open_cfw_freertos_queue_next_list *event_list
)
{
    struct open_cfw_freertos_queue_next_tcb *unblocked_tcb;

    unblocked_tcb = (struct open_cfw_freertos_queue_next_tcb *)
        event_list->end.next->owner;
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(unblocked_tcb != 0);
    open_cfw_freertos_queue_next_list_remove_inline(
        &unblocked_tcb->event_list_item
    );

    if (
        OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD() ==
        (open_cfw_freertos_queue_next_ubase_type)
        OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
    ) {
        struct open_cfw_freertos_queue_next_list *ready_list;

        open_cfw_freertos_queue_next_list_remove_inline(
            &unblocked_tcb->state_list_item
        );

        if (
            unblocked_tcb->priority >
            OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_LOAD()
        ) {
            OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_STORE(
                unblocked_tcb->priority
            );
        }
        ready_list = OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LIST(
            unblocked_tcb->priority
        );
        open_cfw_freertos_queue_next_list_insert_end_inline(
            ready_list,
            &unblocked_tcb->state_list_item
        );
        OPEN_CFW_FREERTOS_QUEUE_NEXT_RESET_UNBLOCK();
    } else {
        open_cfw_freertos_queue_next_list_insert_end_inline(
            OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST(),
            &unblocked_tcb->event_list_item
        );
    }

    if (
        unblocked_tcb->priority >
        OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_LOAD()->priority
    ) {
        OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_STORE(
            OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE
        );
        return OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE;
    }

    return OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE;
}

__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_give_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken
)
{
    open_cfw_freertos_queue_next_ubase_type saved_interrupt_status;
    open_cfw_freertos_queue_next_ubase_type messages_waiting;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(queue->item_size == 0U);
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((queue->head == 0) &&
          (queue->value.semaphore.mutex_holder != 0))
    );
    OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY();

    saved_interrupt_status = OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK();
    messages_waiting = queue->messages_waiting;

    if (messages_waiting < queue->length) {
        const open_cfw_freertos_queue_next_int8 transmit_lock =
            queue->transmit_lock;

        OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR(queue);
        queue->messages_waiting = messages_waiting + 1U;

        if (
            transmit_lock ==
            (open_cfw_freertos_queue_next_int8)
            OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED
        ) {
            if (queue->tasks_waiting_to_receive.item_count != 0U) {
                if (
                    open_cfw_freertos_task_remove_from_event_list(
                        &queue->tasks_waiting_to_receive
                    ) != OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
                ) {
                    if (higher_priority_task_woken != 0) {
                        *higher_priority_task_woken =
                            OPEN_CFW_FREERTOS_QUEUE_NEXT_TRUE;
                    }
                }
            }
        } else {
            const open_cfw_freertos_queue_next_ubase_type task_count =
                OPEN_CFW_FREERTOS_QUEUE_NEXT_TASK_COUNT_LOAD();

            if (
                (open_cfw_freertos_queue_next_ubase_type)transmit_lock <
                task_count
            ) {
                OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
                    transmit_lock !=
                    (open_cfw_freertos_queue_next_int8)
                    OPEN_CFW_FREERTOS_QUEUE_NEXT_INT8_MAX
                );
                queue->transmit_lock =
                    (open_cfw_freertos_queue_next_int8)
                    (transmit_lock + 1);
            }
        }
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_PASS;
    } else {
        OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR_FAILED(queue);
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL;
    }

    OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(saved_interrupt_status);
    return result;
}
