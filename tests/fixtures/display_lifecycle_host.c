unsigned int open_cfw_test_display_lifecycle_active;
void *open_cfw_test_display_lifecycle_queue_handle;
int open_cfw_test_display_lifecycle_running_result;
unsigned int open_cfw_test_display_lifecycle_running_calls;
int open_cfw_test_display_lifecycle_queue_results[4];
unsigned int open_cfw_test_display_lifecycle_queue_result_count;
unsigned int open_cfw_test_display_lifecycle_queue_calls;
void *open_cfw_test_display_lifecycle_queues[4];
unsigned int open_cfw_test_display_lifecycle_messages[4][9];
unsigned int open_cfw_test_display_lifecycle_priorities[4];
unsigned int open_cfw_test_display_lifecycle_timeouts[4];
unsigned int open_cfw_test_display_lifecycle_flag_values[16];
unsigned int open_cfw_test_display_lifecycle_flag_value_count;
unsigned int open_cfw_test_display_lifecycle_flag_calls;
unsigned int open_cfw_test_display_lifecycle_log_calls;
unsigned int open_cfw_test_display_lifecycle_log_levels[8];
const void *open_cfw_test_display_lifecycle_log_tags[8];
const void *open_cfw_test_display_lifecycle_log_files[8];
const void *open_cfw_test_display_lifecycle_log_functions[8];
unsigned int open_cfw_test_display_lifecycle_log_lines[8];
const void *open_cfw_test_display_lifecycle_log_formats[8];
unsigned int open_cfw_test_display_lifecycle_backend_calls;
unsigned int open_cfw_test_display_lifecycle_backend_masks[8];
const void *open_cfw_test_display_lifecycle_backend_formats[8];
const void *open_cfw_test_display_lifecycle_backend_duplicate_formats[8];
unsigned int open_cfw_test_display_lifecycle_trace_count;
unsigned int open_cfw_test_display_lifecycle_trace[64];

static void open_cfw_test_display_lifecycle_record(unsigned int event)
{
    unsigned int index = open_cfw_test_display_lifecycle_trace_count++;

    if (index < 64U) {
        open_cfw_test_display_lifecycle_trace[index] = event;
    }
}

int open_cfw_test_display_lifecycle_running(void)
{
    open_cfw_test_display_lifecycle_record(1U);
    open_cfw_test_display_lifecycle_running_calls += 1U;
    return open_cfw_test_display_lifecycle_running_result;
}

int open_cfw_test_display_lifecycle_queue_send(
    void *queue,
    const void *message,
    unsigned int priority,
    unsigned int timeout
)
{
    const unsigned int *words = message;
    unsigned int index = open_cfw_test_display_lifecycle_queue_calls++;
    unsigned int word;
    unsigned int result_index = index;

    open_cfw_test_display_lifecycle_record(2U);
    if (index < 4U) {
        open_cfw_test_display_lifecycle_queues[index] = queue;
        for (word = 0U; word < 9U; word += 1U) {
            open_cfw_test_display_lifecycle_messages[index][word] =
                words[word];
        }
        open_cfw_test_display_lifecycle_priorities[index] = priority;
        open_cfw_test_display_lifecycle_timeouts[index] = timeout;
    }
    if (open_cfw_test_display_lifecycle_queue_result_count == 0U) {
        return 0;
    }
    if (result_index >= open_cfw_test_display_lifecycle_queue_result_count) {
        result_index =
            open_cfw_test_display_lifecycle_queue_result_count - 1U;
    }
    return open_cfw_test_display_lifecycle_queue_results[result_index];
}

unsigned int open_cfw_test_display_lifecycle_log_flags(void)
{
    unsigned int index = open_cfw_test_display_lifecycle_flag_calls++;

    open_cfw_test_display_lifecycle_record(3U);
    if (open_cfw_test_display_lifecycle_flag_value_count == 0U) {
        return 0U;
    }
    if (index >= open_cfw_test_display_lifecycle_flag_value_count) {
        index = open_cfw_test_display_lifecycle_flag_value_count - 1U;
    }
    return open_cfw_test_display_lifecycle_flag_values[index];
}

void open_cfw_test_display_lifecycle_log(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    unsigned int index = open_cfw_test_display_lifecycle_log_calls++;

    open_cfw_test_display_lifecycle_record(4U);
    if (index < 8U) {
        open_cfw_test_display_lifecycle_log_levels[index] = level;
        open_cfw_test_display_lifecycle_log_tags[index] = tag;
        open_cfw_test_display_lifecycle_log_files[index] = file;
        open_cfw_test_display_lifecycle_log_functions[index] = function;
        open_cfw_test_display_lifecycle_log_lines[index] = line;
        open_cfw_test_display_lifecycle_log_formats[index] = format;
    }
}

void open_cfw_test_display_lifecycle_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    unsigned int index = open_cfw_test_display_lifecycle_backend_calls++;

    open_cfw_test_display_lifecycle_record(5U);
    if (index < 8U) {
        open_cfw_test_display_lifecycle_backend_masks[index] = mask;
        open_cfw_test_display_lifecycle_backend_formats[index] = format;
        open_cfw_test_display_lifecycle_backend_duplicate_formats[index] =
            duplicate_format;
    }
}

#define OPEN_CFW_DISPLAY_LIFECYCLE_ACTIVE \
    open_cfw_test_display_lifecycle_active
#define OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_HANDLE \
    open_cfw_test_display_lifecycle_queue_handle
#define OPEN_CFW_DISPLAY_LIFECYCLE_RUNNING() \
    open_cfw_test_display_lifecycle_running()
#define OPEN_CFW_DISPLAY_LIFECYCLE_QUEUE_SEND( \
    queue, \
    message, \
    priority, \
    timeout \
) \
    open_cfw_test_display_lifecycle_queue_send( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    )
#define OPEN_CFW_DISPLAY_LIFECYCLE_LOG_FLAGS() \
    open_cfw_test_display_lifecycle_log_flags()
#define OPEN_CFW_DISPLAY_LIFECYCLE_LOG open_cfw_test_display_lifecycle_log
#define OPEN_CFW_DISPLAY_LIFECYCLE_BACKEND_LOG \
    open_cfw_test_display_lifecycle_backend_log

#include "../../components/apollo_main/core_overlay/display_lifecycle.c"
