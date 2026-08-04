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
 * Bounded, freestanding adaptation of vTaskInternalSetTimeOutState() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official Apollo-main leaf at [0x00455556, 0x00455566) first reads the
 * volatile xNumOfOverflows word at 0x20074A48 and stores it to TimeOut_t +0,
 * then reads the volatile xTickCount word at 0x20074A34 and stores it to
 * TimeOut_t +4.  This internal helper intentionally has no critical section.
 */

#include "runtime_freertos_timeout_state.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_internal_set_timeout_state(
    struct open_cfw_freertos_timeout_state *timeout
)
{
    open_cfw_freertos_timeout_base_type overflow_count;
    open_cfw_freertos_timeout_tick_type tick_count;

    overflow_count = OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_READ();
    OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_STORE(timeout, overflow_count);
    tick_count = OPEN_CFW_FREERTOS_TIMEOUT_TICK_READ();
    OPEN_CFW_FREERTOS_TIMEOUT_TICK_STORE(timeout, tick_count);
}
