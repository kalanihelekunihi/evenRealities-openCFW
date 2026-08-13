/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 * Bounded vTaskPrioritySet() adaptation from commit
 * def7d2df2b0506d3d249334974f51e427c17a41c; stock G2 body
 * [0x00454C12,0x00454CEC).
 */

#include "runtime_freertos_task_priority_set.h"

extern void open_cfw_freertos_port_enter_critical(void);
extern void open_cfw_freertos_port_exit_critical(void);
extern void open_cfw_freertos_port_yield(void);
extern open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
);

static __attribute__((always_inline)) inline void
open_cfw_freertos_priority_set_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
)
{
    struct open_cfw_freertos_queue_next_list_item *index = list->index;
    item->next = index; item->previous = index->previous;
    index->previous->next = item; index->previous = item;
    item->container = list; ++list->item_count;
}

__attribute__((used, noinline))
void open_cfw_freertos_task_priority_set(
    struct open_cfw_freertos_priority_set_tcb *task,
    open_cfw_freertos_queue_next_ubase_type new_priority
)
{
    struct open_cfw_freertos_priority_set_tcb *current;
    open_cfw_freertos_queue_next_ubase_type current_base, old_priority;
    open_cfw_freertos_queue_next_base_type yield_required = 0;

    OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
        new_priority < OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES
    );
    if (new_priority >= OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES) {
        new_priority = OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES - 1U;
    }
    open_cfw_freertos_port_enter_critical();
    current = OPEN_CFW_FREERTOS_PRIORITY_SET_CURRENT_TCB_LOAD();
    if (task == 0) task = current;
    current_base = task->base_priority;
    if (current_base != new_priority) {
        if (new_priority > current_base) {
            if ((task != current) && (new_priority >= current->priority)) {
                yield_required = 1;
            }
        } else if (task == current) {
            yield_required = 1;
        }
        old_priority = task->priority;
        if (task->base_priority == task->priority) task->priority = new_priority;
        task->base_priority = new_priority;
        if ((task->event_list_item.item_value & OPEN_CFW_FREERTOS_PRIORITY_SET_EVENT_VALUE_IN_USE) == 0U) {
            task->event_list_item.item_value = OPEN_CFW_FREERTOS_QUEUE_NEXT_MAX_PRIORITIES - new_priority;
        }
        if (task->state_list_item.container == OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST(old_priority)) {
            (void)open_cfw_freertos_list_remove(&task->state_list_item);
            if (task->priority > OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_LOAD()) {
                OPEN_CFW_FREERTOS_PRIORITY_SET_TOP_READY_STORE(task->priority);
            }
            open_cfw_freertos_priority_set_insert_end(
                OPEN_CFW_FREERTOS_PRIORITY_SET_READY_LIST(task->priority),
                &task->state_list_item
            );
        }
        if (yield_required != 0) open_cfw_freertos_port_yield();
    }
    open_cfw_freertos_port_exit_critical();
}
