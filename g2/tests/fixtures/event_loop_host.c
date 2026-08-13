/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the bounded CMSIS event-loop cluster.
 */

#include <stdarg.h>

unsigned int open_cfw_test_event_loop_log_level(void);
void open_cfw_test_event_loop_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_event_loop_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void *open_cfw_test_event_loop_queue_create(
    unsigned int,
    unsigned int,
    const void *
);
void *open_cfw_test_event_loop_timer_create(
    void (*)(unsigned int),
    unsigned int,
    unsigned int,
    const void *
);
void *open_cfw_test_event_loop_mutex_create(const void *);
void *open_cfw_test_event_loop_thread_create(
    void (*)(void *),
    void *,
    const void *
);
unsigned int open_cfw_test_event_loop_thread_terminate(void *);
unsigned int open_cfw_test_event_loop_queue_get(
    void *,
    void *,
    unsigned char *,
    unsigned int
);
unsigned int open_cfw_test_event_loop_queue_put(
    void *,
    const void *,
    unsigned char,
    unsigned int
);
unsigned int open_cfw_test_event_loop_mutex_acquire(
    void *,
    unsigned int
);
unsigned int open_cfw_test_event_loop_mutex_release(void *);
unsigned int open_cfw_test_event_loop_timer_start(void *, unsigned int);
unsigned int open_cfw_test_event_loop_timer_stop(void *);
void open_cfw_test_event_loop_critical_enter(void);
void open_cfw_test_event_loop_critical_exit(void);
void open_cfw_test_event_loop_delay(unsigned int);
unsigned int open_cfw_test_event_loop_tick(void);
int open_cfw_test_event_loop_task_continue(void);

void *open_cfw_test_event_loop_queue_handle;
void *open_cfw_test_event_loop_thread_handle;
void *open_cfw_test_event_loop_mutex_handle;
void *open_cfw_test_event_loop_timer_handle;
unsigned int open_cfw_test_event_loop_last_tick;
unsigned int open_cfw_test_event_loop_next_delay;
void (*open_cfw_test_event_loop_callbacks[64])(void *);
void *open_cfw_test_event_loop_arguments[64];
unsigned int open_cfw_test_event_loop_delays[64];

#define OPEN_CFW_EVENT_LOOP_QUEUE_HANDLE \
    open_cfw_test_event_loop_queue_handle
#define OPEN_CFW_EVENT_LOOP_THREAD_HANDLE \
    open_cfw_test_event_loop_thread_handle
#define OPEN_CFW_EVENT_LOOP_MUTEX_HANDLE \
    open_cfw_test_event_loop_mutex_handle
#define OPEN_CFW_EVENT_LOOP_TIMER_HANDLE \
    open_cfw_test_event_loop_timer_handle
#define OPEN_CFW_EVENT_LOOP_LAST_TICK open_cfw_test_event_loop_last_tick
#define OPEN_CFW_EVENT_LOOP_NEXT_DELAY open_cfw_test_event_loop_next_delay
#define OPEN_CFW_EVENT_LOOP_CALLBACKS open_cfw_test_event_loop_callbacks
#define OPEN_CFW_EVENT_LOOP_ARGUMENTS open_cfw_test_event_loop_arguments
#define OPEN_CFW_EVENT_LOOP_DELAYS open_cfw_test_event_loop_delays
#define OPEN_CFW_EVENT_LOOP_LOG_LEVEL() \
    open_cfw_test_event_loop_log_level()
#define OPEN_CFW_EVENT_LOOP_LOG(...) \
    open_cfw_test_event_loop_log(__VA_ARGS__)
#define OPEN_CFW_EVENT_LOOP_TRACE(...) \
    open_cfw_test_event_loop_trace(__VA_ARGS__)
#define OPEN_CFW_EVENT_LOOP_QUEUE_CREATE(count, size, attributes) \
    open_cfw_test_event_loop_queue_create((count), (size), (attributes))
#define OPEN_CFW_EVENT_LOOP_TIMER_CREATE(callback, type, argument, attributes) \
    open_cfw_test_event_loop_timer_create( \
        (callback), (type), (argument), (attributes) \
    )
#define OPEN_CFW_EVENT_LOOP_MUTEX_CREATE(attributes) \
    open_cfw_test_event_loop_mutex_create(attributes)
#define OPEN_CFW_EVENT_LOOP_THREAD_CREATE(entry, argument, attributes) \
    open_cfw_test_event_loop_thread_create((entry), (argument), (attributes))
#define OPEN_CFW_EVENT_LOOP_THREAD_TERMINATE(handle) \
    open_cfw_test_event_loop_thread_terminate(handle)
#define OPEN_CFW_EVENT_LOOP_QUEUE_GET(queue, event, priority, timeout) \
    open_cfw_test_event_loop_queue_get( \
        (queue), (event), (priority), (timeout) \
    )
#define OPEN_CFW_EVENT_LOOP_QUEUE_PUT(queue, event, priority, timeout) \
    open_cfw_test_event_loop_queue_put( \
        (queue), (event), (priority), (timeout) \
    )
#define OPEN_CFW_EVENT_LOOP_MUTEX_ACQUIRE(handle, timeout) \
    open_cfw_test_event_loop_mutex_acquire((handle), (timeout))
#define OPEN_CFW_EVENT_LOOP_MUTEX_RELEASE(handle) \
    open_cfw_test_event_loop_mutex_release(handle)
#define OPEN_CFW_EVENT_LOOP_TIMER_START(handle, ticks) \
    open_cfw_test_event_loop_timer_start((handle), (ticks))
#define OPEN_CFW_EVENT_LOOP_TIMER_STOP(handle) \
    open_cfw_test_event_loop_timer_stop(handle)
#define OPEN_CFW_EVENT_LOOP_CRITICAL_ENTER() \
    open_cfw_test_event_loop_critical_enter()
#define OPEN_CFW_EVENT_LOOP_CRITICAL_EXIT() \
    open_cfw_test_event_loop_critical_exit()
#define OPEN_CFW_EVENT_LOOP_DELAY(ticks) \
    open_cfw_test_event_loop_delay(ticks)
#define OPEN_CFW_EVENT_LOOP_TICK() open_cfw_test_event_loop_tick()
#define OPEN_CFW_EVENT_LOOP_TASK_CONTINUE() \
    open_cfw_test_event_loop_task_continue()

#include "../../components/apollo_main/core_overlay/event_loop.c"

struct open_cfw_test_event_loop_event {
    void *argument;
    void (*callback)(void *);
};

unsigned int open_cfw_test_event_loop_events[512];
unsigned int open_cfw_test_event_loop_event_count;
unsigned int open_cfw_test_event_loop_levels[256];
unsigned int open_cfw_test_event_loop_level_count;
unsigned int open_cfw_test_event_loop_level_index;
__UINTPTR_TYPE__ open_cfw_test_event_loop_log_records[32][8];
unsigned int open_cfw_test_event_loop_log_count;
__UINTPTR_TYPE__ open_cfw_test_event_loop_trace_records[32][6];
unsigned int open_cfw_test_event_loop_trace_count;

void *open_cfw_test_event_loop_queue_create_result;
void *open_cfw_test_event_loop_timer_create_result;
void *open_cfw_test_event_loop_mutex_create_result;
void *open_cfw_test_event_loop_thread_create_result;
unsigned int open_cfw_test_event_loop_queue_create_calls;
unsigned int open_cfw_test_event_loop_queue_create_count;
unsigned int open_cfw_test_event_loop_queue_create_size;
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_create_attributes;
unsigned int open_cfw_test_event_loop_timer_create_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_timer_create_callback;
unsigned int open_cfw_test_event_loop_timer_create_type;
unsigned int open_cfw_test_event_loop_timer_create_argument;
__UINTPTR_TYPE__ open_cfw_test_event_loop_timer_create_attributes;
unsigned int open_cfw_test_event_loop_mutex_create_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_mutex_create_attributes;
unsigned int open_cfw_test_event_loop_thread_create_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_thread_create_entry;
__UINTPTR_TYPE__ open_cfw_test_event_loop_thread_create_argument;
__UINTPTR_TYPE__ open_cfw_test_event_loop_thread_create_attributes;
unsigned int open_cfw_test_event_loop_thread_terminate_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_thread_terminate_handle;

unsigned int open_cfw_test_event_loop_queue_get_results[16];
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_get_arguments[16];
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_get_callbacks[16];
unsigned int open_cfw_test_event_loop_queue_get_count;
unsigned int open_cfw_test_event_loop_queue_get_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_get_handle;
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_get_priority;
unsigned int open_cfw_test_event_loop_queue_get_timeout;

unsigned int open_cfw_test_event_loop_queue_put_results[32];
unsigned int open_cfw_test_event_loop_queue_put_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_put_handles[32];
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_put_arguments[32];
__UINTPTR_TYPE__ open_cfw_test_event_loop_queue_put_callbacks[32];
unsigned int open_cfw_test_event_loop_queue_put_priorities[32];
unsigned int open_cfw_test_event_loop_queue_put_timeouts[32];

unsigned int open_cfw_test_event_loop_mutex_acquire_results[16];
unsigned int open_cfw_test_event_loop_mutex_acquire_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_mutex_acquire_handle;
unsigned int open_cfw_test_event_loop_mutex_acquire_timeout;
unsigned int open_cfw_test_event_loop_mutex_release_results[16];
unsigned int open_cfw_test_event_loop_mutex_release_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_mutex_release_handle;

unsigned int open_cfw_test_event_loop_timer_start_results[16];
unsigned int open_cfw_test_event_loop_timer_start_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_timer_start_handles[16];
unsigned int open_cfw_test_event_loop_timer_start_ticks[16];
unsigned int open_cfw_test_event_loop_timer_stop_calls;
__UINTPTR_TYPE__ open_cfw_test_event_loop_timer_stop_handles[16];

unsigned int open_cfw_test_event_loop_critical_enter_calls;
unsigned int open_cfw_test_event_loop_critical_exit_calls;
unsigned int open_cfw_test_event_loop_delay_calls;
unsigned int open_cfw_test_event_loop_delay_ticks[16];
unsigned int open_cfw_test_event_loop_delay_publish_thread_call;
unsigned int open_cfw_test_event_loop_ticks[32];
unsigned int open_cfw_test_event_loop_tick_count;
unsigned int open_cfw_test_event_loop_tick_calls;
unsigned int open_cfw_test_event_loop_task_iterations;
unsigned int open_cfw_test_event_loop_task_continue_calls;
unsigned int open_cfw_test_event_loop_callback_calls[4];
__UINTPTR_TYPE__ open_cfw_test_event_loop_callback_arguments[4];

static void open_cfw_test_event_loop_record(unsigned int event)
{
    open_cfw_test_event_loop_events[
        open_cfw_test_event_loop_event_count++
    ] = event;
}

void open_cfw_test_event_loop_callback_zero(void *argument)
{
    ++open_cfw_test_event_loop_callback_calls[0];
    open_cfw_test_event_loop_callback_arguments[0] =
        (__UINTPTR_TYPE__)argument;
    open_cfw_test_event_loop_record(40U);
}

void open_cfw_test_event_loop_callback_one(void *argument)
{
    ++open_cfw_test_event_loop_callback_calls[1];
    open_cfw_test_event_loop_callback_arguments[1] =
        (__UINTPTR_TYPE__)argument;
    open_cfw_test_event_loop_record(41U);
}

void open_cfw_test_event_loop_callback_two(void *argument)
{
    ++open_cfw_test_event_loop_callback_calls[2];
    open_cfw_test_event_loop_callback_arguments[2] =
        (__UINTPTR_TYPE__)argument;
    open_cfw_test_event_loop_record(42U);
}

void open_cfw_test_event_loop_reset(void)
{
    unsigned int first;
    unsigned int second;

    open_cfw_test_event_loop_queue_handle = (void *)0;
    open_cfw_test_event_loop_thread_handle = (void *)0;
    open_cfw_test_event_loop_mutex_handle = (void *)0;
    open_cfw_test_event_loop_timer_handle = (void *)0;
    open_cfw_test_event_loop_last_tick = 0U;
    open_cfw_test_event_loop_next_delay = 0U;
    for (first = 0U; first < 64U; ++first) {
        open_cfw_test_event_loop_callbacks[first] =
            (void (*)(void *))0;
        open_cfw_test_event_loop_arguments[first] = (void *)0;
        open_cfw_test_event_loop_delays[first] = 0U;
    }
    for (first = 0U; first < 512U; ++first) {
        open_cfw_test_event_loop_events[first] = 0U;
    }
    for (first = 0U; first < 256U; ++first) {
        open_cfw_test_event_loop_levels[first] = 0U;
    }
    for (first = 0U; first < 32U; ++first) {
        open_cfw_test_event_loop_queue_put_results[first] = 0U;
        open_cfw_test_event_loop_queue_put_handles[first] = 0U;
        open_cfw_test_event_loop_queue_put_arguments[first] = 0U;
        open_cfw_test_event_loop_queue_put_callbacks[first] = 0U;
        open_cfw_test_event_loop_queue_put_priorities[first] = 0U;
        open_cfw_test_event_loop_queue_put_timeouts[first] = 0U;
        open_cfw_test_event_loop_ticks[first] = 0U;
        for (second = 0U; second < 8U; ++second) {
            open_cfw_test_event_loop_log_records[first][second] = 0U;
        }
        for (second = 0U; second < 6U; ++second) {
            open_cfw_test_event_loop_trace_records[first][second] = 0U;
        }
    }
    for (first = 0U; first < 16U; ++first) {
        open_cfw_test_event_loop_queue_get_results[first] = 0U;
        open_cfw_test_event_loop_queue_get_arguments[first] = 0U;
        open_cfw_test_event_loop_queue_get_callbacks[first] = 0U;
        open_cfw_test_event_loop_mutex_acquire_results[first] = 0U;
        open_cfw_test_event_loop_mutex_release_results[first] = 0U;
        open_cfw_test_event_loop_timer_start_results[first] = 0U;
        open_cfw_test_event_loop_timer_start_handles[first] = 0U;
        open_cfw_test_event_loop_timer_start_ticks[first] = 0U;
        open_cfw_test_event_loop_timer_stop_handles[first] = 0U;
        open_cfw_test_event_loop_delay_ticks[first] = 0U;
    }
    for (first = 0U; first < 4U; ++first) {
        open_cfw_test_event_loop_callback_calls[first] = 0U;
        open_cfw_test_event_loop_callback_arguments[first] = 0U;
    }

    open_cfw_test_event_loop_event_count = 0U;
    open_cfw_test_event_loop_level_count = 0U;
    open_cfw_test_event_loop_level_index = 0U;
    open_cfw_test_event_loop_log_count = 0U;
    open_cfw_test_event_loop_trace_count = 0U;
    open_cfw_test_event_loop_queue_create_result = (void *)0x11110000U;
    open_cfw_test_event_loop_timer_create_result = (void *)0x22220000U;
    open_cfw_test_event_loop_mutex_create_result = (void *)0x33330000U;
    open_cfw_test_event_loop_thread_create_result = (void *)0x44440000U;
    open_cfw_test_event_loop_queue_create_calls = 0U;
    open_cfw_test_event_loop_queue_create_count = 0U;
    open_cfw_test_event_loop_queue_create_size = 0U;
    open_cfw_test_event_loop_queue_create_attributes = 0U;
    open_cfw_test_event_loop_timer_create_calls = 0U;
    open_cfw_test_event_loop_timer_create_callback = 0U;
    open_cfw_test_event_loop_timer_create_type = 0U;
    open_cfw_test_event_loop_timer_create_argument = 0U;
    open_cfw_test_event_loop_timer_create_attributes = 0U;
    open_cfw_test_event_loop_mutex_create_calls = 0U;
    open_cfw_test_event_loop_mutex_create_attributes = 0U;
    open_cfw_test_event_loop_thread_create_calls = 0U;
    open_cfw_test_event_loop_thread_create_entry = 0U;
    open_cfw_test_event_loop_thread_create_argument = 0U;
    open_cfw_test_event_loop_thread_create_attributes = 0U;
    open_cfw_test_event_loop_thread_terminate_calls = 0U;
    open_cfw_test_event_loop_thread_terminate_handle = 0U;
    open_cfw_test_event_loop_queue_get_count = 0U;
    open_cfw_test_event_loop_queue_get_calls = 0U;
    open_cfw_test_event_loop_queue_get_handle = 0U;
    open_cfw_test_event_loop_queue_get_priority = 0U;
    open_cfw_test_event_loop_queue_get_timeout = 0U;
    open_cfw_test_event_loop_queue_put_calls = 0U;
    open_cfw_test_event_loop_mutex_acquire_calls = 0U;
    open_cfw_test_event_loop_mutex_acquire_handle = 0U;
    open_cfw_test_event_loop_mutex_acquire_timeout = 0U;
    open_cfw_test_event_loop_mutex_release_calls = 0U;
    open_cfw_test_event_loop_mutex_release_handle = 0U;
    open_cfw_test_event_loop_timer_start_calls = 0U;
    open_cfw_test_event_loop_timer_stop_calls = 0U;
    open_cfw_test_event_loop_critical_enter_calls = 0U;
    open_cfw_test_event_loop_critical_exit_calls = 0U;
    open_cfw_test_event_loop_delay_calls = 0U;
    open_cfw_test_event_loop_delay_publish_thread_call = 0U;
    open_cfw_test_event_loop_tick_count = 0U;
    open_cfw_test_event_loop_tick_calls = 0U;
    open_cfw_test_event_loop_task_iterations = 0U;
    open_cfw_test_event_loop_task_continue_calls = 0U;
}

unsigned int open_cfw_test_event_loop_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_event_loop_level_index
        < open_cfw_test_event_loop_level_count
    ) {
        value = open_cfw_test_event_loop_levels[
            open_cfw_test_event_loop_level_index
        ];
    }
    ++open_cfw_test_event_loop_level_index;
    open_cfw_test_event_loop_record(1U);
    return value;
}

static unsigned int open_cfw_test_event_loop_argument_count(
    unsigned int line
)
{
    if (line == 0x8CU || line == 0xA0U) {
        return 1U;
    }
    if (line == 0xE1U) {
        return 2U;
    }
    return 0U;
}

void open_cfw_test_event_loop_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    unsigned int index = open_cfw_test_event_loop_log_count++;
    unsigned int count = open_cfw_test_event_loop_argument_count(line);
    va_list arguments;

    open_cfw_test_event_loop_log_records[index][0] = level;
    open_cfw_test_event_loop_log_records[index][1] =
        (__UINTPTR_TYPE__)module;
    open_cfw_test_event_loop_log_records[index][2] =
        (__UINTPTR_TYPE__)file;
    open_cfw_test_event_loop_log_records[index][3] =
        (__UINTPTR_TYPE__)function;
    open_cfw_test_event_loop_log_records[index][4] = line;
    open_cfw_test_event_loop_log_records[index][5] =
        (__UINTPTR_TYPE__)message;
    va_start(arguments, message);
    if (count > 0U) {
        open_cfw_test_event_loop_log_records[index][6] =
            va_arg(arguments, unsigned int);
    }
    if (count > 1U) {
        open_cfw_test_event_loop_log_records[index][7] =
            va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_event_loop_record(2U);
}

void open_cfw_test_event_loop_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    unsigned int index = open_cfw_test_event_loop_trace_count++;
    unsigned int count = 0U;
    va_list arguments;

    if (level == 0x04400000U) {
        count = 1U;
    }
    else if (level == 0x04800000U) {
        count = 2U;
    }
    open_cfw_test_event_loop_trace_records[index][0] = level;
    open_cfw_test_event_loop_trace_records[index][1] =
        (__UINTPTR_TYPE__)first;
    open_cfw_test_event_loop_trace_records[index][2] =
        (__UINTPTR_TYPE__)second;
    va_start(arguments, second);
    if (count > 0U) {
        open_cfw_test_event_loop_trace_records[index][3] =
            va_arg(arguments, unsigned int);
    }
    if (count > 1U) {
        open_cfw_test_event_loop_trace_records[index][4] =
            va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_event_loop_record(3U);
}

void *open_cfw_test_event_loop_queue_create(
    unsigned int count,
    unsigned int size,
    const void *attributes
)
{
    ++open_cfw_test_event_loop_queue_create_calls;
    open_cfw_test_event_loop_queue_create_count = count;
    open_cfw_test_event_loop_queue_create_size = size;
    open_cfw_test_event_loop_queue_create_attributes =
        (__UINTPTR_TYPE__)attributes;
    open_cfw_test_event_loop_record(10U);
    return open_cfw_test_event_loop_queue_create_result;
}

void *open_cfw_test_event_loop_timer_create(
    void (*callback)(unsigned int),
    unsigned int type,
    unsigned int argument,
    const void *attributes
)
{
    ++open_cfw_test_event_loop_timer_create_calls;
    open_cfw_test_event_loop_timer_create_callback =
        (__UINTPTR_TYPE__)callback;
    open_cfw_test_event_loop_timer_create_type = type;
    open_cfw_test_event_loop_timer_create_argument = argument;
    open_cfw_test_event_loop_timer_create_attributes =
        (__UINTPTR_TYPE__)attributes;
    open_cfw_test_event_loop_record(11U);
    return open_cfw_test_event_loop_timer_create_result;
}

void *open_cfw_test_event_loop_mutex_create(const void *attributes)
{
    ++open_cfw_test_event_loop_mutex_create_calls;
    open_cfw_test_event_loop_mutex_create_attributes =
        (__UINTPTR_TYPE__)attributes;
    open_cfw_test_event_loop_record(12U);
    return open_cfw_test_event_loop_mutex_create_result;
}

void *open_cfw_test_event_loop_thread_create(
    void (*entry)(void *),
    void *argument,
    const void *attributes
)
{
    ++open_cfw_test_event_loop_thread_create_calls;
    open_cfw_test_event_loop_thread_create_entry = (__UINTPTR_TYPE__)entry;
    open_cfw_test_event_loop_thread_create_argument =
        (__UINTPTR_TYPE__)argument;
    open_cfw_test_event_loop_thread_create_attributes =
        (__UINTPTR_TYPE__)attributes;
    open_cfw_test_event_loop_record(13U);
    return open_cfw_test_event_loop_thread_create_result;
}

unsigned int open_cfw_test_event_loop_thread_terminate(void *handle)
{
    ++open_cfw_test_event_loop_thread_terminate_calls;
    open_cfw_test_event_loop_thread_terminate_handle =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_record(14U);
    return 0U;
}

unsigned int open_cfw_test_event_loop_queue_get(
    void *handle,
    void *event_pointer,
    unsigned char *priority,
    unsigned int timeout
)
{
    unsigned int index = open_cfw_test_event_loop_queue_get_calls++;
    struct open_cfw_test_event_loop_event *event = event_pointer;
    unsigned int result =
        open_cfw_test_event_loop_queue_get_results[index];

    open_cfw_test_event_loop_queue_get_handle = (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_queue_get_priority =
        (__UINTPTR_TYPE__)priority;
    open_cfw_test_event_loop_queue_get_timeout = timeout;
    if (result == 0U) {
        event->argument = (void *)
            open_cfw_test_event_loop_queue_get_arguments[index];
        event->callback = (void (*)(void *))
            open_cfw_test_event_loop_queue_get_callbacks[index];
    }
    open_cfw_test_event_loop_record(20U);
    return result;
}

unsigned int open_cfw_test_event_loop_queue_put(
    void *handle,
    const void *event_pointer,
    unsigned char priority,
    unsigned int timeout
)
{
    unsigned int index = open_cfw_test_event_loop_queue_put_calls++;
    const struct open_cfw_test_event_loop_event *event = event_pointer;

    open_cfw_test_event_loop_queue_put_handles[index] =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_queue_put_arguments[index] =
        (__UINTPTR_TYPE__)event->argument;
    open_cfw_test_event_loop_queue_put_callbacks[index] =
        (__UINTPTR_TYPE__)event->callback;
    open_cfw_test_event_loop_queue_put_priorities[index] = priority;
    open_cfw_test_event_loop_queue_put_timeouts[index] = timeout;
    open_cfw_test_event_loop_record(21U);
    return open_cfw_test_event_loop_queue_put_results[index];
}

unsigned int open_cfw_test_event_loop_mutex_acquire(
    void *handle,
    unsigned int timeout
)
{
    unsigned int index = open_cfw_test_event_loop_mutex_acquire_calls++;

    open_cfw_test_event_loop_mutex_acquire_handle =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_mutex_acquire_timeout = timeout;
    open_cfw_test_event_loop_record(22U);
    return open_cfw_test_event_loop_mutex_acquire_results[index];
}

unsigned int open_cfw_test_event_loop_mutex_release(void *handle)
{
    unsigned int index = open_cfw_test_event_loop_mutex_release_calls++;

    open_cfw_test_event_loop_mutex_release_handle =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_record(23U);
    return open_cfw_test_event_loop_mutex_release_results[index];
}

unsigned int open_cfw_test_event_loop_timer_start(
    void *handle,
    unsigned int ticks
)
{
    unsigned int index = open_cfw_test_event_loop_timer_start_calls++;

    open_cfw_test_event_loop_timer_start_handles[index] =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_timer_start_ticks[index] = ticks;
    open_cfw_test_event_loop_record(24U);
    return open_cfw_test_event_loop_timer_start_results[index];
}

unsigned int open_cfw_test_event_loop_timer_stop(void *handle)
{
    unsigned int index = open_cfw_test_event_loop_timer_stop_calls++;

    open_cfw_test_event_loop_timer_stop_handles[index] =
        (__UINTPTR_TYPE__)handle;
    open_cfw_test_event_loop_record(25U);
    return 0U;
}

void open_cfw_test_event_loop_critical_enter(void)
{
    ++open_cfw_test_event_loop_critical_enter_calls;
    open_cfw_test_event_loop_record(26U);
}

void open_cfw_test_event_loop_critical_exit(void)
{
    ++open_cfw_test_event_loop_critical_exit_calls;
    open_cfw_test_event_loop_record(27U);
}

void open_cfw_test_event_loop_delay(unsigned int ticks)
{
    unsigned int index = open_cfw_test_event_loop_delay_calls++;

    open_cfw_test_event_loop_delay_ticks[index] = ticks;
    if (
        open_cfw_test_event_loop_delay_publish_thread_call != 0U
        && open_cfw_test_event_loop_delay_calls
            == open_cfw_test_event_loop_delay_publish_thread_call
    ) {
        open_cfw_test_event_loop_thread_handle = (void *)0x44440000U;
    }
    open_cfw_test_event_loop_record(28U);
}

unsigned int open_cfw_test_event_loop_tick(void)
{
    unsigned int index = open_cfw_test_event_loop_tick_calls++;

    open_cfw_test_event_loop_record(29U);
    if (index < open_cfw_test_event_loop_tick_count) {
        return open_cfw_test_event_loop_ticks[index];
    }
    return 0U;
}

int open_cfw_test_event_loop_task_continue(void)
{
    ++open_cfw_test_event_loop_task_continue_calls;
    return open_cfw_test_event_loop_task_continue_calls
        < open_cfw_test_event_loop_task_iterations;
}
