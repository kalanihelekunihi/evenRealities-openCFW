/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

unsigned int open_cfw_test_rtos_timer_expire_events[16];
unsigned int open_cfw_test_rtos_timer_expire_event_count;
unsigned int open_cfw_test_rtos_timer_expire_timer_select_calls;
unsigned int open_cfw_test_rtos_timer_expire_remove_calls;
unsigned int open_cfw_test_rtos_timer_expire_remove_result;
unsigned int open_cfw_test_rtos_timer_expire_status_reads;
unsigned int open_cfw_test_rtos_timer_expire_status_writes;
unsigned int open_cfw_test_rtos_timer_expire_reload_calls;
unsigned int open_cfw_test_rtos_timer_expire_callback_calls;
unsigned int open_cfw_test_rtos_timer_expire_expired_time;
unsigned int open_cfw_test_rtos_timer_expire_time_now;
unsigned int open_cfw_test_rtos_timer_expire_status_mutate_after_read;
unsigned int open_cfw_test_rtos_timer_expire_mutated_status;
unsigned char open_cfw_test_rtos_timer_expire_status;
unsigned char open_cfw_test_rtos_timer_expire_written_status;
unsigned char open_cfw_test_rtos_timer_expire_callback_status;
unsigned char open_cfw_test_rtos_timer_expire_object[64];
void *open_cfw_test_rtos_timer_expire_selected_timer;
void *open_cfw_test_rtos_timer_expire_removed_item;
void *open_cfw_test_rtos_timer_expire_reload_timer;
void *open_cfw_test_rtos_timer_expire_callback_timer;

static void open_cfw_test_rtos_timer_expire_record(unsigned int event)
{
    open_cfw_test_rtos_timer_expire_events[
        open_cfw_test_rtos_timer_expire_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_expire_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_expire_event_count = 0U;
    open_cfw_test_rtos_timer_expire_timer_select_calls = 0U;
    open_cfw_test_rtos_timer_expire_remove_calls = 0U;
    open_cfw_test_rtos_timer_expire_remove_result = 0U;
    open_cfw_test_rtos_timer_expire_status_reads = 0U;
    open_cfw_test_rtos_timer_expire_status_writes = 0U;
    open_cfw_test_rtos_timer_expire_reload_calls = 0U;
    open_cfw_test_rtos_timer_expire_callback_calls = 0U;
    open_cfw_test_rtos_timer_expire_expired_time = 0U;
    open_cfw_test_rtos_timer_expire_time_now = 0U;
    open_cfw_test_rtos_timer_expire_status_mutate_after_read =
        0xFFFFFFFFU;
    open_cfw_test_rtos_timer_expire_mutated_status = 0U;
    open_cfw_test_rtos_timer_expire_status = 0U;
    open_cfw_test_rtos_timer_expire_written_status = 0U;
    open_cfw_test_rtos_timer_expire_callback_status = 0U;
    open_cfw_test_rtos_timer_expire_selected_timer =
        open_cfw_test_rtos_timer_expire_object;
    open_cfw_test_rtos_timer_expire_removed_item = (void *)0;
    open_cfw_test_rtos_timer_expire_reload_timer = (void *)0;
    open_cfw_test_rtos_timer_expire_callback_timer = (void *)0;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_expire_events[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_rtos_timer_expire_object[index] = 0U;
    }
}

static void *open_cfw_test_rtos_timer_expire_timer(void)
{
    open_cfw_test_rtos_timer_expire_record(10U);
    ++open_cfw_test_rtos_timer_expire_timer_select_calls;
    return open_cfw_test_rtos_timer_expire_selected_timer;
}

static unsigned int open_cfw_test_rtos_timer_expire_remove(void *item)
{
    open_cfw_test_rtos_timer_expire_record(20U);
    ++open_cfw_test_rtos_timer_expire_remove_calls;
    open_cfw_test_rtos_timer_expire_removed_item = item;
    return open_cfw_test_rtos_timer_expire_remove_result;
}

static unsigned int open_cfw_test_rtos_timer_expire_read_status(
    void *timer
)
{
    unsigned int read_index =
        open_cfw_test_rtos_timer_expire_status_reads;
    unsigned int value = open_cfw_test_rtos_timer_expire_status;

    (void)timer;
    open_cfw_test_rtos_timer_expire_record(30U);
    ++open_cfw_test_rtos_timer_expire_status_reads;
    if (
        read_index ==
        open_cfw_test_rtos_timer_expire_status_mutate_after_read
    ) {
        open_cfw_test_rtos_timer_expire_status =
            (unsigned char)open_cfw_test_rtos_timer_expire_mutated_status;
    }
    return value;
}

static void open_cfw_test_rtos_timer_expire_write_status(
    void *timer,
    unsigned int value
)
{
    (void)timer;
    open_cfw_test_rtos_timer_expire_record(50U);
    ++open_cfw_test_rtos_timer_expire_status_writes;
    open_cfw_test_rtos_timer_expire_written_status =
        (unsigned char)value;
    open_cfw_test_rtos_timer_expire_status = (unsigned char)value;
}

static void open_cfw_test_rtos_timer_expire_reload(
    void *timer,
    unsigned int expired_time,
    unsigned int time_now
)
{
    open_cfw_test_rtos_timer_expire_record(40U);
    ++open_cfw_test_rtos_timer_expire_reload_calls;
    open_cfw_test_rtos_timer_expire_reload_timer = timer;
    open_cfw_test_rtos_timer_expire_expired_time = expired_time;
    open_cfw_test_rtos_timer_expire_time_now = time_now;
}

static void open_cfw_test_rtos_timer_expire_callback(void *timer)
{
    open_cfw_test_rtos_timer_expire_record(60U);
    ++open_cfw_test_rtos_timer_expire_callback_calls;
    open_cfw_test_rtos_timer_expire_callback_timer = timer;
    open_cfw_test_rtos_timer_expire_callback_status =
        open_cfw_test_rtos_timer_expire_status;
}

#define OPEN_CFW_RTOS_TIMER_EXPIRE_TIMER() \
    open_cfw_test_rtos_timer_expire_timer()
#define OPEN_CFW_RTOS_TIMER_EXPIRE_REMOVE(item) \
    open_cfw_test_rtos_timer_expire_remove(item)
#define OPEN_CFW_RTOS_TIMER_EXPIRE_STATUS(timer) \
    open_cfw_test_rtos_timer_expire_read_status(timer)
#define OPEN_CFW_RTOS_TIMER_EXPIRE_WRITE_STATUS(timer, value) \
    open_cfw_test_rtos_timer_expire_write_status(timer, value)
#define OPEN_CFW_RTOS_TIMER_EXPIRE_RELOAD( \
    timer, expired_time, time_now \
) \
    open_cfw_test_rtos_timer_expire_reload( \
        timer, expired_time, time_now \
    )
#define OPEN_CFW_RTOS_TIMER_EXPIRE_CALLBACK(timer) \
    open_cfw_test_rtos_timer_expire_callback(timer)

#include "../../components/apollo_main/core_overlay/rtos_timer_expire.c"
