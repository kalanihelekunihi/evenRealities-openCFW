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
 * Bounded, freestanding adaptation of uxQueueMessagesWaiting() from the
 * authenticated FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  Its official Apollo-main
 * span is [0x00441E66, 0x00441E8A).
 *
 * The task-context leaf samples the volatile queue count inside the recovered
 * FreeRTOS critical section after configASSERT.
 */

#include "runtime_freertos_queue_messages_waiting.h"

__attribute__((used, noinline))
open_cfw_freertos_queue_messages_ubase_type
open_cfw_freertos_queue_messages_waiting(
    const struct open_cfw_freertos_queue_messages_control *queue
)
{
    open_cfw_freertos_queue_messages_ubase_type result;

    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT(queue != 0);

    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL();
    {
        result = queue->messages_waiting;
    }
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL();

    return result;
}
