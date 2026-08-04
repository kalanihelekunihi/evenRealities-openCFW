#include <stdarg.h>

typedef void (*open_cfw_test_display_thread_entry_fn)(void *argument);

void *open_cfw_test_display_thread_handle;
void *open_cfw_test_display_thread_create_result;
void *open_cfw_test_display_queue_handle;
void *open_cfw_test_display_queue_create_result;
unsigned int open_cfw_test_display_thread_trace_count;
unsigned int open_cfw_test_display_thread_trace[8];
unsigned int open_cfw_test_display_thread_create_calls;
open_cfw_test_display_thread_entry_fn
    open_cfw_test_display_thread_create_entry;
void *open_cfw_test_display_thread_create_argument;
const void *open_cfw_test_display_thread_create_attributes;
unsigned int open_cfw_test_display_queue_create_calls;
unsigned int open_cfw_test_display_queue_create_count;
unsigned int open_cfw_test_display_queue_create_size;
const void *open_cfw_test_display_queue_create_attributes;
unsigned int open_cfw_test_display_thread_flag_calls;
unsigned int open_cfw_test_display_thread_flag_values[3];
unsigned int open_cfw_test_display_thread_log_calls;
unsigned int open_cfw_test_display_thread_log_level;
const void *open_cfw_test_display_thread_log_tag;
const void *open_cfw_test_display_thread_log_file;
const void *open_cfw_test_display_thread_log_function;
unsigned int open_cfw_test_display_thread_log_line;
const void *open_cfw_test_display_thread_log_format;
void *open_cfw_test_display_thread_log_handle;
unsigned int open_cfw_test_display_thread_backend_calls;
unsigned int open_cfw_test_display_thread_backend_mask;
const void *open_cfw_test_display_thread_backend_format;
const void *open_cfw_test_display_thread_backend_duplicate_format;
void *open_cfw_test_display_thread_backend_handle;

static void open_cfw_test_display_thread_record(unsigned int value)
{
    unsigned int index = open_cfw_test_display_thread_trace_count++;

    if (index < 8U) {
        open_cfw_test_display_thread_trace[index] = value;
    }
}

void *open_cfw_test_display_thread_create(
    open_cfw_test_display_thread_entry_fn entry,
    void *argument,
    const void *attributes
)
{
    open_cfw_test_display_thread_record(1U);
    open_cfw_test_display_thread_create_calls += 1U;
    open_cfw_test_display_thread_create_entry = entry;
    open_cfw_test_display_thread_create_argument = argument;
    open_cfw_test_display_thread_create_attributes = attributes;
    return open_cfw_test_display_thread_create_result;
}

void *open_cfw_test_display_queue_create(
    unsigned int message_count,
    unsigned int message_size,
    const void *attributes
)
{
    open_cfw_test_display_thread_record(5U);
    open_cfw_test_display_queue_create_calls += 1U;
    open_cfw_test_display_queue_create_count = message_count;
    open_cfw_test_display_queue_create_size = message_size;
    open_cfw_test_display_queue_create_attributes = attributes;
    return open_cfw_test_display_queue_create_result;
}

unsigned int open_cfw_test_display_thread_log_flags(void)
{
    unsigned int index = open_cfw_test_display_thread_flag_calls++;

    open_cfw_test_display_thread_record(2U);
    if (index >= 3U) {
        index = 2U;
    }
    return open_cfw_test_display_thread_flag_values[index];
}

void open_cfw_test_display_thread_log(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    va_list arguments;

    open_cfw_test_display_thread_record(3U);
    open_cfw_test_display_thread_log_calls += 1U;
    open_cfw_test_display_thread_log_level = level;
    open_cfw_test_display_thread_log_tag = tag;
    open_cfw_test_display_thread_log_file = file;
    open_cfw_test_display_thread_log_function = function;
    open_cfw_test_display_thread_log_line = line;
    open_cfw_test_display_thread_log_format = format;
    open_cfw_test_display_thread_log_handle = (void *)0;
    if (level == 4U) {
        va_start(arguments, format);
        open_cfw_test_display_thread_log_handle =
            va_arg(arguments, void *);
        va_end(arguments);
    }
}

void open_cfw_test_display_thread_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    va_list arguments;

    open_cfw_test_display_thread_record(4U);
    open_cfw_test_display_thread_backend_calls += 1U;
    open_cfw_test_display_thread_backend_mask = mask;
    open_cfw_test_display_thread_backend_format = format;
    open_cfw_test_display_thread_backend_duplicate_format =
        duplicate_format;
    open_cfw_test_display_thread_backend_handle = (void *)0;
    if (mask == 0x10400000U) {
        va_start(arguments, duplicate_format);
        open_cfw_test_display_thread_backend_handle =
            va_arg(arguments, void *);
        va_end(arguments);
    }
}

#define OPEN_CFW_DISPLAY_THREAD_HANDLE \
    open_cfw_test_display_thread_handle
#define OPEN_CFW_DISPLAY_THREAD_CREATE(entry, argument, attributes) \
    open_cfw_test_display_thread_create((entry), (argument), (attributes))
#define OPEN_CFW_DISPLAY_THREAD_LOG_FLAGS() \
    open_cfw_test_display_thread_log_flags()
#define OPEN_CFW_DISPLAY_QUEUE_HANDLE \
    open_cfw_test_display_queue_handle
#define OPEN_CFW_DISPLAY_QUEUE_CREATE(count, size, attributes) \
    open_cfw_test_display_queue_create((count), (size), (attributes))
#define OPEN_CFW_DISPLAY_THREAD_LOG open_cfw_test_display_thread_log
#define OPEN_CFW_DISPLAY_THREAD_BACKEND_LOG \
    open_cfw_test_display_thread_backend_log

#include "../../components/apollo_main/core_overlay/display_thread_init.c"
