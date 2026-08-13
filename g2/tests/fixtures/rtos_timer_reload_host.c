/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

unsigned int open_cfw_test_rtos_timer_reload_events[48];
unsigned int open_cfw_test_rtos_timer_reload_event_count;
unsigned int open_cfw_test_rtos_timer_reload_period;
unsigned int open_cfw_test_rtos_timer_reload_period_reads;
unsigned int open_cfw_test_rtos_timer_reload_insert_calls;
unsigned int open_cfw_test_rtos_timer_reload_callback_calls;
unsigned int open_cfw_test_rtos_timer_reload_insert_results[16];
unsigned int open_cfw_test_rtos_timer_reload_insert_result_count;
unsigned int open_cfw_test_rtos_timer_reload_next_expiry[16];
unsigned int open_cfw_test_rtos_timer_reload_time_now[16];
unsigned int open_cfw_test_rtos_timer_reload_expired_time[16];
unsigned int open_cfw_test_rtos_timer_reload_insert_mutate_call;
unsigned int open_cfw_test_rtos_timer_reload_insert_period_value;
unsigned int open_cfw_test_rtos_timer_reload_callback_mutates_period;
unsigned int open_cfw_test_rtos_timer_reload_callback_period_value;
void *open_cfw_test_rtos_timer_reload_insert_timer[16];
void *open_cfw_test_rtos_timer_reload_callback_timer[16];

static void open_cfw_test_rtos_timer_reload_record(unsigned int event)
{
    open_cfw_test_rtos_timer_reload_events[
        open_cfw_test_rtos_timer_reload_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_reload_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_reload_event_count = 0U;
    open_cfw_test_rtos_timer_reload_period = 0U;
    open_cfw_test_rtos_timer_reload_period_reads = 0U;
    open_cfw_test_rtos_timer_reload_insert_calls = 0U;
    open_cfw_test_rtos_timer_reload_callback_calls = 0U;
    open_cfw_test_rtos_timer_reload_insert_result_count = 0U;
    open_cfw_test_rtos_timer_reload_insert_mutate_call = 0xFFFFFFFFU;
    open_cfw_test_rtos_timer_reload_insert_period_value = 0U;
    open_cfw_test_rtos_timer_reload_callback_mutates_period = 0U;
    open_cfw_test_rtos_timer_reload_callback_period_value = 0U;
    for (index = 0U; index < 48U; ++index) {
        open_cfw_test_rtos_timer_reload_events[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_reload_insert_results[index] = 0U;
        open_cfw_test_rtos_timer_reload_next_expiry[index] = 0U;
        open_cfw_test_rtos_timer_reload_time_now[index] = 0U;
        open_cfw_test_rtos_timer_reload_expired_time[index] = 0U;
        open_cfw_test_rtos_timer_reload_insert_timer[index] = (void *)0;
        open_cfw_test_rtos_timer_reload_callback_timer[index] = (void *)0;
    }
}

static unsigned int open_cfw_test_rtos_timer_reload_read_period(void *timer)
{
    (void)timer;
    open_cfw_test_rtos_timer_reload_record(10U);
    ++open_cfw_test_rtos_timer_reload_period_reads;
    return open_cfw_test_rtos_timer_reload_period;
}

static unsigned int open_cfw_test_rtos_timer_reload_insert(
    void *timer,
    unsigned int next_expiry,
    unsigned int time_now,
    unsigned int expired_time
)
{
    unsigned int index = open_cfw_test_rtos_timer_reload_insert_calls;
    unsigned int result = 0U;

    open_cfw_test_rtos_timer_reload_record(20U);
    open_cfw_test_rtos_timer_reload_insert_timer[index] = timer;
    open_cfw_test_rtos_timer_reload_next_expiry[index] = next_expiry;
    open_cfw_test_rtos_timer_reload_time_now[index] = time_now;
    open_cfw_test_rtos_timer_reload_expired_time[index] = expired_time;
    if (index < open_cfw_test_rtos_timer_reload_insert_result_count) {
        result = open_cfw_test_rtos_timer_reload_insert_results[index];
    }
    ++open_cfw_test_rtos_timer_reload_insert_calls;
    if (index == open_cfw_test_rtos_timer_reload_insert_mutate_call) {
        open_cfw_test_rtos_timer_reload_period =
            open_cfw_test_rtos_timer_reload_insert_period_value;
    }
    return result;
}

static void open_cfw_test_rtos_timer_reload_callback(void *timer)
{
    unsigned int index = open_cfw_test_rtos_timer_reload_callback_calls;

    open_cfw_test_rtos_timer_reload_record(30U);
    open_cfw_test_rtos_timer_reload_callback_timer[index] = timer;
    ++open_cfw_test_rtos_timer_reload_callback_calls;
    if (open_cfw_test_rtos_timer_reload_callback_mutates_period != 0U) {
        open_cfw_test_rtos_timer_reload_period =
            open_cfw_test_rtos_timer_reload_callback_period_value;
    }
}

#define OPEN_CFW_RTOS_TIMER_RELOAD_PERIOD(timer) \
    open_cfw_test_rtos_timer_reload_read_period(timer)
#define OPEN_CFW_RTOS_TIMER_RELOAD_INSERT( \
    timer, next_expiry, time_now, expired_time \
) \
    open_cfw_test_rtos_timer_reload_insert( \
        timer, next_expiry, time_now, expired_time \
    )
#define OPEN_CFW_RTOS_TIMER_RELOAD_CALLBACK(timer) \
    open_cfw_test_rtos_timer_reload_callback(timer)

#include "../../components/apollo_main/core_overlay/rtos_timer_reload.c"
