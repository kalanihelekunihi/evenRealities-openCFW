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
 * Bounded, freestanding adaptation of xQueueReceiveFromISR() from
 * authenticated FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2 body is
 * [0x00441DA6,0x00441E66).
 */

#include "runtime_freertos_queue_next_closure.h"

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE(queue) \
    do { \
        (void)(queue); \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue) \
    do { \
        (void)(queue); \
    } while (0)
#endif

extern void open_cfw_freertos_queue_copy_data_from_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer
);

__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_receive_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken
)
{
    open_cfw_freertos_queue_next_ubase_type saved_interrupt_status;
    open_cfw_freertos_queue_next_ubase_type messages_waiting;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((buffer == 0) && (queue->item_size != 0U))
    );
    OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY();

    saved_interrupt_status = OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK();
    messages_waiting = queue->messages_waiting;

    if (messages_waiting > 0U) {
        const open_cfw_freertos_queue_next_int8 receive_lock =
            queue->receive_lock;

        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE(queue);
        open_cfw_freertos_queue_copy_data_from_queue(queue, buffer);
        queue->messages_waiting = messages_waiting - 1U;

        if (
            receive_lock ==
            (open_cfw_freertos_queue_next_int8)
            OPEN_CFW_FREERTOS_QUEUE_NEXT_UNLOCKED
        ) {
            if (queue->tasks_waiting_to_send.item_count != 0U) {
                if (
                    open_cfw_freertos_task_remove_from_event_list(
                        &queue->tasks_waiting_to_send
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
                (open_cfw_freertos_queue_next_ubase_type)receive_lock <
                task_count
            ) {
                OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
                    receive_lock !=
                    (open_cfw_freertos_queue_next_int8)
                    OPEN_CFW_FREERTOS_QUEUE_NEXT_INT8_MAX
                );
                queue->receive_lock =
                    (open_cfw_freertos_queue_next_int8)(receive_lock + 1);
            }
        }
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_PASS;
    } else {
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue);
        result = OPEN_CFW_FREERTOS_QUEUE_NEXT_FAIL;
    }

    OPEN_CFW_FREERTOS_QUEUE_NEXT_CLEAR_MASK(saved_interrupt_status);
    return result;
}
