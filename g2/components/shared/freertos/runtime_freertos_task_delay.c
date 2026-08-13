/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Bounded adaptation of vTaskDelay() from commit
 * def7d2df2b0506d3d249334974f51e427c17a41c. Stock G2 body:
 * [0x00454B4C,0x00454B88).
 */

#include "runtime_freertos_queue_receive.h"

__attribute__((used, noinline))
void open_cfw_freertos_task_delay(
    open_cfw_freertos_queue_next_tick_type ticks_to_delay
)
{
    open_cfw_freertos_queue_next_base_type already_yielded =
        OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE;

    if (ticks_to_delay > 0U) {
        OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(
            OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD() == 0U
        );
        open_cfw_freertos_task_suspend_all();
        open_cfw_freertos_task_add_current_to_delayed_list(
            ticks_to_delay,
            OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE
        );
        already_yielded = open_cfw_freertos_task_resume_all();
    }
    if (already_yielded == OPEN_CFW_FREERTOS_QUEUE_NEXT_FALSE) {
        open_cfw_freertos_port_yield();
    }
}
