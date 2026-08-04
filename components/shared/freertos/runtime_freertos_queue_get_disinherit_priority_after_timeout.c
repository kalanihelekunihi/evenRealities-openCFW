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
 * Production isolated adaptation of
 * prvGetDisinheritPriorityAfterTimeout() from the authenticated
 * FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 helper occupies [0x00441EC4, 0x00441ED8). Focused
 * disassembly proves configMAX_PRIORITIES=56, tskIDLE_PRIORITY=0, the
 * receive-wait List_t at Queue_t +0x24, and its head pointer at Queue_t
 * +0x30. Production binds the source-owned semaphore-take call directly to
 * this appended leaf; the unreachable stock helper entry remains unpatched.
 */

#include "runtime_freertos_queue_get_disinherit_priority_after_timeout.h"

__attribute__((used, noinline))
open_cfw_freertos_disinherit_ubase_type
open_cfw_freertos_queue_get_disinherit_priority_after_timeout(
    const void *queue
)
{
    open_cfw_freertos_disinherit_ubase_type highest_waiting_priority;

    if (OPEN_CFW_FREERTOS_DISINHERIT_LIST_LENGTH(queue) > 0U) {
        highest_waiting_priority =
            (open_cfw_freertos_disinherit_ubase_type)
                OPEN_CFW_FREERTOS_DISINHERIT_MAX_PRIORITIES -
            (open_cfw_freertos_disinherit_ubase_type)
                OPEN_CFW_FREERTOS_DISINHERIT_HEAD_ITEM_VALUE(queue);
    } else {
        highest_waiting_priority =
            (open_cfw_freertos_disinherit_ubase_type)
                OPEN_CFW_FREERTOS_DISINHERIT_IDLE_PRIORITY;
    }

    return highest_waiting_priority;
}
