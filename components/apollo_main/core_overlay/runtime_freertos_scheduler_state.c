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
 * Integrated, freestanding port of xTaskGetSchedulerState() from
 * FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image places the complete 32-byte leaf at
 * [0x004558A4, 0x004558C4). Its two PC-relative literals name the stock
 * xSchedulerRunning word at 0x20074A3C and uxSchedulerSuspended word at
 * 0x20074A58.
 *
 * The overlay replaces only the complete function entry. The fixed SRAM words
 * remain compatibility state owned by the official kernel until its global
 * data layout is migrated atomically.
 */

typedef signed int open_cfw_freertos_base_type;
typedef unsigned int open_cfw_freertos_ubase_type;

typedef char open_cfw_freertos_scheduler_state_base_type_must_be_32_bits[
    __SIZEOF_INT__ == 4 ? 1 : -1
];

#ifndef OPEN_CFW_FREERTOS_SCHEDULER_RUNNING
#define OPEN_CFW_FREERTOS_SCHEDULER_RUNNING \
    (*(volatile open_cfw_freertos_base_type *) \
        (__UINTPTR_TYPE__)0x20074A3CU)
#endif

#ifndef OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED
#define OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED \
    (*(volatile open_cfw_freertos_ubase_type *) \
        (__UINTPTR_TYPE__)0x20074A58U)
#endif

#define OPEN_CFW_TASK_SCHEDULER_SUSPENDED \
    ((open_cfw_freertos_base_type)0)
#define OPEN_CFW_TASK_SCHEDULER_NOT_STARTED \
    ((open_cfw_freertos_base_type)1)
#define OPEN_CFW_TASK_SCHEDULER_RUNNING \
    ((open_cfw_freertos_base_type)2)

__attribute__((used, noinline))
open_cfw_freertos_base_type
open_cfw_freertos_task_get_scheduler_state(void)
{
    open_cfw_freertos_base_type result;

    if (OPEN_CFW_FREERTOS_SCHEDULER_RUNNING == 0) {
        result = OPEN_CFW_TASK_SCHEDULER_NOT_STARTED;
    } else {
        if (OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED == 0U) {
            result = OPEN_CFW_TASK_SCHEDULER_RUNNING;
        } else {
            result = OPEN_CFW_TASK_SCHEDULER_SUSPENDED;
        }
    }

    return result;
}
