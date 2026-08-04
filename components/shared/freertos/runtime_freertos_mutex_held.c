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
 * Bounded, freestanding adaptation of pvTaskIncrementMutexHeldCount() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official Apollo-main leaf at [0x00455AE0, 0x00455AF6) is enabled by
 * configUSE_MUTEXES=1.  It reads the volatile pxCurrentTCB word at 0x20074A20,
 * increments the 32-bit UBaseType_t uxMutexesHeld field at TCB offset 0x64
 * only when the second current-TCB snapshot is nonnull, and returns the final
 * current-TCB snapshot.
 */

#include "runtime_freertos_mutex_held.h"

__attribute__((used, noinline))
open_cfw_freertos_mutex_held_task_handle
open_cfw_freertos_task_increment_mutex_held_count(void)
{
    open_cfw_freertos_mutex_held_uintptr current_tcb;

    current_tcb = OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ();
    if (current_tcb != (open_cfw_freertos_mutex_held_uintptr)0U) {
        current_tcb = OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ();
        OPEN_CFW_FREERTOS_MUTEX_HELD_INCREMENT(current_tcb);
    }

    return (open_cfw_freertos_mutex_held_task_handle)
        OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ();
}
