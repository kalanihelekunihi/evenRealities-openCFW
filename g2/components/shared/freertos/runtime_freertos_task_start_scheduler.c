/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of vTaskStartScheduler() from authenticated commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. Stock G2 body:
 * [0x00454CEC,0x00454D7C).
 */

#include "runtime_freertos_task_start_scheduler.h"

enum {
    OPEN_CFW_FREERTOS_START_FAIL = 0,
    OPEN_CFW_FREERTOS_START_PASS = 1,
    OPEN_CFW_FREERTOS_START_COULD_NOT_ALLOCATE = -1,
    OPEN_CFW_FREERTOS_START_IDLE_PRIORITY = 0,
    OPEN_CFW_FREERTOS_START_MAX_DELAY = 0xFFFFFFFFU,
};

extern const char open_cfw_retained_freertos_idle_task_name[];

extern void open_cfw_retained_freertos_idle_task_entry(void *argument);

extern void open_cfw_retained_freertos_idle_task_memory_get(
    void **task_control_block,
    open_cfw_freertos_start_u32 **stack,
    open_cfw_freertos_start_u32 *stack_depth
);

extern open_cfw_freertos_start_task_handle
open_cfw_retained_freertos_task_create_static(
    open_cfw_freertos_start_task_function entry,
    const char *name,
    open_cfw_freertos_start_u32 stack_depth,
    void *argument,
    open_cfw_freertos_start_u32 priority,
    open_cfw_freertos_start_u32 *stack,
    void *task_control_block
);

extern open_cfw_freertos_start_base_type
open_cfw_retained_freertos_timer_task_create(void);
extern open_cfw_freertos_start_u32
open_cfw_retained_freertos_interrupt_mask_set(void);
extern open_cfw_freertos_start_base_type
open_cfw_freertos_port_start_scheduler(void);
extern void open_cfw_freertos_start_assert_failure(void);

__attribute__((used, noinline))
void open_cfw_freertos_task_start_scheduler(void)
{
    void *idle_task_control_block = (void *)0;
    open_cfw_freertos_start_u32 *idle_task_stack =
        (open_cfw_freertos_start_u32 *)0;
    open_cfw_freertos_start_u32 idle_task_stack_depth = 0U;
    open_cfw_freertos_start_base_type result;

    open_cfw_retained_freertos_idle_task_memory_get(
        &idle_task_control_block,
        &idle_task_stack,
        &idle_task_stack_depth
    );
    open_cfw_retained_freertos_idle_task_handle =
        open_cfw_retained_freertos_task_create_static(
            open_cfw_retained_freertos_idle_task_entry,
            open_cfw_retained_freertos_idle_task_name,
            idle_task_stack_depth,
            (void *)0,
            OPEN_CFW_FREERTOS_START_IDLE_PRIORITY,
            idle_task_stack,
            idle_task_control_block
        );

    result = open_cfw_retained_freertos_idle_task_handle !=
        (open_cfw_freertos_start_task_handle)0
        ? OPEN_CFW_FREERTOS_START_PASS
        : OPEN_CFW_FREERTOS_START_FAIL;

    if (result == OPEN_CFW_FREERTOS_START_PASS) {
        result = open_cfw_retained_freertos_timer_task_create();
    }

    if (result == OPEN_CFW_FREERTOS_START_PASS) {
        (void)open_cfw_retained_freertos_interrupt_mask_set();
        open_cfw_retained_freertos_next_task_unblock_time =
            OPEN_CFW_FREERTOS_START_MAX_DELAY;
        open_cfw_retained_freertos_scheduler_running =
            OPEN_CFW_FREERTOS_START_PASS;
        open_cfw_retained_freertos_tick_count = 0U;
        (void)open_cfw_freertos_port_start_scheduler();
    } else if (result == OPEN_CFW_FREERTOS_START_COULD_NOT_ALLOCATE) {
        open_cfw_freertos_start_assert_failure();
    }

    (void)open_cfw_retained_freertos_idle_task_handle;
    (void)open_cfw_retained_freertos_top_used_priority;
}
