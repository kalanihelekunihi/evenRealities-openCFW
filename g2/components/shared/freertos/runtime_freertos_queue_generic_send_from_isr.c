/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of xQueueGenericSendFromISR() at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The official G2 body is
 * [0x00441952,0x00441A42).
 */

#include "runtime_freertos_queue_next_closure.h"

enum {
    OPEN_CFW_FREERTOS_QUEUE_SEND_ISR_OVERWRITE = 2
};

extern open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_copy_data_to_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    const void *item,
    open_cfw_freertos_queue_next_base_type position
);

__attribute__((used, noinline))
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_queue_generic_send_from_isr(
    struct open_cfw_freertos_queue_next_control *queue,
    const void *item,
    open_cfw_freertos_queue_next_base_type *higher_priority_task_woken,
    open_cfw_freertos_queue_next_base_type position
)
{
    open_cfw_freertos_queue_next_ubase_type saved_interrupt_status;
    open_cfw_freertos_queue_next_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((item == 0) && (queue->item_size != 0U))
    );
    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        !((position == OPEN_CFW_FREERTOS_QUEUE_SEND_ISR_OVERWRITE) &&
          (queue->length != 1U))
    );
    OPEN_CFW_FREERTOS_QUEUE_NEXT_VALIDATE_INTERRUPT_PRIORITY();

    saved_interrupt_status = OPEN_CFW_FREERTOS_QUEUE_NEXT_SET_MASK();
    if (
        (queue->messages_waiting < queue->length) ||
        (position == OPEN_CFW_FREERTOS_QUEUE_SEND_ISR_OVERWRITE)
    ) {
        const open_cfw_freertos_queue_next_int8 transmit_lock =
            queue->transmit_lock;

        OPEN_CFW_FREERTOS_QUEUE_NEXT_TRACE_SEND_FROM_ISR(queue);
        (void)open_cfw_freertos_queue_copy_data_to_queue(
            queue, item, position
        );

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
                    (open_cfw_freertos_queue_next_int8)(transmit_lock + 1);
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
