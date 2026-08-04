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
 * Bounded, freestanding adaptation of vTaskSuspendAll() from the authenticated
 * FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official Apollo-main leaf at [0x00454D7C, 0x00454D88) performs one
 * volatile 32-bit read, wrapping unsigned increment, and volatile store to
 * uxSchedulerSuspended at 0x20074A58.  The source barriers preserve the
 * upstream portSOFTWARE_BARRIER()/portMEMORY_BARRIER() ordering contract while
 * emitting no target instruction for the recovered G2 port configuration.
 */

#include "runtime_freertos_suspend_all.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_suspend_all(void)
{
    open_cfw_freertos_suspend_all_ubase_type suspended_depth;

    OPEN_CFW_FREERTOS_SUSPEND_ALL_SOFTWARE_BARRIER();
    suspended_depth = OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_READ();
    suspended_depth +=
        (open_cfw_freertos_suspend_all_ubase_type)1U;
    OPEN_CFW_FREERTOS_SUSPEND_ALL_DEPTH_WRITE(suspended_depth);
    OPEN_CFW_FREERTOS_SUSPEND_ALL_MEMORY_BARRIER();
}
