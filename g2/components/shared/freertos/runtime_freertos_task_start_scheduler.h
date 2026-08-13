/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded bounded scheduler-start adaptation.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_START_SCHEDULER_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_START_SCHEDULER_H

typedef unsigned int open_cfw_freertos_start_u32;
typedef int open_cfw_freertos_start_base_type;
typedef void *open_cfw_freertos_start_task_handle;
typedef void (*open_cfw_freertos_start_task_function)(void *argument);

extern open_cfw_freertos_start_task_handle volatile
    open_cfw_retained_freertos_idle_task_handle;
extern volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_next_task_unblock_time;
extern volatile open_cfw_freertos_start_base_type
    open_cfw_retained_freertos_scheduler_running;
extern volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_tick_count;
extern const volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_top_used_priority;

extern const char open_cfw_freertos_idle_task_name[];

void open_cfw_freertos_task_start_scheduler(void);

#endif
