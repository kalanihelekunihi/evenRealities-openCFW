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
 * Bounded, freestanding port of xTaskGetCurrentTaskHandle() from
 * FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image places the complete eight-byte leaf at
 * [0x0045589C, 0x004558A4).  Its PC-relative literal at 0x0045605C names
 * the stock pxCurrentTCB word at 0x20074A20.  No TCB field is accessed.
 *
 * The source-owned boundary retains only the recovered fixed pxCurrentTCB
 * word. It does not dereference a TCB field or depend on the vendor
 * stack-depth extension in the complete G2 TCB layout.
 */

typedef void *open_cfw_freertos_task_handle;

#ifndef OPEN_CFW_FREERTOS_TASK_CURRENT_TCB
#define OPEN_CFW_FREERTOS_TASK_CURRENT_TCB \
    (*(open_cfw_freertos_task_handle volatile *) \
        (__UINTPTR_TYPE__)0x20074A20U)
#endif

__attribute__((used, noinline))
open_cfw_freertos_task_handle
open_cfw_freertos_task_get_current_task_handle(void)
{
    open_cfw_freertos_task_handle result;

    result = OPEN_CFW_FREERTOS_TASK_CURRENT_TCB;

    return result;
}
