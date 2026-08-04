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
 * Bounded, freestanding adaptation of prvResetNextTaskUnblockTime() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official Apollo-main private leaf at [0x00455876, 0x0045589C) reads the
 * volatile pxDelayedTaskList word at 0x20074A24. If its List_t count is zero,
 * it writes portMAX_DELAY to xNextTaskUnblockTime at 0x20074A50. Otherwise it
 * reloads pxDelayedTaskList and stores the head ListItem_t value. The explicit
 * second load preserves the released volatile evaluation order.
 */

#include "runtime_freertos_reset_next_task_unblock_time.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_reset_next_task_unblock_time(void)
{
    struct open_cfw_freertos_reset_unblock_list *delayed_list;
    open_cfw_freertos_reset_unblock_tick_type next_unblock_time;

    delayed_list = OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD();
    if (OPEN_CFW_FREERTOS_DELAYED_LIST_COUNT_READ(delayed_list) == 0U) {
        next_unblock_time =
            (open_cfw_freertos_reset_unblock_tick_type)-1;
    } else {
        delayed_list = OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD();
        next_unblock_time =
            OPEN_CFW_FREERTOS_DELAYED_LIST_HEAD_VALUE_READ(delayed_list);
    }

    OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_STORE(next_unblock_time);
}
