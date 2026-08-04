/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_get_context_uintptr;

unsigned int open_cfw_test_rtos_timer_get_context_events[8];
unsigned int open_cfw_test_rtos_timer_get_context_event_count;
unsigned int open_cfw_test_rtos_timer_get_context_event_depths[8];
unsigned int open_cfw_test_rtos_timer_get_context_critical_depth;
unsigned int open_cfw_test_rtos_timer_get_context_enter_calls;
unsigned int open_cfw_test_rtos_timer_get_context_exit_calls;
unsigned int open_cfw_test_rtos_timer_get_context_context_reads;
unsigned int open_cfw_test_rtos_timer_get_context_fail_stop_calls;
open_cfw_test_rtos_timer_get_context_uintptr
    open_cfw_test_rtos_timer_get_context_read_result;
open_cfw_test_rtos_timer_get_context_uintptr
    open_cfw_test_rtos_timer_get_context_last_timer;
unsigned char open_cfw_test_rtos_timer_get_context_object[44];

static void open_cfw_test_rtos_timer_get_context_record(unsigned int event)
{
    unsigned int index = open_cfw_test_rtos_timer_get_context_event_count++;

    open_cfw_test_rtos_timer_get_context_events[index] = event;
    open_cfw_test_rtos_timer_get_context_event_depths[index] =
        open_cfw_test_rtos_timer_get_context_critical_depth;
}

void open_cfw_test_rtos_timer_get_context_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_get_context_event_count = 0U;
    open_cfw_test_rtos_timer_get_context_critical_depth = 0U;
    open_cfw_test_rtos_timer_get_context_enter_calls = 0U;
    open_cfw_test_rtos_timer_get_context_exit_calls = 0U;
    open_cfw_test_rtos_timer_get_context_context_reads = 0U;
    open_cfw_test_rtos_timer_get_context_fail_stop_calls = 0U;
    open_cfw_test_rtos_timer_get_context_read_result = 0U;
    open_cfw_test_rtos_timer_get_context_last_timer = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_get_context_events[index] = 0U;
        open_cfw_test_rtos_timer_get_context_event_depths[index] = 0U;
    }
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_get_context_object[index] = 0xA5U;
    }
}

void open_cfw_test_rtos_timer_get_context_set_result(
    open_cfw_test_rtos_timer_get_context_uintptr value
)
{
    open_cfw_test_rtos_timer_get_context_read_result = value;
}

static void open_cfw_test_rtos_timer_get_context_enter(void)
{
    ++open_cfw_test_rtos_timer_get_context_critical_depth;
    ++open_cfw_test_rtos_timer_get_context_enter_calls;
    open_cfw_test_rtos_timer_get_context_record(10U);
}

static void *open_cfw_test_rtos_timer_get_context_read_context(
    const void *timer
)
{
    open_cfw_test_rtos_timer_get_context_record(20U);
    ++open_cfw_test_rtos_timer_get_context_context_reads;
    open_cfw_test_rtos_timer_get_context_last_timer =
        (open_cfw_test_rtos_timer_get_context_uintptr)timer;
    return (void *)open_cfw_test_rtos_timer_get_context_read_result;
}

static void open_cfw_test_rtos_timer_get_context_exit(void)
{
    open_cfw_test_rtos_timer_get_context_record(30U);
    ++open_cfw_test_rtos_timer_get_context_exit_calls;
    --open_cfw_test_rtos_timer_get_context_critical_depth;
}

static void open_cfw_test_rtos_timer_get_context_fail_stop(void)
{
    open_cfw_test_rtos_timer_get_context_record(40U);
    ++open_cfw_test_rtos_timer_get_context_fail_stop_calls;
}

#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_ENTER_CRITICAL() \
    open_cfw_test_rtos_timer_get_context_enter()
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_EXIT_CRITICAL() \
    open_cfw_test_rtos_timer_get_context_exit()
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_READ_CONTEXT(timer) \
    open_cfw_test_rtos_timer_get_context_read_context(timer)
#define OPEN_CFW_RTOS_TIMER_GET_CONTEXT_FAIL_STOP() \
    open_cfw_test_rtos_timer_get_context_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_timer_get_context.c"
