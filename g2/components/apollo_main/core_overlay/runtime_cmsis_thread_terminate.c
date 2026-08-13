/* Copyright (c) 2013-2022 Arm Limited. SPDX-License-Identifier: Apache-2.0 */
typedef __UINT32_TYPE__ open_cfw_cmsis_terminate_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_terminate_int32;
extern open_cfw_cmsis_terminate_uint32 open_cfw_cmsis_irq_context(void);
struct open_cfw_freertos_task_delete_tcb;
extern int open_cfw_freertos_task_get_state(
    const struct open_cfw_freertos_task_delete_tcb *task
);
extern void open_cfw_freertos_task_delete(
    struct open_cfw_freertos_task_delete_tcb *task
);
__attribute__((used,noinline))
open_cfw_cmsis_terminate_int32 open_cfw_cmsis_thread_terminate(void *task)
{
    if (open_cfw_cmsis_irq_context()!=0U) return -6;
    if (task==(void *)0) return -4;
    if (open_cfw_freertos_task_get_state(task)==4) return -3;
    open_cfw_freertos_task_delete(task);
    return 0;
}
