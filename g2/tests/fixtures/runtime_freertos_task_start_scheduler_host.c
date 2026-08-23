/* SPDX-License-Identifier: MIT */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_task_start_scheduler.h"

open_cfw_freertos_start_task_handle volatile
    open_cfw_retained_freertos_idle_task_handle;
volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_next_task_unblock_time;
volatile open_cfw_freertos_start_base_type
    open_cfw_retained_freertos_scheduler_running;
volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_tick_count;
const volatile open_cfw_freertos_start_u32
    open_cfw_retained_freertos_top_used_priority = 55U;
const char open_cfw_retained_freertos_idle_task_name[] = "IDLE";

uint32_t open_cfw_test_freertos_start_events[16];
uint32_t open_cfw_test_freertos_start_event_count;
uint32_t open_cfw_test_freertos_start_create_succeeds;
int32_t open_cfw_test_freertos_start_timer_result;
uint32_t open_cfw_test_freertos_start_depth;
uintptr_t open_cfw_test_freertos_start_stack;
uintptr_t open_cfw_test_freertos_start_tcb;
uintptr_t open_cfw_test_freertos_start_created_entry;
const char *open_cfw_test_freertos_start_created_name;
uint32_t open_cfw_test_freertos_start_created_depth;
uintptr_t open_cfw_test_freertos_start_created_argument;
uint32_t open_cfw_test_freertos_start_created_priority;
uintptr_t open_cfw_test_freertos_start_created_stack;
uintptr_t open_cfw_test_freertos_start_created_tcb;
uint32_t open_cfw_test_freertos_start_port_next_unblock;
int32_t open_cfw_test_freertos_start_port_running;
uint32_t open_cfw_test_freertos_start_port_tick;

static void open_cfw_test_freertos_start_note(uint32_t event)
{
    open_cfw_test_freertos_start_events[
        open_cfw_test_freertos_start_event_count++
    ] = event;
}

void open_cfw_retained_freertos_idle_task_entry(void *argument)
{
    (void)argument;
}

void open_cfw_retained_freertos_idle_task_memory_get(
    void **task_control_block,
    open_cfw_freertos_start_u32 **stack,
    open_cfw_freertos_start_u32 *stack_depth
)
{
    open_cfw_test_freertos_start_note(1U);
    *task_control_block = (void *)open_cfw_test_freertos_start_tcb;
    *stack = (open_cfw_freertos_start_u32 *)open_cfw_test_freertos_start_stack;
    *stack_depth = open_cfw_test_freertos_start_depth;
}

open_cfw_freertos_start_task_handle
open_cfw_retained_freertos_task_create_static(
    open_cfw_freertos_start_task_function entry,
    const char *name,
    open_cfw_freertos_start_u32 stack_depth,
    void *argument,
    open_cfw_freertos_start_u32 priority,
    open_cfw_freertos_start_u32 *stack,
    void *task_control_block
)
{
    open_cfw_test_freertos_start_note(2U);
    open_cfw_test_freertos_start_created_entry = (uintptr_t)entry;
    open_cfw_test_freertos_start_created_name = name;
    open_cfw_test_freertos_start_created_depth = stack_depth;
    open_cfw_test_freertos_start_created_argument = (uintptr_t)argument;
    open_cfw_test_freertos_start_created_priority = priority;
    open_cfw_test_freertos_start_created_stack = (uintptr_t)stack;
    open_cfw_test_freertos_start_created_tcb = (uintptr_t)task_control_block;
    return open_cfw_test_freertos_start_create_succeeds != 0U
        ? (open_cfw_freertos_start_task_handle)(uintptr_t)0x33333333U
        : (open_cfw_freertos_start_task_handle)0;
}

open_cfw_freertos_start_base_type
open_cfw_retained_freertos_timer_task_create(void)
{
    open_cfw_test_freertos_start_note(3U);
    return open_cfw_test_freertos_start_timer_result;
}

open_cfw_freertos_start_u32
open_cfw_retained_freertos_interrupt_mask_set(void)
{
    open_cfw_test_freertos_start_note(4U);
    return 0xA5U;
}

open_cfw_freertos_start_base_type
open_cfw_freertos_port_start_scheduler(void)
{
    open_cfw_test_freertos_start_note(5U);
    open_cfw_test_freertos_start_port_next_unblock =
        open_cfw_retained_freertos_next_task_unblock_time;
    open_cfw_test_freertos_start_port_running =
        open_cfw_retained_freertos_scheduler_running;
    open_cfw_test_freertos_start_port_tick =
        open_cfw_retained_freertos_tick_count;
    return 0;
}

void open_cfw_freertos_start_assert_failure(void)
{
    open_cfw_test_freertos_start_note(6U);
}

#include "../../components/shared/freertos/runtime_freertos_task_start_scheduler.c"

void open_cfw_test_freertos_start_reset(
    uint32_t create_succeeds,
    int32_t timer_result
)
{
    memset(open_cfw_test_freertos_start_events, 0,
           sizeof(open_cfw_test_freertos_start_events));
    open_cfw_test_freertos_start_event_count = 0U;
    open_cfw_test_freertos_start_create_succeeds = create_succeeds;
    open_cfw_test_freertos_start_timer_result = timer_result;
    open_cfw_test_freertos_start_depth = 0x2468U;
    open_cfw_test_freertos_start_stack = (uintptr_t)0x11111110U;
    open_cfw_test_freertos_start_tcb = (uintptr_t)0x22222220U;
    open_cfw_test_freertos_start_created_entry = 0U;
    open_cfw_test_freertos_start_created_name = (const char *)0;
    open_cfw_test_freertos_start_created_depth = 0U;
    open_cfw_test_freertos_start_created_argument = 1U;
    open_cfw_test_freertos_start_created_priority = 99U;
    open_cfw_test_freertos_start_created_stack = 0U;
    open_cfw_test_freertos_start_created_tcb = 0U;
    open_cfw_test_freertos_start_port_next_unblock = 0U;
    open_cfw_test_freertos_start_port_running = 0;
    open_cfw_test_freertos_start_port_tick = 99U;
    open_cfw_retained_freertos_idle_task_handle =
        (open_cfw_freertos_start_task_handle)0;
    open_cfw_retained_freertos_next_task_unblock_time = 0x12345678U;
    open_cfw_retained_freertos_scheduler_running = 0;
    open_cfw_retained_freertos_tick_count = 0x87654321U;
}
