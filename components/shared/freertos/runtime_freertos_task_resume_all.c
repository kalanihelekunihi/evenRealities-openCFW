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
 * Bounded, freestanding adaptation of xTaskResumeAll() from authenticated
 * FreeRTOS-Kernel V10.5.1 tasks.c commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2 body is
 * [0x00454DCC, 0x00454EFE).  Recovered configuration: preemption enabled,
 * generic ready-priority tracking, 32-bit ticks, empty trace/coverage hooks,
 * and configMAX_PRIORITIES=56.
 *
 * This implementation is registered in the Apollo-main production overlay as
 * part of the source-owned scheduler cluster.  The fixed G2 ABI seams above
 * remain the compatibility boundary for the live replacement.
 */

#include "runtime_freertos_task_resume_all.h"

static __attribute__((always_inline)) inline void
open_cfw_freertos_resume_list_remove_inline(
    struct open_cfw_freertos_resume_list_item *item
)
{
    struct open_cfw_freertos_resume_list *list = item->container;

    item->next->previous = item->previous;
    item->previous->next = item->next;
    if (list->index == item) {
        list->index = item->previous;
    }
    item->container = (struct open_cfw_freertos_resume_list *)0;
    --list->item_count;
}

static __attribute__((always_inline)) inline void
open_cfw_freertos_resume_list_insert_end_inline(
    struct open_cfw_freertos_resume_list *list,
    struct open_cfw_freertos_resume_list_item *item
)
{
    struct open_cfw_freertos_resume_list_item *index = list->index;

    item->next = index;
    item->previous = index->previous;
    index->previous->next = item;
    index->previous = item;
    item->container = list;
    ++list->item_count;
}

__attribute__((used, noinline))
open_cfw_freertos_resume_base_type
open_cfw_freertos_task_resume_all(void)
{
    struct open_cfw_freertos_resume_tcb *tcb =
        (struct open_cfw_freertos_resume_tcb *)0;
    struct open_cfw_freertos_resume_list *pending_list;
    struct open_cfw_freertos_resume_list *ready_list;
    open_cfw_freertos_resume_tick_type pended_counts;
    open_cfw_freertos_resume_ubase_type suspended;
    open_cfw_freertos_resume_base_type already_yielded =
        OPEN_CFW_FREERTOS_RESUME_FALSE;

    OPEN_CFW_FREERTOS_RESUME_ASSERT(
        OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD() != 0U
    );

    OPEN_CFW_FREERTOS_RESUME_ENTER_CRITICAL();

    suspended = OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD() - 1U;
    OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_STORE(suspended);

    if (OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD() == 0U) {
        if (OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_LOAD() > 0U) {
            pending_list = OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST();
            while (pending_list->item_count != 0U) {
                tcb = (struct open_cfw_freertos_resume_tcb *)
                    pending_list->end.next->owner;

                open_cfw_freertos_resume_list_remove_inline(
                    &tcb->event_list_item
                );
                OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER();
                open_cfw_freertos_resume_list_remove_inline(
                    &tcb->state_list_item
                );

                if (
                    tcb->priority >
                    OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_LOAD()
                ) {
                    OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_STORE(
                        tcb->priority
                    );
                }
                ready_list = OPEN_CFW_FREERTOS_RESUME_READY_LIST(
                    tcb->priority
                );
                open_cfw_freertos_resume_list_insert_end_inline(
                    ready_list,
                    &tcb->state_list_item
                );

                if (
                    tcb->priority >=
                    OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_LOAD()->priority
                ) {
                    OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE(
                        OPEN_CFW_FREERTOS_RESUME_TRUE
                    );
                }
            }

            if (tcb != (struct open_cfw_freertos_resume_tcb *)0) {
                OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME();
            }

            pended_counts = OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_LOAD();
            if (pended_counts > 0U) {
                do {
                    if (
                        OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK() !=
                        OPEN_CFW_FREERTOS_RESUME_FALSE
                    ) {
                        OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE(
                            OPEN_CFW_FREERTOS_RESUME_TRUE
                        );
                    }
                    --pended_counts;
                } while (pended_counts > 0U);

                OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_STORE(0U);
            }

            if (OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_LOAD() != 0) {
                already_yielded = OPEN_CFW_FREERTOS_RESUME_TRUE;
                OPEN_CFW_FREERTOS_RESUME_YIELD();
            }
        }
    }

    OPEN_CFW_FREERTOS_RESUME_EXIT_CRITICAL();
    return already_yielded;
}
