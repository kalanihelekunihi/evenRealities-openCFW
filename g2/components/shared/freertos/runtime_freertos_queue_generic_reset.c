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
 * Bounded, freestanding adaptation of xQueueGenericReset() from the
 * authenticated FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2 body is
 * [0x00441516,0x004415CA).  This module is production-registered by the
 * Apollo-main core overlay; hosted differential fixtures retain the
 * candidate/oracle terminology only to distinguish this implementation from
 * pristine upstream queue.c.
 */

#include "runtime_freertos_queue_generic_reset.h"

__attribute__((used, noinline))
open_cfw_freertos_queue_reset_base_type
open_cfw_freertos_queue_generic_reset(
    struct open_cfw_freertos_queue_reset_control *queue,
    open_cfw_freertos_queue_reset_base_type new_queue
)
{
    open_cfw_freertos_queue_reset_base_type result =
        OPEN_CFW_FREERTOS_QUEUE_RESET_PASS;

    OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT(queue != 0);

    if (
        queue != 0 &&
        queue->length >= 1U &&
        (OPEN_CFW_FREERTOS_QUEUE_RESET_SIZE_MAX / queue->length) >=
            queue->item_size
    ) {
        OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL();
        queue->value.queue.tail =
            queue->head + (queue->length * queue->item_size);
        queue->messages_waiting = 0U;
        queue->write_to = queue->head;
        queue->value.queue.read_from =
            queue->head + ((queue->length - 1U) * queue->item_size);
        queue->receive_lock =
            (open_cfw_freertos_queue_reset_int8)
            OPEN_CFW_FREERTOS_QUEUE_RESET_UNLOCKED;
        queue->transmit_lock =
            (open_cfw_freertos_queue_reset_int8)
            OPEN_CFW_FREERTOS_QUEUE_RESET_UNLOCKED;

        if (new_queue == OPEN_CFW_FREERTOS_QUEUE_RESET_FALSE) {
            if (queue->tasks_waiting_to_send.item_count != 0U) {
                if (
                    OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_FROM_EVENT_LIST(
                        &queue->tasks_waiting_to_send
                    ) != OPEN_CFW_FREERTOS_QUEUE_RESET_FALSE
                ) {
                    OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD();
                } else {
                    OPEN_CFW_FREERTOS_QUEUE_RESET_COVERAGE_MARKER();
                }
            } else {
                OPEN_CFW_FREERTOS_QUEUE_RESET_COVERAGE_MARKER();
            }
        } else {
            OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE(
                &queue->tasks_waiting_to_send
            );
            OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE(
                &queue->tasks_waiting_to_receive
            );
        }
        OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL();
    } else {
        result = OPEN_CFW_FREERTOS_QUEUE_RESET_FAIL;
    }

    OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT(
        result != OPEN_CFW_FREERTOS_QUEUE_RESET_FAIL
    );
    return result;
}
