/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of vTaskGetInfo() from authenticated commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. The G2 compile-time selections
 * are configUSE_TRACE_FACILITY=1, configUSE_MUTEXES=1,
 * configGENERATE_RUN_TIME_STATS=0, INCLUDE_vTaskSuspend=1, downward-growing
 * stacks, 32-bit StackType_t, and a 16-bit configSTACK_DEPTH_TYPE.
 */

#include "runtime_freertos_task_get_info.h"

extern enum open_cfw_freertos_task_get_info_state
open_cfw_freertos_task_get_state(
    const struct open_cfw_freertos_task_get_info_tcb *task
);
extern void open_cfw_freertos_task_suspend_all(void);
extern open_cfw_freertos_task_get_info_u32
open_cfw_freertos_task_resume_all(void);
extern open_cfw_freertos_task_get_info_u16
open_cfw_freertos_task_check_free_stack_space(
    const open_cfw_freertos_task_get_info_u8 *stack_byte
);

__attribute__((used, noinline))
void open_cfw_freertos_task_get_info(
    struct open_cfw_freertos_task_get_info_tcb *task,
    struct open_cfw_freertos_task_get_info_status *status,
    open_cfw_freertos_task_get_info_u32 get_free_stack_space,
    enum open_cfw_freertos_task_get_info_state state
)
{
    struct open_cfw_freertos_task_get_info_tcb *current;

    current = OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_LOAD();
    if (task == 0) {
        task = current;
    }

    status->handle = task;
    status->name = task->name;
    status->current_priority = task->priority;
    status->stack_base = task->stack;
    status->task_number = task->tcb_number;
    status->base_priority = task->base_priority;
    status->run_time_counter = 0U;

    if (state != OPEN_CFW_FREERTOS_TASK_GET_INFO_INVALID) {
        if (task == current) {
            status->current_state =
                (open_cfw_freertos_task_get_info_u8)
                    OPEN_CFW_FREERTOS_TASK_GET_INFO_RUNNING;
        } else {
            status->current_state =
                (open_cfw_freertos_task_get_info_u8)state;
            if (state == OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED) {
                open_cfw_freertos_task_suspend_all();
                if (task->event_list_item.container != 0) {
                    status->current_state =
                        (open_cfw_freertos_task_get_info_u8)
                            OPEN_CFW_FREERTOS_TASK_GET_INFO_BLOCKED;
                }
                (void)open_cfw_freertos_task_resume_all();
            }
        }
    } else {
        status->current_state =
            (open_cfw_freertos_task_get_info_u8)
                open_cfw_freertos_task_get_state(task);
    }

    if (get_free_stack_space != 0U) {
        status->stack_high_water_mark =
            open_cfw_freertos_task_check_free_stack_space(task->stack);
    } else {
        status->stack_high_water_mark = 0U;
    }
}
