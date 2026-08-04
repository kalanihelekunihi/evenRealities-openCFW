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
 * Bounded, freestanding adaptation of vTaskRemoveFromUnorderedEventList()
 * from authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2 body is
 * [0x0045547C,0x00455556).  This module is production-registered by the
 * Apollo-main core overlay; hosted differential fixtures retain the
 * candidate/oracle terminology only to distinguish this implementation from
 * pristine upstream tasks.c/list.c.
 */

#include "runtime_freertos_task_remove_from_unordered_event_list.h"

static __attribute__((always_inline)) inline void
open_cfw_freertos_unordered_list_remove_inline(
    struct open_cfw_freertos_unordered_list_item *item
)
{
    struct open_cfw_freertos_unordered_list *list = item->container;

    item->next->previous = item->previous;
    item->previous->next = item->next;
    if (list->index == item) {
        list->index = item->previous;
    }
    item->container = (struct open_cfw_freertos_unordered_list *)0;
    --list->item_count;
}

static __attribute__((always_inline)) inline void
open_cfw_freertos_unordered_list_insert_end_inline(
    struct open_cfw_freertos_unordered_list *list,
    struct open_cfw_freertos_unordered_list_item *item
)
{
    struct open_cfw_freertos_unordered_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

__attribute__((used, noinline))
void open_cfw_freertos_task_remove_from_unordered_event_list(
    struct open_cfw_freertos_unordered_list_item *event_list_item,
    open_cfw_freertos_unordered_tick_type item_value
)
{
    struct open_cfw_freertos_unordered_tcb *unblocked_tcb;
    struct open_cfw_freertos_unordered_list *ready_list;

    OPEN_CFW_FREERTOS_UNORDERED_ASSERT(
        OPEN_CFW_FREERTOS_UNORDERED_SCHEDULER_SUSPENDED_LOAD() !=
        (open_cfw_freertos_unordered_ubase_type)
        OPEN_CFW_FREERTOS_UNORDERED_FALSE
    );

    event_list_item->item_value =
        item_value | OPEN_CFW_FREERTOS_UNORDERED_VALUE_IN_USE;
    unblocked_tcb = (struct open_cfw_freertos_unordered_tcb *)
        event_list_item->owner;
    OPEN_CFW_FREERTOS_UNORDERED_ASSERT(unblocked_tcb != 0);
    open_cfw_freertos_unordered_list_remove_inline(event_list_item);

    OPEN_CFW_FREERTOS_UNORDERED_RESET_NEXT_UNBLOCK();

    open_cfw_freertos_unordered_list_remove_inline(
        &unblocked_tcb->state_list_item
    );
    OPEN_CFW_FREERTOS_UNORDERED_TRACE_MOVED_TO_READY(unblocked_tcb);
    if (
        unblocked_tcb->priority >
        OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_LOAD()
    ) {
        OPEN_CFW_FREERTOS_UNORDERED_TOP_READY_PRIORITY_STORE(
            unblocked_tcb->priority
        );
    }
    ready_list = OPEN_CFW_FREERTOS_UNORDERED_READY_LIST(
        unblocked_tcb->priority
    );
    open_cfw_freertos_unordered_list_insert_end_inline(
        ready_list,
        &unblocked_tcb->state_list_item
    );

    if (
        unblocked_tcb->priority >
        OPEN_CFW_FREERTOS_UNORDERED_CURRENT_TCB_LOAD()->priority
    ) {
        OPEN_CFW_FREERTOS_UNORDERED_YIELD_PENDING_STORE(
            OPEN_CFW_FREERTOS_UNORDERED_TRUE
        );
    }
}
