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
 * Isolated, non-production candidate for pcTaskGetName() from tasks.c at
 * FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image owns the complete function at
 * [0x00454F16, 0x00454F38). The released algorithm selects pxCurrentTCB when
 * passed NULL, asserts that the selected TCB is non-NULL, and returns the first
 * byte of pcTaskName. The authenticated G2 layout places pxCurrentTCB at
 * 0x20074A20 and pcTaskName at TCB offset 0x34.
 *
 * This file is deliberately not registered by the production overlay. Its
 * assertion path retains the known ulSetInterruptMask() dependency so a future
 * integration must bind that port seam explicitly.
 */

typedef unsigned int open_cfw_freertos_u32;
typedef void *open_cfw_freertos_task_handle;

typedef struct open_cfw_freertos_tcb_name_prefix
{
    open_cfw_freertos_u32 px_top_of_stack;
    open_cfw_freertos_u32 state_list_item[5];
    open_cfw_freertos_u32 event_list_item[5];
    open_cfw_freertos_u32 priority;
    open_cfw_freertos_u32 stack_base;
    char task_name[32];
} open_cfw_freertos_tcb_name_prefix;

_Static_assert(
    __builtin_offsetof(open_cfw_freertos_tcb_name_prefix, task_name) == 0x34,
    "G2 pcTaskName offset changed");
_Static_assert(
    sizeof(open_cfw_freertos_tcb_name_prefix) == 0x54,
    "G2 prefix through pcTaskName changed");

#ifndef OPEN_CFW_FREERTOS_CURRENT_TCB
#define OPEN_CFW_FREERTOS_CURRENT_TCB \
    (*(open_cfw_freertos_task_handle volatile *) \
        (__UINTPTR_TYPE__)0x20074A20U)
#endif

/*
 * The official assertion path calls the Cortex-M55 port leaf at 0x005FA0A4.
 * Keeping the source symbol unresolved in this isolated object prevents an
 * accidental production integration without an explicit port binding.
 */
extern open_cfw_freertos_u32 ulSetInterruptMask(void);

__attribute__((noreturn, noinline))
static void open_cfw_freertos_pc_task_get_name_assert(void)
{
    (void)ulSetInterruptMask();
    *(volatile open_cfw_freertos_u32 *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U;

    for (;;)
    {
    }
}

__attribute__((used, noinline))
char *open_cfw_freertos_pc_task_get_name(
    open_cfw_freertos_task_handle task_to_query)
{
    open_cfw_freertos_tcb_name_prefix *tcb;

    if (task_to_query == (open_cfw_freertos_task_handle)0)
    {
        tcb = (open_cfw_freertos_tcb_name_prefix *)
            OPEN_CFW_FREERTOS_CURRENT_TCB;
    }
    else
    {
        tcb = (open_cfw_freertos_tcb_name_prefix *)task_to_query;
    }

    if (tcb == (open_cfw_freertos_tcb_name_prefix *)0)
    {
        open_cfw_freertos_pc_task_get_name_assert();
    }

    return &(tcb->task_name[0]);
}
