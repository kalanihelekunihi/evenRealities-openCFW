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
 * Bounded, freestanding adaptation of xTaskCheckForTimeOut() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official Apollo-main
 * function is [0x00455566, 0x004555E6).
 *
 * Focused disassembly selects INCLUDE_vTaskSuspend=1,
 * INCLUDE_xTaskAbortDelay=0, 32-bit ticks, and portMAX_DELAY=UINT32_MAX.
 * This reviewed source is registered by the Apollo-main production overlay.
 */

#include "runtime_freertos_task_check_for_timeout.h"

__attribute__((used, noinline))
open_cfw_freertos_check_timeout_base_type
open_cfw_freertos_task_check_for_timeout(
    struct open_cfw_freertos_check_timeout_state *timeout,
    open_cfw_freertos_check_timeout_tick_type *ticks_to_wait
)
{
    open_cfw_freertos_check_timeout_base_type result;

    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT(timeout != 0);
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT(ticks_to_wait != 0);

    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL();
    {
        const open_cfw_freertos_check_timeout_tick_type const_tick_count =
            OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_LOAD();
        const open_cfw_freertos_check_timeout_tick_type elapsed_time =
            const_tick_count - timeout->time_on_entering;

        if (
            *ticks_to_wait ==
            (open_cfw_freertos_check_timeout_tick_type)
            OPEN_CFW_FREERTOS_CHECK_TIMEOUT_MAX_DELAY
        ) {
            result = OPEN_CFW_FREERTOS_CHECK_TIMEOUT_FALSE;
        } else if (
            (OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_LOAD() !=
             timeout->overflow_count) &&
            (const_tick_count >= timeout->time_on_entering)
        ) {
            result = OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TRUE;
            *ticks_to_wait =
                (open_cfw_freertos_check_timeout_tick_type)0U;
        } else if (elapsed_time < *ticks_to_wait) {
            *ticks_to_wait -= elapsed_time;
            OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET(timeout);
            result = OPEN_CFW_FREERTOS_CHECK_TIMEOUT_FALSE;
        } else {
            *ticks_to_wait =
                (open_cfw_freertos_check_timeout_tick_type)0U;
            result = OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TRUE;
        }
    }
    OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL();

    return result;
}
