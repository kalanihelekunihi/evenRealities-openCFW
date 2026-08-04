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
 * Bounded production source replacement for pcTaskGetName() from tasks.c at
 * authenticated FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The released algorithm is retained exactly. Focused G2 disassembly supplies
 * only the fixed pxCurrentTCB word, the 32-byte task-name field at TCB offset
 * 0x34, and the configured fail-stop assertion binding.
 */

typedef unsigned int open_cfw_freertos_pc_task_get_name_u32;
typedef void *open_cfw_freertos_pc_task_get_name_handle;

typedef struct open_cfw_freertos_pc_task_get_name_tcb_prefix
{
    open_cfw_freertos_pc_task_get_name_u32 px_top_of_stack;
    open_cfw_freertos_pc_task_get_name_u32 state_list_item[5];
    open_cfw_freertos_pc_task_get_name_u32 event_list_item[5];
    open_cfw_freertos_pc_task_get_name_u32 priority;
    open_cfw_freertos_pc_task_get_name_u32 stack_base;
    char task_name[32];
} open_cfw_freertos_pc_task_get_name_tcb_prefix;

_Static_assert(
    __builtin_offsetof(
        open_cfw_freertos_pc_task_get_name_tcb_prefix,
        task_name
    ) == 0x34U,
    "G2 pcTaskName offset changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_pc_task_get_name_tcb_prefix) == 0x54U,
    "G2 TCB prefix through pcTaskName changed"
);

#ifndef OPEN_CFW_FREERTOS_PC_TASK_GET_NAME_CURRENT_TCB
#define OPEN_CFW_FREERTOS_PC_TASK_GET_NAME_CURRENT_TCB \
    (*(open_cfw_freertos_pc_task_get_name_handle volatile *) \
        (__UINTPTR_TYPE__)0x20074A20U)
#endif

extern open_cfw_freertos_pc_task_get_name_u32 ulSetInterruptMask(void);

__attribute__((used, noinline))
char *open_cfw_freertos_pc_task_get_name(
    open_cfw_freertos_pc_task_get_name_handle task_to_query
)
{
    open_cfw_freertos_pc_task_get_name_tcb_prefix *tcb;

    tcb = (open_cfw_freertos_pc_task_get_name_tcb_prefix *)
        (
            (task_to_query == (open_cfw_freertos_pc_task_get_name_handle)0)
                ? OPEN_CFW_FREERTOS_PC_TASK_GET_NAME_CURRENT_TCB
                : task_to_query
        );

    if (tcb == (open_cfw_freertos_pc_task_get_name_tcb_prefix *)0)
    {
        (void)ulSetInterruptMask();
        *(volatile open_cfw_freertos_pc_task_get_name_u32 *)
            (__UINTPTR_TYPE__)0xFFFFFFFFU = 0U;

        for (;;)
        {
        }
    }

    return &(tcb->task_name[0]);
}
