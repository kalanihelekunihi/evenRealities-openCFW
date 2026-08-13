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
 * Bounded, freestanding adaptation of xTaskGetTickCount() and
 * xTaskGetTickCountFromISR() from the authenticated FreeRTOS-Kernel V10.5.1
 * tasks.c at commit def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The selected G2 Cortex-M55 port uses a 32-bit TickType_t and
 * portTICK_TYPE_IS_ATOMIC == 1.  FreeRTOS therefore defines away both
 * functions' tick critical/mask macros, leaving one volatile load of
 * xTickCount.  The official Apollo-main leaves at
 * [0x00454EFE, 0x00454F06) and [0x00454F06, 0x00454F10) both resolve their
 * PC-relative literal to the recovered xTickCount word at 0x20074A34.  IAR
 * retained a leading `movs r0, #0` in the ISR leaf for the saved-mask value
 * that the released atomic-port clear macro discards.
 *
 * The load remains an explicit provider so each public leaf can be extracted
 * and relocated independently without an undefined data-symbol relocation.
 */

#include "runtime_freertos_tick_count.h"

#if defined(OPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF) && \
    (defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_TASK) + \
        defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_FROM_ISR) + \
        defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_PROVIDER)) != 1
#error "select exactly one FreeRTOS tick-count leaf"
#endif

#if !defined(OPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_PROVIDER)
__attribute__((used, noinline))
open_cfw_freertos_tick_type open_cfw_freertos_tick_count_read(void)
{
    return OPEN_CFW_FREERTOS_TICK_COUNT_WORD;
}
#endif

#if !defined(OPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_TASK)
__attribute__((used, noinline))
open_cfw_freertos_tick_type
open_cfw_freertos_task_get_tick_count(void)
{
    open_cfw_freertos_tick_type ticks;

    ticks = OPEN_CFW_FREERTOS_TICK_COUNT_READ();

    return ticks;
}
#endif

#if !defined(OPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_TICK_COUNT_LEAF_FROM_ISR)
__attribute__((used, noinline))
open_cfw_freertos_tick_type
open_cfw_freertos_task_get_tick_count_from_isr(void)
{
    open_cfw_freertos_tick_type ticks;

    ticks = OPEN_CFW_FREERTOS_TICK_COUNT_READ();

    return ticks;
}
#endif
