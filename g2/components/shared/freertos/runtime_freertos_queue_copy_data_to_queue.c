/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of private prvCopyDataToQueue() at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The official G2 body is
 * [0x00441ED8,0x00441F5E).
 */

#include "runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_FREERTOS_QUEUE_COPY_TO_BACK = 0,
    OPEN_CFW_FREERTOS_QUEUE_COPY_OVERWRITE = 2
};

extern void __aeabi_memcpy(void *destination, const void *source,
                           open_cfw_freertos_queue_next_ubase_type size);
extern open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_priority_disinherit(void *mutex_holder);

__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_copy_data_to_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    const void *item,
    open_cfw_freertos_queue_next_base_type position
)
{
    open_cfw_freertos_queue_next_base_type result =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE;
    open_cfw_freertos_queue_next_ubase_type messages_waiting =
        queue->messages_waiting;

    if (queue->item_size == 0U) {
        if (queue->head == 0) {
            result = open_cfw_freertos_task_priority_disinherit(
                queue->value.semaphore.mutex_holder
            );
            queue->value.semaphore.mutex_holder = 0;
        }
    } else if (position == OPEN_CFW_FREERTOS_QUEUE_COPY_TO_BACK) {
        __aeabi_memcpy(queue->write_to, item, queue->item_size);
        queue->write_to += queue->item_size;
        if (queue->write_to >= queue->value.queue.tail) {
            queue->write_to = queue->head;
        }
    } else {
        __aeabi_memcpy(
            queue->value.queue.read_from,
            item,
            queue->item_size
        );
        queue->value.queue.read_from -= queue->item_size;
        if (queue->value.queue.read_from < queue->head) {
            queue->value.queue.read_from =
                queue->value.queue.tail - queue->item_size;
        }
        if (
            (position == OPEN_CFW_FREERTOS_QUEUE_COPY_OVERWRITE) &&
            (messages_waiting > 0U)
        ) {
            messages_waiting -= 1U;
        }
    }
    queue->messages_waiting = messages_waiting + 1U;
    return result;
}
