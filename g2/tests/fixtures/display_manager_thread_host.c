#include <stdarg.h>

void *open_cfw_test_display_manager_queue_handle;
unsigned int open_cfw_test_display_manager_active;
unsigned int open_cfw_test_display_manager_trace_count;
unsigned int open_cfw_test_display_manager_trace[64];
unsigned int open_cfw_test_display_manager_queue_get_calls;
int open_cfw_test_display_manager_queue_get_results[4];
unsigned int open_cfw_test_display_manager_queue_get_result_count;
unsigned int open_cfw_test_display_manager_queue_get_zero_words[4];
unsigned int open_cfw_test_display_manager_message[9];
void *open_cfw_test_display_manager_queue_get_queue;
unsigned int open_cfw_test_display_manager_queue_get_priority;
unsigned int open_cfw_test_display_manager_queue_get_timeout;
int open_cfw_test_display_manager_gate_result;
unsigned int open_cfw_test_display_manager_command3_words[6];
unsigned int open_cfw_test_display_manager_query_value;
unsigned int open_cfw_test_display_manager_query_first_before;
unsigned int open_cfw_test_display_manager_query_second_before;
unsigned int open_cfw_test_display_manager_query_first_result;
unsigned int open_cfw_test_display_manager_query_second_result;
unsigned int open_cfw_test_display_manager_query_result_value;
unsigned int open_cfw_test_display_manager_query_result_second;
unsigned int open_cfw_test_display_manager_query_result_first;
unsigned int open_cfw_test_display_manager_command6_gate_value;
unsigned int open_cfw_test_display_manager_command6_gate_result;
unsigned int open_cfw_test_display_manager_command8_value;
unsigned int open_cfw_test_display_manager_flag_calls;
unsigned int open_cfw_test_display_manager_flag_values[3];
unsigned int open_cfw_test_display_manager_log_calls;
unsigned int open_cfw_test_display_manager_log_level;
const void *open_cfw_test_display_manager_log_tag;
const void *open_cfw_test_display_manager_log_file;
const void *open_cfw_test_display_manager_log_function;
unsigned int open_cfw_test_display_manager_log_line;
const void *open_cfw_test_display_manager_log_format;
unsigned int open_cfw_test_display_manager_log_command;
unsigned int open_cfw_test_display_manager_backend_calls;
unsigned int open_cfw_test_display_manager_backend_mask;
const void *open_cfw_test_display_manager_backend_format;
const void *open_cfw_test_display_manager_backend_duplicate_format;
unsigned int open_cfw_test_display_manager_backend_command;

static void open_cfw_test_display_manager_record(unsigned int value)
{
    unsigned int index = open_cfw_test_display_manager_trace_count++;

    if (index < 64U) {
        open_cfw_test_display_manager_trace[index] = value;
    }
}

void open_cfw_test_display_manager_queue_initialize(void)
{
    open_cfw_test_display_manager_record(1U);
}

void open_cfw_test_display_manager_resource_acquire(void)
{
    open_cfw_test_display_manager_record(2U);
}

void open_cfw_test_display_manager_interface_initialize(void)
{
    open_cfw_test_display_manager_record(3U);
}

void open_cfw_test_display_manager_resource_release(void)
{
    open_cfw_test_display_manager_record(4U);
}

void open_cfw_test_display_manager_timer_initialize(void)
{
    open_cfw_test_display_manager_record(5U);
}

int open_cfw_test_display_manager_queue_get(
    void *queue,
    void *message,
    unsigned int priority,
    unsigned int timeout
)
{
    unsigned int *words = message;
    unsigned int call = open_cfw_test_display_manager_queue_get_calls++;
    unsigned int index;
    unsigned int zero_words = 0U;
    int result;

    open_cfw_test_display_manager_record(6U);
    open_cfw_test_display_manager_queue_get_queue = queue;
    open_cfw_test_display_manager_queue_get_priority = priority;
    open_cfw_test_display_manager_queue_get_timeout = timeout;
    for (index = 0U; index < 9U; index += 1U) {
        if (words[index] == 0U) {
            zero_words += 1U;
        }
    }
    if (call < 4U) {
        open_cfw_test_display_manager_queue_get_zero_words[call] = zero_words;
    }
    if (call < open_cfw_test_display_manager_queue_get_result_count) {
        result = open_cfw_test_display_manager_queue_get_results[call];
    } else {
        result = 0;
    }
    if (result == 0) {
        for (index = 0U; index < 9U; index += 1U) {
            words[index] = open_cfw_test_display_manager_message[index];
        }
    } else {
        for (index = 0U; index < 9U; index += 1U) {
            words[index] = 0xDEADBEEFU;
        }
    }
    return result;
}

void open_cfw_test_display_manager_enter(void)
{
    open_cfw_test_display_manager_record(7U);
}

void open_cfw_test_display_manager_prepare(void)
{
    open_cfw_test_display_manager_record(8U);
}

void open_cfw_test_display_manager_display_unlock(void)
{
    open_cfw_test_display_manager_record(9U);
}

int open_cfw_test_display_manager_gate(void)
{
    open_cfw_test_display_manager_record(10U);
    return open_cfw_test_display_manager_gate_result;
}

void open_cfw_test_display_manager_leave(void)
{
    open_cfw_test_display_manager_record(11U);
}

void open_cfw_test_display_manager_command0(void)
{
    open_cfw_test_display_manager_record(12U);
}

void open_cfw_test_display_manager_command1(void)
{
    open_cfw_test_display_manager_record(13U);
}

void open_cfw_test_display_manager_timer_start(void)
{
    open_cfw_test_display_manager_record(14U);
}

void open_cfw_test_display_manager_command2(void)
{
    open_cfw_test_display_manager_record(15U);
}

void open_cfw_test_display_manager_command3(
    unsigned int word1,
    unsigned int word2,
    unsigned int word3,
    unsigned int word4,
    unsigned int word5,
    unsigned int word6
)
{
    open_cfw_test_display_manager_record(16U);
    open_cfw_test_display_manager_command3_words[0] = word1;
    open_cfw_test_display_manager_command3_words[1] = word2;
    open_cfw_test_display_manager_command3_words[2] = word3;
    open_cfw_test_display_manager_command3_words[3] = word4;
    open_cfw_test_display_manager_command3_words[4] = word5;
    open_cfw_test_display_manager_command3_words[5] = word6;
}

void open_cfw_test_display_manager_query(
    unsigned int value,
    unsigned int *first,
    unsigned int *second
)
{
    open_cfw_test_display_manager_record(17U);
    open_cfw_test_display_manager_query_value = value;
    open_cfw_test_display_manager_query_first_before = *first;
    open_cfw_test_display_manager_query_second_before = *second;
    *first = open_cfw_test_display_manager_query_first_result;
    *second = open_cfw_test_display_manager_query_second_result;
}

void open_cfw_test_display_manager_query_result(
    unsigned int value,
    unsigned int second,
    unsigned int first
)
{
    open_cfw_test_display_manager_record(18U);
    open_cfw_test_display_manager_query_result_value = value;
    open_cfw_test_display_manager_query_result_second = second;
    open_cfw_test_display_manager_query_result_first = first;
}

void open_cfw_test_display_manager_timer_stop(void)
{
    open_cfw_test_display_manager_record(19U);
}

void open_cfw_test_display_manager_command5(void)
{
    open_cfw_test_display_manager_record(20U);
}

unsigned int open_cfw_test_display_manager_command6_gate(
    unsigned int value
)
{
    open_cfw_test_display_manager_record(21U);
    open_cfw_test_display_manager_command6_gate_value = value;
    return open_cfw_test_display_manager_command6_gate_result;
}

void open_cfw_test_display_manager_command8(unsigned int value)
{
    open_cfw_test_display_manager_record(22U);
    open_cfw_test_display_manager_command8_value = value;
}

unsigned int open_cfw_test_display_manager_log_flags(void)
{
    unsigned int index = open_cfw_test_display_manager_flag_calls++;

    open_cfw_test_display_manager_record(23U);
    if (index >= 3U) {
        index = 2U;
    }
    return open_cfw_test_display_manager_flag_values[index];
}

void open_cfw_test_display_manager_log(
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

    open_cfw_test_display_manager_record(24U);
    open_cfw_test_display_manager_log_calls += 1U;
    open_cfw_test_display_manager_log_level = level;
    open_cfw_test_display_manager_log_tag = tag;
    open_cfw_test_display_manager_log_file = file;
    open_cfw_test_display_manager_log_function = function;
    open_cfw_test_display_manager_log_line = line;
    open_cfw_test_display_manager_log_format = format;
    open_cfw_test_display_manager_log_command = 0U;
    if (line == 0x117U) {
        va_start(arguments, format);
        open_cfw_test_display_manager_log_command =
            va_arg(arguments, unsigned int);
        va_end(arguments);
    }
}

void open_cfw_test_display_manager_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    va_list arguments;

    open_cfw_test_display_manager_record(25U);
    open_cfw_test_display_manager_backend_calls += 1U;
    open_cfw_test_display_manager_backend_mask = mask;
    open_cfw_test_display_manager_backend_format = format;
    open_cfw_test_display_manager_backend_duplicate_format =
        duplicate_format;
    open_cfw_test_display_manager_backend_command = 0U;
    if (mask == 0x08400000U) {
        va_start(arguments, duplicate_format);
        open_cfw_test_display_manager_backend_command =
            va_arg(arguments, unsigned int);
        va_end(arguments);
    }
}

#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_HANDLE \
    open_cfw_test_display_manager_queue_handle
#define OPEN_CFW_DISPLAY_MANAGER_ACTIVE \
    open_cfw_test_display_manager_active
#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_INITIALIZE() \
    open_cfw_test_display_manager_queue_initialize()
#define OPEN_CFW_DISPLAY_MANAGER_RESOURCE_ACQUIRE() \
    open_cfw_test_display_manager_resource_acquire()
#define OPEN_CFW_DISPLAY_MANAGER_INTERFACE_INITIALIZE() \
    open_cfw_test_display_manager_interface_initialize()
#define OPEN_CFW_DISPLAY_MANAGER_RESOURCE_RELEASE() \
    open_cfw_test_display_manager_resource_release()
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_INITIALIZE() \
    open_cfw_test_display_manager_timer_initialize()
#define OPEN_CFW_DISPLAY_MANAGER_QUEUE_GET(queue, message, priority, timeout) \
    open_cfw_test_display_manager_queue_get( \
        (queue), \
        (message), \
        (priority), \
        (timeout) \
    )
#define OPEN_CFW_DISPLAY_MANAGER_ENTER() \
    open_cfw_test_display_manager_enter()
#define OPEN_CFW_DISPLAY_MANAGER_PREPARE() \
    open_cfw_test_display_manager_prepare()
#define OPEN_CFW_DISPLAY_MANAGER_DISPLAY_UNLOCK() \
    open_cfw_test_display_manager_display_unlock()
#define OPEN_CFW_DISPLAY_MANAGER_GATE() \
    open_cfw_test_display_manager_gate()
#define OPEN_CFW_DISPLAY_MANAGER_LEAVE() \
    open_cfw_test_display_manager_leave()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND0() \
    open_cfw_test_display_manager_command0()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND1() \
    open_cfw_test_display_manager_command1()
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_START() \
    open_cfw_test_display_manager_timer_start()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND2() \
    open_cfw_test_display_manager_command2()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND3( \
    word1, \
    word2, \
    word3, \
    word4, \
    word5, \
    word6 \
) \
    open_cfw_test_display_manager_command3( \
        (word1), \
        (word2), \
        (word3), \
        (word4), \
        (word5), \
        (word6) \
    )
#define OPEN_CFW_DISPLAY_MANAGER_QUERY(value, first, second) \
    open_cfw_test_display_manager_query((value), (first), (second))
#define OPEN_CFW_DISPLAY_MANAGER_QUERY_RESULT(value, second, first) \
    open_cfw_test_display_manager_query_result((value), (second), (first))
#define OPEN_CFW_DISPLAY_MANAGER_TIMER_STOP() \
    open_cfw_test_display_manager_timer_stop()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND5() \
    open_cfw_test_display_manager_command5()
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND6_GATE(value) \
    open_cfw_test_display_manager_command6_gate(value)
#define OPEN_CFW_DISPLAY_MANAGER_COMMAND8(value) \
    open_cfw_test_display_manager_command8(value)
#define OPEN_CFW_DISPLAY_MANAGER_LOG_FLAGS() \
    open_cfw_test_display_manager_log_flags()
#define OPEN_CFW_DISPLAY_MANAGER_LOG open_cfw_test_display_manager_log
#define OPEN_CFW_DISPLAY_MANAGER_BACKEND_LOG \
    open_cfw_test_display_manager_backend_log
#define OPEN_CFW_DISPLAY_MANAGER_LOOP_CONTINUES() 0

#include "../../components/apollo_main/core_overlay/display_manager_thread.c"
