/* Copyright (c) 2013-2022 Arm Limited. SPDX-License-Identifier: Apache-2.0 */
typedef __UINT32_TYPE__ open_cfw_cmsis_priority_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_priority_int32;
extern open_cfw_cmsis_priority_uint32 open_cfw_cmsis_irq_context(void);
struct open_cfw_freertos_priority_set_tcb;
extern void open_cfw_freertos_task_priority_set(
    struct open_cfw_freertos_priority_set_tcb *task,
    open_cfw_cmsis_priority_uint32 priority
);
__attribute__((used,noinline))
open_cfw_cmsis_priority_int32 open_cfw_cmsis_thread_set_priority(void *task, open_cfw_cmsis_priority_int32 priority)
{
    if (open_cfw_cmsis_irq_context()!=0U) return -6;
    if ((task==(void *)0)||(priority<1)||(priority>56)) return -4;
    open_cfw_freertos_task_priority_set(task,(open_cfw_cmsis_priority_uint32)priority);
    return 0;
}
