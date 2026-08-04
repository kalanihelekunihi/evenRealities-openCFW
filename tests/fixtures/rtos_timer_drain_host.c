/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

unsigned int open_cfw_test_rtos_timer_drain_events[256];
unsigned int open_cfw_test_rtos_timer_drain_event_count;
unsigned int open_cfw_test_rtos_timer_drain_messages[64];
unsigned int open_cfw_test_rtos_timer_drain_receive_results[17];
unsigned int open_cfw_test_rtos_timer_drain_message_count;
unsigned int open_cfw_test_rtos_timer_drain_queue_reads;
unsigned int open_cfw_test_rtos_timer_drain_receive_calls;
unsigned int open_cfw_test_rtos_timer_drain_queue_tag;
void *open_cfw_test_rtos_timer_drain_queue_values[17];
void *open_cfw_test_rtos_timer_drain_received_queues[17];
unsigned int open_cfw_test_rtos_timer_drain_receive_ticks[17];

unsigned int open_cfw_test_rtos_timer_drain_timer[11];
unsigned int open_cfw_test_rtos_timer_drain_timer_tokens[17];
unsigned int open_cfw_test_rtos_timer_drain_timer_maps;
unsigned int open_cfw_test_rtos_timer_drain_container_reads;
unsigned int open_cfw_test_rtos_timer_drain_remove_calls;
void *open_cfw_test_rtos_timer_drain_removed_items[17];

unsigned int open_cfw_test_rtos_timer_drain_sample_values[17];
unsigned int open_cfw_test_rtos_timer_drain_sample_switched[17];
unsigned int open_cfw_test_rtos_timer_drain_sample_calls;

unsigned int open_cfw_test_rtos_timer_drain_status_reads;
unsigned int open_cfw_test_rtos_timer_drain_status_writes;
unsigned int open_cfw_test_rtos_timer_drain_status_read_values[32];
unsigned int open_cfw_test_rtos_timer_drain_status_write_values[32];
unsigned int open_cfw_test_rtos_timer_drain_period_reads;
unsigned int open_cfw_test_rtos_timer_drain_period_writes;
unsigned int open_cfw_test_rtos_timer_drain_period_read_values[32];
unsigned int open_cfw_test_rtos_timer_drain_period_write_values[32];

unsigned int open_cfw_test_rtos_timer_drain_insert_calls;
unsigned int open_cfw_test_rtos_timer_drain_insert_results[17];
unsigned int open_cfw_test_rtos_timer_drain_insert_next_expiry[17];
unsigned int open_cfw_test_rtos_timer_drain_insert_time_now[17];
unsigned int open_cfw_test_rtos_timer_drain_insert_command_time[17];
void *open_cfw_test_rtos_timer_drain_insert_timers[17];
unsigned int open_cfw_test_rtos_timer_drain_insert_mutate_status_call;
unsigned int open_cfw_test_rtos_timer_drain_insert_status_value;
unsigned int open_cfw_test_rtos_timer_drain_insert_mutate_period_call;
unsigned int open_cfw_test_rtos_timer_drain_insert_period_value;

unsigned int open_cfw_test_rtos_timer_drain_reload_calls;
unsigned int open_cfw_test_rtos_timer_drain_reload_next_expiry[17];
unsigned int open_cfw_test_rtos_timer_drain_reload_time_now[17];
void *open_cfw_test_rtos_timer_drain_reload_timers[17];
unsigned int open_cfw_test_rtos_timer_drain_callback_calls;
void *open_cfw_test_rtos_timer_drain_callback_timers[17];
unsigned int open_cfw_test_rtos_timer_drain_free_calls;
void *open_cfw_test_rtos_timer_drain_free_timers[17];
unsigned int open_cfw_test_rtos_timer_drain_fail_stop_calls;

unsigned int open_cfw_test_rtos_timer_drain_pended_calls;
unsigned int open_cfw_test_rtos_timer_drain_pended_functions[17];
unsigned int open_cfw_test_rtos_timer_drain_pended_parameter_one[17];
unsigned int open_cfw_test_rtos_timer_drain_pended_parameter_two[17];

static void open_cfw_test_rtos_timer_drain_record(unsigned int event)
{
    open_cfw_test_rtos_timer_drain_events[
        open_cfw_test_rtos_timer_drain_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_drain_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_drain_event_count = 0U;
    open_cfw_test_rtos_timer_drain_message_count = 0U;
    open_cfw_test_rtos_timer_drain_queue_reads = 0U;
    open_cfw_test_rtos_timer_drain_receive_calls = 0U;
    open_cfw_test_rtos_timer_drain_timer_maps = 0U;
    open_cfw_test_rtos_timer_drain_container_reads = 0U;
    open_cfw_test_rtos_timer_drain_remove_calls = 0U;
    open_cfw_test_rtos_timer_drain_sample_calls = 0U;
    open_cfw_test_rtos_timer_drain_status_reads = 0U;
    open_cfw_test_rtos_timer_drain_status_writes = 0U;
    open_cfw_test_rtos_timer_drain_period_reads = 0U;
    open_cfw_test_rtos_timer_drain_period_writes = 0U;
    open_cfw_test_rtos_timer_drain_insert_calls = 0U;
    open_cfw_test_rtos_timer_drain_reload_calls = 0U;
    open_cfw_test_rtos_timer_drain_callback_calls = 0U;
    open_cfw_test_rtos_timer_drain_free_calls = 0U;
    open_cfw_test_rtos_timer_drain_fail_stop_calls = 0U;
    open_cfw_test_rtos_timer_drain_pended_calls = 0U;
    open_cfw_test_rtos_timer_drain_insert_mutate_status_call =
        0xFFFFFFFFU;
    open_cfw_test_rtos_timer_drain_insert_status_value = 0U;
    open_cfw_test_rtos_timer_drain_insert_mutate_period_call =
        0xFFFFFFFFU;
    open_cfw_test_rtos_timer_drain_insert_period_value = 0U;

    for (index = 0U; index < 256U; ++index) {
        open_cfw_test_rtos_timer_drain_events[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_rtos_timer_drain_messages[index] = 0U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_rtos_timer_drain_status_read_values[index] = 0U;
        open_cfw_test_rtos_timer_drain_status_write_values[index] = 0U;
        open_cfw_test_rtos_timer_drain_period_read_values[index] = 0U;
        open_cfw_test_rtos_timer_drain_period_write_values[index] = 0U;
    }
    for (index = 0U; index < 17U; ++index) {
        open_cfw_test_rtos_timer_drain_receive_results[index] = 0U;
        open_cfw_test_rtos_timer_drain_queue_values[index] =
            &open_cfw_test_rtos_timer_drain_queue_tag;
        open_cfw_test_rtos_timer_drain_received_queues[index] =
            (void *)0;
        open_cfw_test_rtos_timer_drain_receive_ticks[index] = 0U;
        open_cfw_test_rtos_timer_drain_timer_tokens[index] = 0U;
        open_cfw_test_rtos_timer_drain_removed_items[index] = (void *)0;
        open_cfw_test_rtos_timer_drain_sample_values[index] = 0U;
        open_cfw_test_rtos_timer_drain_sample_switched[index] = 0U;
        open_cfw_test_rtos_timer_drain_insert_results[index] = 0U;
        open_cfw_test_rtos_timer_drain_insert_next_expiry[index] = 0U;
        open_cfw_test_rtos_timer_drain_insert_time_now[index] = 0U;
        open_cfw_test_rtos_timer_drain_insert_command_time[index] = 0U;
        open_cfw_test_rtos_timer_drain_insert_timers[index] = (void *)0;
        open_cfw_test_rtos_timer_drain_reload_next_expiry[index] = 0U;
        open_cfw_test_rtos_timer_drain_reload_time_now[index] = 0U;
        open_cfw_test_rtos_timer_drain_reload_timers[index] = (void *)0;
        open_cfw_test_rtos_timer_drain_callback_timers[index] = (void *)0;
        open_cfw_test_rtos_timer_drain_free_timers[index] = (void *)0;
        open_cfw_test_rtos_timer_drain_pended_functions[index] = 0U;
        open_cfw_test_rtos_timer_drain_pended_parameter_one[index] = 0U;
        open_cfw_test_rtos_timer_drain_pended_parameter_two[index] = 0U;
    }
    for (index = 0U; index < 11U; ++index) {
        open_cfw_test_rtos_timer_drain_timer[index] = 0U;
    }
}

static void *open_cfw_test_rtos_timer_drain_queue(void)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_queue_reads;

    open_cfw_test_rtos_timer_drain_record(10U);
    ++open_cfw_test_rtos_timer_drain_queue_reads;
    return open_cfw_test_rtos_timer_drain_queue_values[index];
}

static unsigned int open_cfw_test_rtos_timer_drain_receive(
    void *queue,
    void *message,
    unsigned int ticks
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_receive_calls;
    unsigned int result =
        open_cfw_test_rtos_timer_drain_receive_results[index];
    unsigned int *words = (unsigned int *)message;

    open_cfw_test_rtos_timer_drain_record(20U);
    open_cfw_test_rtos_timer_drain_received_queues[index] = queue;
    open_cfw_test_rtos_timer_drain_receive_ticks[index] = ticks;
    if (result != 0U && index < open_cfw_test_rtos_timer_drain_message_count) {
        words[0] = open_cfw_test_rtos_timer_drain_messages[index * 4U];
        words[1] =
            open_cfw_test_rtos_timer_drain_messages[index * 4U + 1U];
        words[2] =
            open_cfw_test_rtos_timer_drain_messages[index * 4U + 2U];
        words[3] =
            open_cfw_test_rtos_timer_drain_messages[index * 4U + 3U];
    }
    ++open_cfw_test_rtos_timer_drain_receive_calls;
    return result;
}

static void open_cfw_test_rtos_timer_drain_pended_call(
    unsigned int function,
    unsigned int parameter_one,
    unsigned int parameter_two
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_pended_calls;

    open_cfw_test_rtos_timer_drain_record(30U);
    open_cfw_test_rtos_timer_drain_pended_functions[index] = function;
    open_cfw_test_rtos_timer_drain_pended_parameter_one[index] =
        parameter_one;
    open_cfw_test_rtos_timer_drain_pended_parameter_two[index] =
        parameter_two;
    ++open_cfw_test_rtos_timer_drain_pended_calls;
}

static void *open_cfw_test_rtos_timer_drain_timer_from_token(
    unsigned int token
)
{
    open_cfw_test_rtos_timer_drain_timer_tokens[
        open_cfw_test_rtos_timer_drain_timer_maps++
    ] = token;
    return open_cfw_test_rtos_timer_drain_timer;
}

static unsigned int open_cfw_test_rtos_timer_drain_container(void *timer)
{
    open_cfw_test_rtos_timer_drain_record(40U);
    ++open_cfw_test_rtos_timer_drain_container_reads;
    return *(unsigned int *)((unsigned char *)timer + 0x14U);
}

static unsigned int open_cfw_test_rtos_timer_drain_remove(void *item)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_remove_calls;

    open_cfw_test_rtos_timer_drain_record(50U);
    open_cfw_test_rtos_timer_drain_removed_items[index] = item;
    ++open_cfw_test_rtos_timer_drain_remove_calls;
    return 0xFFFFFFFFU;
}

static unsigned int open_cfw_test_rtos_timer_drain_sample(
    unsigned int *switched
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_sample_calls;

    open_cfw_test_rtos_timer_drain_record(60U);
    *switched =
        open_cfw_test_rtos_timer_drain_sample_switched[index];
    ++open_cfw_test_rtos_timer_drain_sample_calls;
    return open_cfw_test_rtos_timer_drain_sample_values[index];
}

static unsigned int open_cfw_test_rtos_timer_drain_read_status(void *timer)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_status_reads;
    unsigned int value =
        *(unsigned char *)((unsigned char *)timer + 0x28U);

    open_cfw_test_rtos_timer_drain_record(70U);
    open_cfw_test_rtos_timer_drain_status_read_values[index] = value;
    ++open_cfw_test_rtos_timer_drain_status_reads;
    return value;
}

static void open_cfw_test_rtos_timer_drain_write_status(
    void *timer,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_status_writes;

    open_cfw_test_rtos_timer_drain_record(80U);
    *(unsigned char *)((unsigned char *)timer + 0x28U) =
        (unsigned char)value;
    open_cfw_test_rtos_timer_drain_status_write_values[index] =
        value & 0xFFU;
    ++open_cfw_test_rtos_timer_drain_status_writes;
}

static unsigned int open_cfw_test_rtos_timer_drain_read_period(void *timer)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_period_reads;
    unsigned int value =
        *(unsigned int *)((unsigned char *)timer + 0x18U);

    open_cfw_test_rtos_timer_drain_record(90U);
    open_cfw_test_rtos_timer_drain_period_read_values[index] = value;
    ++open_cfw_test_rtos_timer_drain_period_reads;
    return value;
}

static void open_cfw_test_rtos_timer_drain_write_period(
    void *timer,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_period_writes;

    open_cfw_test_rtos_timer_drain_record(100U);
    *(unsigned int *)((unsigned char *)timer + 0x18U) = value;
    open_cfw_test_rtos_timer_drain_period_write_values[index] = value;
    ++open_cfw_test_rtos_timer_drain_period_writes;
}

static unsigned int open_cfw_test_rtos_timer_drain_insert(
    void *timer,
    unsigned int next_expiry,
    unsigned int time_now,
    unsigned int command_time
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_insert_calls;

    open_cfw_test_rtos_timer_drain_record(110U);
    open_cfw_test_rtos_timer_drain_insert_timers[index] = timer;
    open_cfw_test_rtos_timer_drain_insert_next_expiry[index] =
        next_expiry;
    open_cfw_test_rtos_timer_drain_insert_time_now[index] = time_now;
    open_cfw_test_rtos_timer_drain_insert_command_time[index] =
        command_time;
    ++open_cfw_test_rtos_timer_drain_insert_calls;
    if (
        index
        == open_cfw_test_rtos_timer_drain_insert_mutate_status_call
    ) {
        *(unsigned char *)((unsigned char *)timer + 0x28U) =
            (unsigned char)
                open_cfw_test_rtos_timer_drain_insert_status_value;
    }
    if (
        index
        == open_cfw_test_rtos_timer_drain_insert_mutate_period_call
    ) {
        *(unsigned int *)((unsigned char *)timer + 0x18U) =
            open_cfw_test_rtos_timer_drain_insert_period_value;
    }
    return open_cfw_test_rtos_timer_drain_insert_results[index];
}

static void open_cfw_test_rtos_timer_drain_reload(
    void *timer,
    unsigned int next_expiry,
    unsigned int time_now
)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_reload_calls;

    open_cfw_test_rtos_timer_drain_record(120U);
    open_cfw_test_rtos_timer_drain_reload_timers[index] = timer;
    open_cfw_test_rtos_timer_drain_reload_next_expiry[index] =
        next_expiry;
    open_cfw_test_rtos_timer_drain_reload_time_now[index] = time_now;
    ++open_cfw_test_rtos_timer_drain_reload_calls;
}

static void open_cfw_test_rtos_timer_drain_callback(void *timer)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_callback_calls;

    open_cfw_test_rtos_timer_drain_record(130U);
    open_cfw_test_rtos_timer_drain_callback_timers[index] = timer;
    ++open_cfw_test_rtos_timer_drain_callback_calls;
}

static void open_cfw_test_rtos_timer_drain_free(void *timer)
{
    unsigned int index = open_cfw_test_rtos_timer_drain_free_calls;

    open_cfw_test_rtos_timer_drain_record(140U);
    open_cfw_test_rtos_timer_drain_free_timers[index] = timer;
    ++open_cfw_test_rtos_timer_drain_free_calls;
}

static void open_cfw_test_rtos_timer_drain_fail_stop(void)
{
    open_cfw_test_rtos_timer_drain_record(150U);
    ++open_cfw_test_rtos_timer_drain_fail_stop_calls;
}

#define OPEN_CFW_RTOS_TIMER_DRAIN_QUEUE() \
    open_cfw_test_rtos_timer_drain_queue()
#define OPEN_CFW_RTOS_TIMER_DRAIN_RECEIVE(queue, message, ticks) \
    open_cfw_test_rtos_timer_drain_receive(queue, message, ticks)
#define OPEN_CFW_RTOS_TIMER_DRAIN_PENDED_CALL( \
    function, parameter_one, parameter_two \
) \
    open_cfw_test_rtos_timer_drain_pended_call( \
        function, parameter_one, parameter_two \
    )
#define OPEN_CFW_RTOS_TIMER_DRAIN_TIMER(value) \
    open_cfw_test_rtos_timer_drain_timer_from_token(value)
#define OPEN_CFW_RTOS_TIMER_DRAIN_LIST_CONTAINER(timer) \
    open_cfw_test_rtos_timer_drain_container(timer)
#define OPEN_CFW_RTOS_TIMER_DRAIN_LIST_ITEM(timer) \
    ((void *)((unsigned char *)(timer) + 0x04U))
#define OPEN_CFW_RTOS_TIMER_DRAIN_REMOVE(item) \
    open_cfw_test_rtos_timer_drain_remove(item)
#define OPEN_CFW_RTOS_TIMER_DRAIN_SAMPLE(switched) \
    open_cfw_test_rtos_timer_drain_sample(switched)
#define OPEN_CFW_RTOS_TIMER_DRAIN_READ_STATUS(timer) \
    open_cfw_test_rtos_timer_drain_read_status(timer)
#define OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_STATUS(timer, value) \
    open_cfw_test_rtos_timer_drain_write_status(timer, value)
#define OPEN_CFW_RTOS_TIMER_DRAIN_READ_PERIOD(timer) \
    open_cfw_test_rtos_timer_drain_read_period(timer)
#define OPEN_CFW_RTOS_TIMER_DRAIN_WRITE_PERIOD(timer, value) \
    open_cfw_test_rtos_timer_drain_write_period(timer, value)
#define OPEN_CFW_RTOS_TIMER_DRAIN_INSERT( \
    timer, next_expiry, time_now, command_time \
) \
    open_cfw_test_rtos_timer_drain_insert( \
        timer, next_expiry, time_now, command_time \
    )
#define OPEN_CFW_RTOS_TIMER_DRAIN_RELOAD( \
    timer, next_expiry, time_now \
) \
    open_cfw_test_rtos_timer_drain_reload(timer, next_expiry, time_now)
#define OPEN_CFW_RTOS_TIMER_DRAIN_CALLBACK(timer) \
    open_cfw_test_rtos_timer_drain_callback(timer)
#define OPEN_CFW_RTOS_TIMER_DRAIN_FREE(timer) \
    open_cfw_test_rtos_timer_drain_free(timer)
#define OPEN_CFW_RTOS_TIMER_DRAIN_FAIL_STOP() \
    do { \
        open_cfw_test_rtos_timer_drain_fail_stop(); \
        return; \
    } while (0)

#include "../../components/apollo_main/core_overlay/rtos_timer_drain.c"

void open_cfw_test_rtos_timer_drain_run(void)
{
    open_cfw_rtos_timer_drain();
}

unsigned int open_cfw_test_rtos_timer_drain_message_size(void)
{
    return (unsigned int)
        sizeof(struct open_cfw_rtos_timer_drain_message);
}

unsigned int open_cfw_test_rtos_timer_drain_timer_offset(void)
{
    return (unsigned int)__builtin_offsetof(
        struct open_cfw_rtos_timer_drain_message,
        payload.timer.timer
    );
}

unsigned int open_cfw_test_rtos_timer_drain_parameter_two_offset(void)
{
    return (unsigned int)__builtin_offsetof(
        struct open_cfw_rtos_timer_drain_message,
        payload.callback.parameter_two
    );
}
