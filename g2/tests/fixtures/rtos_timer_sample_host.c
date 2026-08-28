/*
 * SPDX-License-Identifier: MIT
 */

unsigned int open_cfw_test_rtos_timer_sample_events[16];
unsigned int open_cfw_test_rtos_timer_sample_event_count;
unsigned int open_cfw_test_rtos_timer_sample_time_now;
unsigned int open_cfw_test_rtos_timer_sample_last_tick;
unsigned int open_cfw_test_rtos_timer_sample_tick_reads;
unsigned int open_cfw_test_rtos_timer_sample_last_tick_reads;
unsigned int open_cfw_test_rtos_timer_sample_last_tick_writes;
unsigned int open_cfw_test_rtos_timer_sample_switch_calls;

static void open_cfw_test_rtos_timer_sample_record(unsigned int event)
{
    open_cfw_test_rtos_timer_sample_events[
        open_cfw_test_rtos_timer_sample_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_sample_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_sample_event_count = 0U;
    open_cfw_test_rtos_timer_sample_time_now = 0U;
    open_cfw_test_rtos_timer_sample_last_tick = 0U;
    open_cfw_test_rtos_timer_sample_tick_reads = 0U;
    open_cfw_test_rtos_timer_sample_last_tick_reads = 0U;
    open_cfw_test_rtos_timer_sample_last_tick_writes = 0U;
    open_cfw_test_rtos_timer_sample_switch_calls = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_sample_events[index] = 0U;
    }
}

static unsigned int open_cfw_test_rtos_timer_sample_read_tick(void)
{
    open_cfw_test_rtos_timer_sample_record(10U);
    ++open_cfw_test_rtos_timer_sample_tick_reads;
    return open_cfw_test_rtos_timer_sample_time_now;
}

static unsigned int open_cfw_test_rtos_timer_sample_read_last_tick(void)
{
    open_cfw_test_rtos_timer_sample_record(20U);
    ++open_cfw_test_rtos_timer_sample_last_tick_reads;
    return open_cfw_test_rtos_timer_sample_last_tick;
}

static void open_cfw_test_rtos_timer_sample_write_last_tick(
    unsigned int value
)
{
    open_cfw_test_rtos_timer_sample_record(40U);
    ++open_cfw_test_rtos_timer_sample_last_tick_writes;
    open_cfw_test_rtos_timer_sample_last_tick = value;
}

static void open_cfw_test_rtos_timer_sample_switch_lists(void)
{
    open_cfw_test_rtos_timer_sample_record(30U);
    ++open_cfw_test_rtos_timer_sample_switch_calls;
}

#define OPEN_CFW_RTOS_TIMER_SAMPLE_TICK() \
    open_cfw_test_rtos_timer_sample_read_tick()
#define OPEN_CFW_RTOS_TIMER_SAMPLE_READ_LAST_TICK() \
    open_cfw_test_rtos_timer_sample_read_last_tick()
#define OPEN_CFW_RTOS_TIMER_SAMPLE_WRITE_LAST_TICK(value) \
    open_cfw_test_rtos_timer_sample_write_last_tick(value)
#define OPEN_CFW_RTOS_TIMER_SAMPLE_SWITCH_LISTS() \
    open_cfw_test_rtos_timer_sample_switch_lists()

#include "../../components/apollo_main/core_overlay/rtos_timer_sample.c"

unsigned int open_cfw_test_rtos_timer_sample_run(
    unsigned int *lists_switched
)
{
    return open_cfw_rtos_timer_sample(lists_switched);
}
