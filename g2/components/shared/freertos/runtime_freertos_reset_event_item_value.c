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
 * Bounded, freestanding adaptation of uxTaskResetEventItemValue() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official Apollo-main leaf at [0x00455ACA, 0x00455AE0) reads the event
 * list item value at TCB + 0x18, writes configMAX_PRIORITIES - uxPriority
 * through a separately evaluated current TCB, and returns the original value.
 * pxCurrentTCB is the volatile compatibility word at 0x20074A20.
 */

#include "runtime_freertos_reset_event_item_value.h"

__attribute__((used, noinline))
open_cfw_freertos_tick_type
open_cfw_freertos_task_reset_event_item_value(void)
{
    struct open_cfw_freertos_event_tcb *read_tcb;
    struct open_cfw_freertos_event_tcb *write_tcb;
    struct open_cfw_freertos_event_tcb *priority_tcb;
    open_cfw_freertos_tick_type original_value;

    read_tcb = OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD();
    original_value = read_tcb->event_item_value;
    write_tcb = OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD();
    priority_tcb = OPEN_CFW_FREERTOS_CURRENT_TCB_LOAD();
    write_tcb->event_item_value =
        (open_cfw_freertos_tick_type)OPEN_CFW_FREERTOS_MAX_PRIORITIES
        - (open_cfw_freertos_tick_type)priority_tcb->priority;

    return original_value;
}
