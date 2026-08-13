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
 * Bounded, freestanding adaptation of xTaskIncrementTick() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * This candidate preserves the released G2 configuration: 32-bit ticks,
 * preemption and time slicing enabled, tick hook disabled, generic numeric
 * ready-priority tracking, empty trace hooks, and the recovered List_t/TCB
 * layout. The official body is [0x0045504C, 0x0045519E).
 */

#include "runtime_freertos_task_increment_tick.h"

static __attribute__((always_inline)) inline void
open_cfw_freertos_tick_list_remove_inline(
    struct open_cfw_freertos_tick_list_item *item
)
{
    struct open_cfw_freertos_tick_list *list = item->container;

    item->next->previous = item->previous;
    item->previous->next = item->next;
    if (list->index == item) {
        list->index = item->previous;
    }
    item->container = (struct open_cfw_freertos_tick_list *)0;
    --list->item_count;
}

static __attribute__((always_inline)) inline void
open_cfw_freertos_tick_list_insert_end_inline(
    struct open_cfw_freertos_tick_list *list,
    struct open_cfw_freertos_tick_list_item *item
)
{
    struct open_cfw_freertos_tick_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

__attribute__((used, noinline))
open_cfw_freertos_tick_base_type
open_cfw_freertos_task_increment_tick(void)
{
    struct open_cfw_freertos_tick_tcb *tcb;
    struct open_cfw_freertos_tick_list *delayed_list;
    struct open_cfw_freertos_tick_list *ready_list;
    struct open_cfw_freertos_tick_list *temporary_list;
    open_cfw_freertos_tick_tick_type item_value;
    open_cfw_freertos_tick_tick_type constant_tick_count;
    open_cfw_freertos_tick_base_type switch_required =
        OPEN_CFW_FREERTOS_TICK_FALSE;

    /* traceTASK_INCREMENT_TICK() is empty in the recovered configuration. */
    if (OPEN_CFW_FREERTOS_TICK_SCHEDULER_SUSPENDED_LOAD() == 0U) {
        constant_tick_count = OPEN_CFW_FREERTOS_TICK_COUNT_LOAD() + 1U;
        OPEN_CFW_FREERTOS_TICK_COUNT_STORE(constant_tick_count);

        if (constant_tick_count == 0U) {
            delayed_list = OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD();
            OPEN_CFW_FREERTOS_TICK_ASSERT(
                delayed_list->item_count == 0U
            );

            temporary_list = OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD();
            OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_STORE(
                OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_LOAD()
            );
            OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_STORE(temporary_list);
            OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_STORE(
                OPEN_CFW_FREERTOS_TICK_OVERFLOW_COUNT_LOAD() + 1
            );
            open_cfw_freertos_task_reset_next_task_unblock_time();
        }

        if (
            constant_tick_count >=
            OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_LOAD()
        ) {
            for (;;) {
                delayed_list = OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD();
                if (delayed_list->item_count == 0U) {
                    OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_STORE(
                        OPEN_CFW_FREERTOS_TICK_PORT_MAX_DELAY
                    );
                    break;
                }

                delayed_list = OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_LOAD();
                tcb = (struct open_cfw_freertos_tick_tcb *)
                    delayed_list->end.next->owner;
                item_value = tcb->state_list_item.item_value;
                if (constant_tick_count < item_value) {
                    OPEN_CFW_FREERTOS_TICK_NEXT_UNBLOCK_TIME_STORE(
                        item_value
                    );
                    break;
                }

                open_cfw_freertos_tick_list_remove_inline(
                    &tcb->state_list_item
                );
                if (tcb->event_list_item.container != 0) {
                    open_cfw_freertos_tick_list_remove_inline(
                        &tcb->event_list_item
                    );
                }

                /* prvAddTaskToReadyList(), with both trace hooks empty. */
                if (
                    tcb->priority >
                    OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_LOAD()
                ) {
                    OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_STORE(
                        tcb->priority
                    );
                }
                ready_list = OPEN_CFW_FREERTOS_TICK_READY_LIST(
                    tcb->priority
                );
                open_cfw_freertos_tick_list_insert_end_inline(
                    ready_list,
                    &tcb->state_list_item
                );

                if (
                    tcb->priority >
                    OPEN_CFW_FREERTOS_TICK_CURRENT_TCB_LOAD()->priority
                ) {
                    switch_required = OPEN_CFW_FREERTOS_TICK_TRUE;
                }
            }
        }

        tcb = OPEN_CFW_FREERTOS_TICK_CURRENT_TCB_LOAD();
        ready_list = OPEN_CFW_FREERTOS_TICK_READY_LIST(tcb->priority);
        if (ready_list->item_count > 1U) {
            switch_required = OPEN_CFW_FREERTOS_TICK_TRUE;
        }

        /* configUSE_TICK_HOOK is zero in the recovered configuration. */
        if (OPEN_CFW_FREERTOS_TICK_YIELD_PENDING_LOAD() != 0) {
            switch_required = OPEN_CFW_FREERTOS_TICK_TRUE;
        }
    } else {
        OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_STORE(
            OPEN_CFW_FREERTOS_TICK_PENDED_TICKS_LOAD() + 1U
        );
    }

    return switch_required;
}
