/*
 * SPDX-License-Identifier: MIT
 */

unsigned int open_cfw_test_rtos_timer_is_active_events[8];
unsigned int open_cfw_test_rtos_timer_is_active_event_count;
unsigned int open_cfw_test_rtos_timer_is_active_event_depths[8];
unsigned int open_cfw_test_rtos_timer_is_active_critical_depth;
unsigned int open_cfw_test_rtos_timer_is_active_enter_calls;
unsigned int open_cfw_test_rtos_timer_is_active_exit_calls;
unsigned int open_cfw_test_rtos_timer_is_active_status_reads;
unsigned int open_cfw_test_rtos_timer_is_active_fail_stop_calls;
unsigned char open_cfw_test_rtos_timer_is_active_object[44];

static void open_cfw_test_rtos_timer_is_active_record(unsigned int event)
{
    unsigned int index = open_cfw_test_rtos_timer_is_active_event_count++;

    open_cfw_test_rtos_timer_is_active_events[index] = event;
    open_cfw_test_rtos_timer_is_active_event_depths[index] =
        open_cfw_test_rtos_timer_is_active_critical_depth;
}

void open_cfw_test_rtos_timer_is_active_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_is_active_event_count = 0U;
    open_cfw_test_rtos_timer_is_active_critical_depth = 0U;
    open_cfw_test_rtos_timer_is_active_enter_calls = 0U;
    open_cfw_test_rtos_timer_is_active_exit_calls = 0U;
    open_cfw_test_rtos_timer_is_active_status_reads = 0U;
    open_cfw_test_rtos_timer_is_active_fail_stop_calls = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_is_active_events[index] = 0U;
        open_cfw_test_rtos_timer_is_active_event_depths[index] = 0U;
    }
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_is_active_object[index] = 0xA5U;
    }
}

void open_cfw_test_rtos_timer_is_active_set_status(unsigned int value)
{
    open_cfw_test_rtos_timer_is_active_object[0x28U] =
        (unsigned char)value;
}

static void open_cfw_test_rtos_timer_is_active_enter(void)
{
    ++open_cfw_test_rtos_timer_is_active_critical_depth;
    ++open_cfw_test_rtos_timer_is_active_enter_calls;
    open_cfw_test_rtos_timer_is_active_record(10U);
}

static unsigned char open_cfw_test_rtos_timer_is_active_read_status(
    const void *timer
)
{
    open_cfw_test_rtos_timer_is_active_record(20U);
    ++open_cfw_test_rtos_timer_is_active_status_reads;
    return ((const unsigned char *)timer)[0x28U];
}

static void open_cfw_test_rtos_timer_is_active_exit(void)
{
    open_cfw_test_rtos_timer_is_active_record(30U);
    ++open_cfw_test_rtos_timer_is_active_exit_calls;
    --open_cfw_test_rtos_timer_is_active_critical_depth;
}

static void open_cfw_test_rtos_timer_is_active_fail_stop(void)
{
    open_cfw_test_rtos_timer_is_active_record(40U);
    ++open_cfw_test_rtos_timer_is_active_fail_stop_calls;
}

#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_ENTER_CRITICAL() \
    open_cfw_test_rtos_timer_is_active_enter()
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_EXIT_CRITICAL() \
    open_cfw_test_rtos_timer_is_active_exit()
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_READ_STATUS(timer) \
    open_cfw_test_rtos_timer_is_active_read_status(timer)
#define OPEN_CFW_RTOS_TIMER_IS_ACTIVE_FAIL_STOP() \
    open_cfw_test_rtos_timer_is_active_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_timer_is_active.c"
