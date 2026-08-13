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
 * Integrated, freestanding port of uxTaskGetNumberOfTasks() from
 * FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image places the complete six-byte leaf at
 * [0x00454F10, 0x00454F16). Its PC-relative literal at 0x004551A0 names
 * the stock uxCurrentNumberOfTasks word at 0x20074A30.
 *
 * The overlay replaces only the complete function entry. The fixed SRAM word
 * remains compatibility state owned by the official kernel until its global
 * data layout is migrated atomically.
 */

typedef unsigned int open_cfw_freertos_task_count_type;

typedef char open_cfw_freertos_task_count_type_must_be_32_bits[
    __SIZEOF_INT__ == 4 ? 1 : -1
];

#ifndef OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT
#define OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT \
    (*(volatile open_cfw_freertos_task_count_type *) \
        (__UINTPTR_TYPE__)0x20074A30U)
#endif

__attribute__((used, noinline))
open_cfw_freertos_task_count_type
open_cfw_freertos_task_get_number_of_tasks(void)
{
    return OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT;
}
