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
 * Candidate-only isolated adaptation of prvTaskCheckFreeStackSpace() from the
 * authenticated FreeRTOS-Kernel V10.5.1 tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 helper occupies [0x00455820, 0x00455836). Focused
 * disassembly proves tskSTACK_FILL_BYTE=0xA5, portSTACK_GROWTH=-1,
 * sizeof(StackType_t)=4, and a 16-bit configSTACK_DEPTH_TYPE. This candidate
 * deliberately has no production overlay or patch-site registration.
 */

#include "runtime_freertos_task_check_free_stack_space.h"

__attribute__((used, noinline))
open_cfw_freertos_stack_depth_type
open_cfw_freertos_task_check_free_stack_space(
    const open_cfw_freertos_stack_byte *stack_byte
)
{
    __UINT32_TYPE__ count = 0U;

    while (
        *stack_byte
        == (open_cfw_freertos_stack_byte)
            OPEN_CFW_FREERTOS_STACK_FILL_BYTE
    ) {
        stack_byte -= OPEN_CFW_FREERTOS_STACK_GROWTH;
        count++;
    }

    count /= (__UINT32_TYPE__)sizeof(open_cfw_freertos_stack_type);

    return (open_cfw_freertos_stack_depth_type)count;
}
