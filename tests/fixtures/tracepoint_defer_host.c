/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the EasyLogger tracepoint deferral state machine.
 */

typedef __UINTPTR_TYPE__ open_cfw_test_tracepoint_uintptr;

unsigned int open_cfw_test_tracepoint_should_defer;
unsigned int open_cfw_test_tracepoint_capture_result;
unsigned int open_cfw_test_tracepoint_event_result;
unsigned int open_cfw_test_tracepoint_timer_result;
void *open_cfw_test_tracepoint_timer_handle;
int open_cfw_test_tracepoint_retry_count;

unsigned int open_cfw_test_tracepoint_query_calls;
unsigned int open_cfw_test_tracepoint_event_calls;
unsigned int open_cfw_test_tracepoint_capture_calls;
unsigned int open_cfw_test_tracepoint_timer_calls;
unsigned int open_cfw_test_tracepoint_query_observed_retry_count;
unsigned int open_cfw_test_tracepoint_capture_observed_retry_count;
unsigned int open_cfw_test_tracepoint_timer_observed_retry_count;

open_cfw_test_tracepoint_uintptr
    open_cfw_test_tracepoint_timer_argument;
unsigned int open_cfw_test_tracepoint_timer_command;
unsigned int open_cfw_test_tracepoint_timer_value;
open_cfw_test_tracepoint_uintptr
    open_cfw_test_tracepoint_timer_woken_argument;
unsigned int open_cfw_test_tracepoint_timer_wait_ticks;

unsigned int open_cfw_test_tracepoint_trace[16];
unsigned int open_cfw_test_tracepoint_trace_count;

static void open_cfw_test_tracepoint_record(unsigned int event)
{
    open_cfw_test_tracepoint_trace[
        open_cfw_test_tracepoint_trace_count
    ] = event;
    open_cfw_test_tracepoint_trace_count += 1U;
}

static unsigned int open_cfw_test_tracepoint_query(void)
{
    open_cfw_test_tracepoint_query_calls += 1U;
    open_cfw_test_tracepoint_query_observed_retry_count =
        (unsigned int)open_cfw_test_tracepoint_retry_count;
    open_cfw_test_tracepoint_record(1U);
    return open_cfw_test_tracepoint_should_defer;
}

static unsigned int open_cfw_test_tracepoint_event_set(void)
{
    open_cfw_test_tracepoint_event_calls += 1U;
    open_cfw_test_tracepoint_record(2U);
    return open_cfw_test_tracepoint_event_result;
}

static unsigned int open_cfw_test_tracepoint_capture(void)
{
    open_cfw_test_tracepoint_capture_calls += 1U;
    open_cfw_test_tracepoint_capture_observed_retry_count =
        (unsigned int)open_cfw_test_tracepoint_retry_count;
    open_cfw_test_tracepoint_record(3U);
    return open_cfw_test_tracepoint_capture_result;
}

static unsigned int open_cfw_test_tracepoint_timer_command_call(
    void *timer,
    unsigned int command,
    unsigned int value,
    void *higher_priority_task_woken,
    unsigned int wait_ticks
)
{
    open_cfw_test_tracepoint_timer_calls += 1U;
    open_cfw_test_tracepoint_timer_argument =
        (open_cfw_test_tracepoint_uintptr)timer;
    open_cfw_test_tracepoint_timer_command = command;
    open_cfw_test_tracepoint_timer_value = value;
    open_cfw_test_tracepoint_timer_woken_argument =
        (open_cfw_test_tracepoint_uintptr)higher_priority_task_woken;
    open_cfw_test_tracepoint_timer_wait_ticks = wait_ticks;
    open_cfw_test_tracepoint_timer_observed_retry_count =
        (unsigned int)open_cfw_test_tracepoint_retry_count;
    open_cfw_test_tracepoint_record(4U);
    return open_cfw_test_tracepoint_timer_result;
}

#define OPEN_CFW_TRACEPOINT_SHOULD_DEFER() \
    open_cfw_test_tracepoint_query()
#define OPEN_CFW_TRACEPOINT_EVENT_SET() \
    open_cfw_test_tracepoint_event_set()
#define OPEN_CFW_TRACEPOINT_CAPTURE() \
    open_cfw_test_tracepoint_capture()
#define OPEN_CFW_TRACEPOINT_TIMER_COMMAND( \
    timer, command, value, higher_priority_task_woken, wait_ticks \
) \
    open_cfw_test_tracepoint_timer_command_call( \
        (timer), \
        (command), \
        (value), \
        (higher_priority_task_woken), \
        (wait_ticks) \
    )
#define OPEN_CFW_TRACEPOINT_TIMER_HANDLE \
    open_cfw_test_tracepoint_timer_handle
#define OPEN_CFW_TRACEPOINT_RETRY_COUNT \
    open_cfw_test_tracepoint_retry_count

#include "../../components/apollo_main/core_overlay/tracepoint_defer.c"
