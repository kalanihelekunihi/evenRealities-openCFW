/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

unsigned int open_cfw_test_rtos_timer_wait_or_expire_events[24];
unsigned int open_cfw_test_rtos_timer_wait_or_expire_event_count;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_suspend_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_sample_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_resume_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_expire_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_overflow_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_queue_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_wait_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_yield_calls;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_time_now;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_lists_switched;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_resume_result;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_overflow_empty;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_expired_time;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_expired_time_now;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_wait_delay;
unsigned int open_cfw_test_rtos_timer_wait_or_expire_wait_indefinitely;
void *open_cfw_test_rtos_timer_wait_or_expire_queue;
void *open_cfw_test_rtos_timer_wait_or_expire_wait_queue;

static void open_cfw_test_rtos_timer_wait_or_expire_record(
    unsigned int event
)
{
    open_cfw_test_rtos_timer_wait_or_expire_events[
        open_cfw_test_rtos_timer_wait_or_expire_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_wait_or_expire_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_wait_or_expire_event_count = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_suspend_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_sample_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_resume_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_expire_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_overflow_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_queue_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_wait_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_yield_calls = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_time_now = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_lists_switched = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_resume_result = 1U;
    open_cfw_test_rtos_timer_wait_or_expire_overflow_empty = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_expired_time = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_expired_time_now = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_wait_delay = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_wait_indefinitely = 0U;
    open_cfw_test_rtos_timer_wait_or_expire_queue =
        (void *)0x12345678U;
    open_cfw_test_rtos_timer_wait_or_expire_wait_queue = (void *)0;
    for (index = 0U; index < 24U; ++index) {
        open_cfw_test_rtos_timer_wait_or_expire_events[index] = 0U;
    }
}

static void open_cfw_test_rtos_timer_wait_or_expire_suspend(void)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(10U);
    ++open_cfw_test_rtos_timer_wait_or_expire_suspend_calls;
}

static unsigned int open_cfw_test_rtos_timer_wait_or_expire_sample(
    unsigned int *switched
)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(20U);
    ++open_cfw_test_rtos_timer_wait_or_expire_sample_calls;
    *switched =
        open_cfw_test_rtos_timer_wait_or_expire_lists_switched;
    return open_cfw_test_rtos_timer_wait_or_expire_time_now;
}

static unsigned int open_cfw_test_rtos_timer_wait_or_expire_resume(void)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(50U);
    ++open_cfw_test_rtos_timer_wait_or_expire_resume_calls;
    return open_cfw_test_rtos_timer_wait_or_expire_resume_result;
}

static void open_cfw_test_rtos_timer_wait_or_expire_expire(
    unsigned int expired_time,
    unsigned int time_now
)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(60U);
    ++open_cfw_test_rtos_timer_wait_or_expire_expire_calls;
    open_cfw_test_rtos_timer_wait_or_expire_expired_time =
        expired_time;
    open_cfw_test_rtos_timer_wait_or_expire_expired_time_now = time_now;
}

static unsigned int
open_cfw_test_rtos_timer_wait_or_expire_read_overflow(void)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(30U);
    ++open_cfw_test_rtos_timer_wait_or_expire_overflow_calls;
    return open_cfw_test_rtos_timer_wait_or_expire_overflow_empty;
}

static void *open_cfw_test_rtos_timer_wait_or_expire_read_queue(void)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(35U);
    ++open_cfw_test_rtos_timer_wait_or_expire_queue_calls;
    return open_cfw_test_rtos_timer_wait_or_expire_queue;
}

static void open_cfw_test_rtos_timer_wait_or_expire_wait(
    void *queue,
    unsigned int delay,
    unsigned int wait_indefinitely
)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(40U);
    ++open_cfw_test_rtos_timer_wait_or_expire_wait_calls;
    open_cfw_test_rtos_timer_wait_or_expire_wait_queue = queue;
    open_cfw_test_rtos_timer_wait_or_expire_wait_delay = delay;
    open_cfw_test_rtos_timer_wait_or_expire_wait_indefinitely =
        wait_indefinitely;
}

static void open_cfw_test_rtos_timer_wait_or_expire_yield(void)
{
    open_cfw_test_rtos_timer_wait_or_expire_record(70U);
    ++open_cfw_test_rtos_timer_wait_or_expire_yield_calls;
}

#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SUSPEND() \
    open_cfw_test_rtos_timer_wait_or_expire_suspend()
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_SAMPLE(switched) \
    open_cfw_test_rtos_timer_wait_or_expire_sample(switched)
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_RESUME() \
    open_cfw_test_rtos_timer_wait_or_expire_resume()
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_EXPIRE(expiry, time_now) \
    open_cfw_test_rtos_timer_wait_or_expire_expire(expiry, time_now)
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_OVERFLOW_EMPTY() \
    open_cfw_test_rtos_timer_wait_or_expire_read_overflow()
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_QUEUE() \
    open_cfw_test_rtos_timer_wait_or_expire_read_queue()
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_WAIT( \
    queue, delay, wait_indefinitely \
) \
    open_cfw_test_rtos_timer_wait_or_expire_wait( \
        queue, delay, wait_indefinitely \
    )
#define OPEN_CFW_RTOS_TIMER_WAIT_OR_EXPIRE_YIELD() \
    open_cfw_test_rtos_timer_wait_or_expire_yield()

#include "../../components/apollo_main/core_overlay/rtos_timer_wait_or_expire.c"
