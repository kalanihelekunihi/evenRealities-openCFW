/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_port_start_scheduler.h"

volatile open_cfw_freertos_port_start_u32
    open_cfw_retained_freertos_system_handler_priority;
volatile open_cfw_freertos_port_start_u32
    open_cfw_retained_freertos_critical_nesting;

uint32_t open_cfw_test_freertos_port_start_events[8];
uint32_t open_cfw_test_freertos_port_start_event_count;
uint32_t open_cfw_test_freertos_port_start_timer_priority;
uint32_t open_cfw_test_freertos_port_start_first_task_priority;
uint32_t open_cfw_test_freertos_port_start_first_task_nesting;

static void open_cfw_test_freertos_port_start_note(uint32_t event)
{
    open_cfw_test_freertos_port_start_events[
        open_cfw_test_freertos_port_start_event_count++
    ] = event;
}

void open_cfw_retained_freertos_timer_interrupt_setup(void)
{
    open_cfw_test_freertos_port_start_note(1U);
    open_cfw_test_freertos_port_start_timer_priority =
        open_cfw_retained_freertos_system_handler_priority;
}

void open_cfw_retained_freertos_start_first_task(void)
{
    open_cfw_test_freertos_port_start_note(2U);
    open_cfw_test_freertos_port_start_first_task_priority =
        open_cfw_retained_freertos_system_handler_priority;
    open_cfw_test_freertos_port_start_first_task_nesting =
        open_cfw_retained_freertos_critical_nesting;
}

void open_cfw_retained_freertos_task_switch_context(void)
{
    open_cfw_test_freertos_port_start_note(3U);
}

void open_cfw_retained_freertos_task_exit_error(void)
{
    open_cfw_test_freertos_port_start_note(4U);
}

#include "../../components/shared/freertos/runtime_freertos_port_start_scheduler.c"

void open_cfw_test_freertos_port_start_reset(
    uint32_t priority,
    uint32_t nesting
)
{
    memset(open_cfw_test_freertos_port_start_events, 0,
           sizeof(open_cfw_test_freertos_port_start_events));
    open_cfw_test_freertos_port_start_event_count = 0U;
    open_cfw_retained_freertos_system_handler_priority = priority;
    open_cfw_retained_freertos_critical_nesting = nesting;
    open_cfw_test_freertos_port_start_timer_priority = 0U;
    open_cfw_test_freertos_port_start_first_task_priority = 0U;
    open_cfw_test_freertos_port_start_first_task_nesting = 0xFFFFFFFFU;
}
