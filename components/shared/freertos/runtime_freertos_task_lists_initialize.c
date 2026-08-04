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
 * Bounded source adaptation of prvInitialiseTaskLists() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 helper occupies [0x0045568C, 0x004556E0). Disassembly
 * selects configMAX_PRIORITIES=56, INCLUDE_vTaskDelete=1, and
 * INCLUDE_vTaskSuspend=1. All six callable edges target the already
 * source-owned vListInitialise entry. Apollo-main registers this function as
 * the production replacement for that complete official helper boundary.
 */

#include "runtime_freertos_task_lists_initialize.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_lists_initialize(void)
{
    open_cfw_freertos_task_lists_ubase_type priority;

    for (
        priority = (open_cfw_freertos_task_lists_ubase_type)0U;
        priority < (open_cfw_freertos_task_lists_ubase_type)
            OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES;
        priority++
    ) {
        open_cfw_freertos_list_initialise(
            (struct open_cfw_freertos_list_initialise_list *)(void *)
                &OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS[priority]
        );
    }

    open_cfw_freertos_list_initialise(
        (struct open_cfw_freertos_list_initialise_list *)(void *)
            OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1
    );
    open_cfw_freertos_list_initialise(
        (struct open_cfw_freertos_list_initialise_list *)(void *)
            OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2
    );
    open_cfw_freertos_list_initialise(
        (struct open_cfw_freertos_list_initialise_list *)(void *)
            OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST
    );
    open_cfw_freertos_list_initialise(
        (struct open_cfw_freertos_list_initialise_list *)(void *)
            OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST
    );
    open_cfw_freertos_list_initialise(
        (struct open_cfw_freertos_list_initialise_list *)(void *)
            OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST
    );

    OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER =
        (open_cfw_freertos_task_lists_target_pointer)
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS;
    OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER =
        (open_cfw_freertos_task_lists_target_pointer)
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS;
}
