void *open_cfw_test_display_sender_queue_handle;
int open_cfw_test_display_sender_queue_result;
unsigned int open_cfw_test_display_sender_queue_calls;
void *open_cfw_test_display_sender_queue;
unsigned int open_cfw_test_display_sender_message[9];
unsigned int open_cfw_test_display_sender_priority;
unsigned int open_cfw_test_display_sender_timeout;
unsigned int open_cfw_test_display_sender_flag_calls;
unsigned int open_cfw_test_display_sender_flag_values[3];
unsigned int open_cfw_test_display_sender_log_calls;
unsigned int open_cfw_test_display_sender_log_level;
const void *open_cfw_test_display_sender_log_tag;
const void *open_cfw_test_display_sender_log_file;
const void *open_cfw_test_display_sender_log_function;
unsigned int open_cfw_test_display_sender_log_line;
const void *open_cfw_test_display_sender_log_format;
unsigned int open_cfw_test_display_sender_backend_calls;
unsigned int open_cfw_test_display_sender_backend_mask;
const void *open_cfw_test_display_sender_backend_format;
const void *open_cfw_test_display_sender_backend_duplicate_format;
unsigned int open_cfw_test_display_sender_trace_count;
unsigned int open_cfw_test_display_sender_trace[8];

static void open_cfw_test_display_sender_record(unsigned int value)
{
    unsigned int index = open_cfw_test_display_sender_trace_count++;

    if (index < 8U) {
        open_cfw_test_display_sender_trace[index] = value;
    }
}

int open_cfw_test_display_sender_queue_send(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
)
{
    const unsigned int *words = message;
    unsigned int index;

    open_cfw_test_display_sender_record(1U);
    open_cfw_test_display_sender_queue_calls += 1U;
    open_cfw_test_display_sender_queue = queue;
    for (index = 0U; index < 9U; index += 1U) {
        open_cfw_test_display_sender_message[index] = words[index];
    }
    open_cfw_test_display_sender_priority = priority;
    open_cfw_test_display_sender_timeout = timeout;
    return open_cfw_test_display_sender_queue_result;
}

unsigned int open_cfw_test_display_sender_log_flags(void)
{
    unsigned int index = open_cfw_test_display_sender_flag_calls++;

    open_cfw_test_display_sender_record(2U);
    if (index >= 3U) {
        index = 2U;
    }
    return open_cfw_test_display_sender_flag_values[index];
}

void open_cfw_test_display_sender_log(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    open_cfw_test_display_sender_record(3U);
    open_cfw_test_display_sender_log_calls += 1U;
    open_cfw_test_display_sender_log_level = level;
    open_cfw_test_display_sender_log_tag = tag;
    open_cfw_test_display_sender_log_file = file;
    open_cfw_test_display_sender_log_function = function;
    open_cfw_test_display_sender_log_line = line;
    open_cfw_test_display_sender_log_format = format;
}

void open_cfw_test_display_sender_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    open_cfw_test_display_sender_record(4U);
    open_cfw_test_display_sender_backend_calls += 1U;
    open_cfw_test_display_sender_backend_mask = mask;
    open_cfw_test_display_sender_backend_format = format;
    open_cfw_test_display_sender_backend_duplicate_format =
        duplicate_format;
}

#define OPEN_CFW_DISPLAY_SENDER_QUEUE_HANDLE \
    open_cfw_test_display_sender_queue_handle
#define OPEN_CFW_DISPLAY_SENDER_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    open_cfw_test_display_sender_queue_send( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    )
#define OPEN_CFW_DISPLAY_SENDER_LOG_FLAGS() \
    open_cfw_test_display_sender_log_flags()
#define OPEN_CFW_DISPLAY_SENDER_LOG open_cfw_test_display_sender_log
#define OPEN_CFW_DISPLAY_SENDER_BACKEND_LOG \
    open_cfw_test_display_sender_backend_log

#include "../../components/apollo_main/core_overlay/display_queue_senders.c"
