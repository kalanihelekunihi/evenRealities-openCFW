/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of xPortStartScheduler() from authenticated commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. Stock G2 body:
 * [0x004421E2,0x00442210). This candidate is not a production input.
 */

#include "runtime_freertos_port_start_scheduler.h"

enum {
    OPEN_CFW_FREERTOS_PORT_START_PENDSV_PRIORITY = 0x00FF0000U,
    OPEN_CFW_FREERTOS_PORT_START_SYSTICK_PRIORITY = 0xFF000000U,
};

extern void open_cfw_retained_freertos_timer_interrupt_setup(void);
extern void open_cfw_retained_freertos_start_first_task(void);
extern void open_cfw_retained_freertos_task_switch_context(void);
extern void open_cfw_retained_freertos_task_exit_error(void);

__attribute__((used, noinline))
open_cfw_freertos_port_start_base_type
open_cfw_freertos_port_start_scheduler(void)
{
    open_cfw_retained_freertos_system_handler_priority |=
        OPEN_CFW_FREERTOS_PORT_START_PENDSV_PRIORITY;
    open_cfw_retained_freertos_system_handler_priority |=
        OPEN_CFW_FREERTOS_PORT_START_SYSTICK_PRIORITY;

    open_cfw_retained_freertos_timer_interrupt_setup();
    open_cfw_retained_freertos_critical_nesting = 0U;
    open_cfw_retained_freertos_start_first_task();

    open_cfw_retained_freertos_task_switch_context();
    open_cfw_retained_freertos_task_exit_error();
    return 0;
}
