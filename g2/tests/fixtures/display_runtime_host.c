#include <stdarg.h>

typedef void (*open_cfw_test_display_runtime_callback_fn)(void *argument);

void *open_cfw_test_display_runtime_thread_handle;
void *open_cfw_test_display_runtime_queue_handle;
void *open_cfw_test_display_runtime_timer_handle;
void *open_cfw_test_display_runtime_timer_create_result;
int open_cfw_test_display_runtime_queue_send_result;
unsigned int open_cfw_test_display_runtime_trace_count;
unsigned int open_cfw_test_display_runtime_trace[16];
unsigned int open_cfw_test_display_runtime_thread_terminate_calls;
void *open_cfw_test_display_runtime_thread_terminate_thread;
void *open_cfw_test_display_runtime_thread_during_terminate;
unsigned int open_cfw_test_display_runtime_resource_acquire_calls;
unsigned int open_cfw_test_display_runtime_resource_acquire_value;
unsigned int open_cfw_test_display_runtime_resource_release_calls;
unsigned int open_cfw_test_display_runtime_resource_release_value;
unsigned int open_cfw_test_display_runtime_timer_create_calls;
open_cfw_test_display_runtime_callback_fn
    open_cfw_test_display_runtime_timer_create_callback;
unsigned int open_cfw_test_display_runtime_timer_create_kind;
void *open_cfw_test_display_runtime_timer_create_argument;
const void *open_cfw_test_display_runtime_timer_create_attributes;
unsigned int open_cfw_test_display_runtime_timer_start_calls;
void *open_cfw_test_display_runtime_timer_start_timer;
unsigned int open_cfw_test_display_runtime_timer_start_ticks;
unsigned int open_cfw_test_display_runtime_timer_stop_calls;
void *open_cfw_test_display_runtime_timer_stop_timer;
unsigned int open_cfw_test_display_runtime_queue_send_calls;
void *open_cfw_test_display_runtime_queue_send_queue;
unsigned int open_cfw_test_display_runtime_queue_send_message[9];
unsigned int open_cfw_test_display_runtime_queue_send_priority;
unsigned int open_cfw_test_display_runtime_queue_send_timeout;
unsigned int open_cfw_test_display_runtime_flag_calls;
unsigned int open_cfw_test_display_runtime_flag_values[3];
unsigned int open_cfw_test_display_runtime_log_calls;
unsigned int open_cfw_test_display_runtime_log_level;
const void *open_cfw_test_display_runtime_log_tag;
const void *open_cfw_test_display_runtime_log_file;
const void *open_cfw_test_display_runtime_log_function;
unsigned int open_cfw_test_display_runtime_log_line;
const void *open_cfw_test_display_runtime_log_format;
unsigned int open_cfw_test_display_runtime_backend_calls;
unsigned int open_cfw_test_display_runtime_backend_mask;
const void *open_cfw_test_display_runtime_backend_format;
const void *open_cfw_test_display_runtime_backend_duplicate_format;

static void open_cfw_test_display_runtime_record(unsigned int value)
{
    unsigned int index = open_cfw_test_display_runtime_trace_count++;

    if (index < 16U) {
        open_cfw_test_display_runtime_trace[index] = value;
    }
}

void open_cfw_test_display_runtime_thread_terminate(void *thread)
{
    open_cfw_test_display_runtime_record(1U);
    open_cfw_test_display_runtime_thread_terminate_calls += 1U;
    open_cfw_test_display_runtime_thread_terminate_thread = thread;
    open_cfw_test_display_runtime_thread_during_terminate =
        open_cfw_test_display_runtime_thread_handle;
}

void open_cfw_test_display_runtime_resource_acquire(unsigned int resource)
{
    open_cfw_test_display_runtime_record(2U);
    open_cfw_test_display_runtime_resource_acquire_calls += 1U;
    open_cfw_test_display_runtime_resource_acquire_value = resource;
}

void open_cfw_test_display_runtime_resource_release(unsigned int resource)
{
    open_cfw_test_display_runtime_record(3U);
    open_cfw_test_display_runtime_resource_release_calls += 1U;
    open_cfw_test_display_runtime_resource_release_value = resource;
}

void *open_cfw_test_display_runtime_timer_create(
    open_cfw_test_display_runtime_callback_fn callback,
    unsigned int kind,
    void *argument,
    const void *attributes
)
{
    open_cfw_test_display_runtime_record(4U);
    open_cfw_test_display_runtime_timer_create_calls += 1U;
    open_cfw_test_display_runtime_timer_create_callback = callback;
    open_cfw_test_display_runtime_timer_create_kind = kind;
    open_cfw_test_display_runtime_timer_create_argument = argument;
    open_cfw_test_display_runtime_timer_create_attributes = attributes;
    return open_cfw_test_display_runtime_timer_create_result;
}

int open_cfw_test_display_runtime_timer_start(
    void *timer,
    unsigned int ticks
)
{
    open_cfw_test_display_runtime_record(5U);
    open_cfw_test_display_runtime_timer_start_calls += 1U;
    open_cfw_test_display_runtime_timer_start_timer = timer;
    open_cfw_test_display_runtime_timer_start_ticks = ticks;
    return 0x1234;
}

int open_cfw_test_display_runtime_timer_stop(void *timer)
{
    open_cfw_test_display_runtime_record(6U);
    open_cfw_test_display_runtime_timer_stop_calls += 1U;
    open_cfw_test_display_runtime_timer_stop_timer = timer;
    return 0x5678;
}

int open_cfw_test_display_runtime_queue_send(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
)
{
    const unsigned int *words = message;
    unsigned int index;

    open_cfw_test_display_runtime_record(7U);
    open_cfw_test_display_runtime_queue_send_calls += 1U;
    open_cfw_test_display_runtime_queue_send_queue = queue;
    for (index = 0U; index < 9U; index += 1U) {
        open_cfw_test_display_runtime_queue_send_message[index] =
            words[index];
    }
    open_cfw_test_display_runtime_queue_send_priority = priority;
    open_cfw_test_display_runtime_queue_send_timeout = timeout;
    return open_cfw_test_display_runtime_queue_send_result;
}

unsigned int open_cfw_test_display_runtime_log_flags(void)
{
    unsigned int index = open_cfw_test_display_runtime_flag_calls++;

    open_cfw_test_display_runtime_record(8U);
    if (index >= 3U) {
        index = 2U;
    }
    return open_cfw_test_display_runtime_flag_values[index];
}

void open_cfw_test_display_runtime_log(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    open_cfw_test_display_runtime_record(9U);
    open_cfw_test_display_runtime_log_calls += 1U;
    open_cfw_test_display_runtime_log_level = level;
    open_cfw_test_display_runtime_log_tag = tag;
    open_cfw_test_display_runtime_log_file = file;
    open_cfw_test_display_runtime_log_function = function;
    open_cfw_test_display_runtime_log_line = line;
    open_cfw_test_display_runtime_log_format = format;
}

void open_cfw_test_display_runtime_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    open_cfw_test_display_runtime_record(10U);
    open_cfw_test_display_runtime_backend_calls += 1U;
    open_cfw_test_display_runtime_backend_mask = mask;
    open_cfw_test_display_runtime_backend_format = format;
    open_cfw_test_display_runtime_backend_duplicate_format =
        duplicate_format;
}

#define OPEN_CFW_DISPLAY_RUNTIME_THREAD_HANDLE \
    open_cfw_test_display_runtime_thread_handle
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_HANDLE \
    open_cfw_test_display_runtime_queue_handle
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_HANDLE \
    open_cfw_test_display_runtime_timer_handle
#define OPEN_CFW_DISPLAY_RUNTIME_THREAD_TERMINATE(thread) \
    open_cfw_test_display_runtime_thread_terminate(thread)
#define OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_ACQUIRE(resource) \
    open_cfw_test_display_runtime_resource_acquire(resource)
#define OPEN_CFW_DISPLAY_RUNTIME_RESOURCE_RELEASE(resource) \
    open_cfw_test_display_runtime_resource_release(resource)
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_CREATE( \
    callback, \
    kind, \
    argument, \
    attributes \
) \
    open_cfw_test_display_runtime_timer_create( \
        (callback), \
        (kind), \
        (argument), \
        (attributes) \
    )
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_START(timer, ticks) \
    open_cfw_test_display_runtime_timer_start((timer), (ticks))
#define OPEN_CFW_DISPLAY_RUNTIME_TIMER_STOP(timer) \
    open_cfw_test_display_runtime_timer_stop(timer)
#define OPEN_CFW_DISPLAY_RUNTIME_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    open_cfw_test_display_runtime_queue_send( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    )
#define OPEN_CFW_DISPLAY_RUNTIME_LOG_FLAGS() \
    open_cfw_test_display_runtime_log_flags()
#define OPEN_CFW_DISPLAY_RUNTIME_LOG open_cfw_test_display_runtime_log
#define OPEN_CFW_DISPLAY_RUNTIME_BACKEND_LOG \
    open_cfw_test_display_runtime_backend_log

#include "../../components/apollo_main/core_overlay/display_runtime.c"
