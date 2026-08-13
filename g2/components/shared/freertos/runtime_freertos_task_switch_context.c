/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Bounded, freestanding adaptation of vTaskSwitchContext() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The released G2 configuration uses generic ready-list selection, method-2
 * stack-overflow checking, and custom switched-out/switched-in trace hooks.
 * The official body is [0x004551B4, 0x00455282).
 */

#include "runtime_freertos_task_switch_context.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_switch_context(void)
{
    struct open_cfw_freertos_switch_tcb *tcb;
    struct open_cfw_freertos_switch_list *ready_list;
    struct open_cfw_freertos_switch_list_item *item;
    volatile open_cfw_freertos_switch_stack_type *stack;
    open_cfw_freertos_switch_ubase_type priority;

    if (OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_LOAD() != 0U) {
        OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_STORE(
            OPEN_CFW_FREERTOS_SWITCH_TRUE
        );
        return;
    }

    OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_STORE(
        OPEN_CFW_FREERTOS_SWITCH_FALSE
    );

    tcb = OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD();
    stack = tcb->stack_base;
    if (
        stack[0] != OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD ||
        stack[1] != OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD ||
        stack[2] != OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD ||
        stack[3] != OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD
    ) {
        tcb = OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD();
        OPEN_CFW_FREERTOS_SWITCH_STACK_OVERFLOW_HOOK(
            OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD(),
            tcb->task_name
        );
    }

    tcb = OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD();
    OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORD(
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD()
    )->switched_out = tcb->task_number;

    priority = OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_LOAD();
    for (;;) {
        ready_list = OPEN_CFW_FREERTOS_SWITCH_READY_LIST(priority);
        if (ready_list->item_count != 0U) {
            break;
        }
        OPEN_CFW_FREERTOS_SWITCH_ASSERT(priority != 0U);
        --priority;
    }

    ready_list->index = ready_list->index->next;
    if (
        ready_list->index ==
        (struct open_cfw_freertos_switch_list_item *)(void *)&ready_list->end
    ) {
        ready_list->index = ready_list->index->next;
    }
    item = ready_list->index;
    OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_STORE(
        (struct open_cfw_freertos_switch_tcb *)item->owner
    );
    OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_STORE(priority);

    tcb = OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD();
    OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORD(
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD()
    )->switched_in = tcb->task_number;

    OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_STORE(
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD() + 1U
    );
    if (
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD() >=
        OPEN_CFW_FREERTOS_SWITCH_TRACE_CAPACITY
    ) {
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_STORE(0U);
    }
}
