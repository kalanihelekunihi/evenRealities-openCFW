/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native queue, backend, diagnostic, and wait fixture for BLE TX dispatch.
 */

#define OPEN_CFW_TEST_BLE_MSGTX_QUEUE_GET 1U
#define OPEN_CFW_TEST_BLE_MSGTX_COMMAND_ONE 2U
#define OPEN_CFW_TEST_BLE_MSGTX_COMMAND_TWO_READY 3U
#define OPEN_CFW_TEST_BLE_MSGTX_COMMAND_TWO 4U
#define OPEN_CFW_TEST_BLE_MSGTX_COMMAND_FOUR 5U
#define OPEN_CFW_TEST_BLE_MSGTX_COMMAND_EIGHT 6U
#define OPEN_CFW_TEST_BLE_MSGTX_FREE 7U
#define OPEN_CFW_TEST_BLE_MSGTX_LEVEL 8U
#define OPEN_CFW_TEST_BLE_MSGTX_LOG 9U
#define OPEN_CFW_TEST_BLE_MSGTX_TRACE 10U
#define OPEN_CFW_TEST_BLE_MSGTX_STAGE 11U
#define OPEN_CFW_TEST_BLE_MSGTX_WAIT 12U
#define OPEN_CFW_TEST_BLE_MSGTX_CONTINUE 13U

struct open_cfw_test_ble_msgtx_dispatch_state_type {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
};

struct open_cfw_test_ble_msgtx_dispatch_message_type {
    unsigned int command;
    unsigned int length;
    unsigned char enabled;
    unsigned char argument_1;
    unsigned char argument_2;
    unsigned char data[8];
};

struct open_cfw_test_ble_msgtx_dispatch_state_type
    open_cfw_test_ble_msgtx_dispatch_state;
struct open_cfw_test_ble_msgtx_dispatch_message_type
    open_cfw_test_ble_msgtx_dispatch_messages[8];
void *open_cfw_test_ble_msgtx_queue_messages[16];
unsigned int open_cfw_test_ble_msgtx_queue_statuses[16];
unsigned int open_cfw_test_ble_msgtx_queue_count;
unsigned int open_cfw_test_ble_msgtx_queue_index;
unsigned int open_cfw_test_ble_msgtx_queue_handle;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_queue_priority;
unsigned int open_cfw_test_ble_msgtx_queue_timeout;
unsigned int open_cfw_test_ble_msgtx_queue_count_values[8];
unsigned int open_cfw_test_ble_msgtx_queue_count_count;
unsigned int open_cfw_test_ble_msgtx_queue_count_index;
unsigned int open_cfw_test_ble_msgtx_events[64];
unsigned int open_cfw_test_ble_msgtx_event_count;
unsigned int open_cfw_test_ble_msgtx_command_one_arguments[5];
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_command_one_data;
unsigned int open_cfw_test_ble_msgtx_command_two_ready_result;
unsigned int open_cfw_test_ble_msgtx_command_two_ready_argument;
unsigned int open_cfw_test_ble_msgtx_command_two_length;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_command_two_data;
unsigned int open_cfw_test_ble_msgtx_command_data_arguments[4];
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_command_data_pointer;
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_freed[16];
unsigned int open_cfw_test_ble_msgtx_free_count;
unsigned int open_cfw_test_ble_msgtx_level_values[16];
unsigned int open_cfw_test_ble_msgtx_level_count;
unsigned int open_cfw_test_ble_msgtx_level_index;
unsigned int open_cfw_test_ble_msgtx_log_arguments[6];
unsigned int open_cfw_test_ble_msgtx_log_extra_arguments[2];
unsigned int open_cfw_test_ble_msgtx_trace_arguments[3];
unsigned int open_cfw_test_ble_msgtx_trace_extra_arguments[2];
unsigned int open_cfw_test_ble_msgtx_stage_index;
unsigned int open_cfw_test_ble_msgtx_wait_timeout;
unsigned int open_cfw_test_ble_msgtx_wait_calls;
unsigned int open_cfw_test_ble_msgtx_continue_result;

static void open_cfw_test_ble_msgtx_record(unsigned int event)
{
    open_cfw_test_ble_msgtx_events[
        open_cfw_test_ble_msgtx_event_count++
    ] = event;
}

void open_cfw_test_ble_msgtx_dispatch_reset(void)
{
    unsigned int index;

    open_cfw_test_ble_msgtx_dispatch_state.reserved_0 = 0x11111111U;
    open_cfw_test_ble_msgtx_dispatch_state.reserved_4 = 0x22222222U;
    open_cfw_test_ble_msgtx_dispatch_state.thread = 0x33333333U;
    open_cfw_test_ble_msgtx_dispatch_state.queue = 0x44444444U;
    open_cfw_test_ble_msgtx_queue_count = 0U;
    open_cfw_test_ble_msgtx_queue_index = 0U;
    open_cfw_test_ble_msgtx_queue_handle = 0U;
    open_cfw_test_ble_msgtx_queue_priority = 1U;
    open_cfw_test_ble_msgtx_queue_timeout = 1U;
    open_cfw_test_ble_msgtx_queue_count_count = 0U;
    open_cfw_test_ble_msgtx_queue_count_index = 0U;
    open_cfw_test_ble_msgtx_event_count = 0U;
    open_cfw_test_ble_msgtx_command_two_ready_result = 0U;
    open_cfw_test_ble_msgtx_command_two_ready_argument = 0U;
    open_cfw_test_ble_msgtx_command_two_length = 0U;
    open_cfw_test_ble_msgtx_command_two_data = 0U;
    open_cfw_test_ble_msgtx_free_count = 0U;
    open_cfw_test_ble_msgtx_level_count = 0U;
    open_cfw_test_ble_msgtx_level_index = 0U;
    open_cfw_test_ble_msgtx_stage_index = 0U;
    open_cfw_test_ble_msgtx_wait_timeout = 0U;
    open_cfw_test_ble_msgtx_wait_calls = 0U;
    open_cfw_test_ble_msgtx_continue_result = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_msgtx_queue_messages[index] = (void *)0;
        open_cfw_test_ble_msgtx_queue_statuses[index] = 1U;
        open_cfw_test_ble_msgtx_freed[index] = 0U;
        open_cfw_test_ble_msgtx_level_values[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_msgtx_queue_count_values[index] = 0U;
        open_cfw_test_ble_msgtx_dispatch_messages[index].command = 0U;
        open_cfw_test_ble_msgtx_dispatch_messages[index].length = 0U;
        open_cfw_test_ble_msgtx_dispatch_messages[index].enabled = 0U;
        open_cfw_test_ble_msgtx_dispatch_messages[index].argument_1 = 0U;
        open_cfw_test_ble_msgtx_dispatch_messages[index].argument_2 = 0U;
    }
}

unsigned int open_cfw_test_ble_msgtx_queue_count_backend(void *queue)
{
    unsigned int index = open_cfw_test_ble_msgtx_queue_count_index++;

    open_cfw_test_ble_msgtx_queue_handle =
        (unsigned int)(__UINTPTR_TYPE__)queue;
    if (index < open_cfw_test_ble_msgtx_queue_count_count) {
        return open_cfw_test_ble_msgtx_queue_count_values[index];
    }
    return 0U;
}

unsigned int open_cfw_test_ble_msgtx_queue_get(
    void *queue,
    void **message,
    unsigned char *priority,
    unsigned int timeout
)
{
    unsigned int index = open_cfw_test_ble_msgtx_queue_index++;
    unsigned int status = 1U;

    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_QUEUE_GET);
    open_cfw_test_ble_msgtx_queue_handle =
        (unsigned int)(__UINTPTR_TYPE__)queue;
    open_cfw_test_ble_msgtx_queue_priority = (__UINTPTR_TYPE__)priority;
    open_cfw_test_ble_msgtx_queue_timeout = timeout;
    if (index < open_cfw_test_ble_msgtx_queue_count) {
        status = open_cfw_test_ble_msgtx_queue_statuses[index];
        if (status == 0U) {
            *message = open_cfw_test_ble_msgtx_queue_messages[index];
        }
    }
    return status;
}

void open_cfw_test_ble_msgtx_message_free(void *message)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_FREE);
    open_cfw_test_ble_msgtx_freed[
        open_cfw_test_ble_msgtx_free_count++
    ] = (__UINTPTR_TYPE__)message;
}

void open_cfw_test_ble_msgtx_command_one(
    unsigned int channel,
    unsigned int enabled,
    unsigned int argument_1,
    unsigned int argument_2,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_COMMAND_ONE);
    open_cfw_test_ble_msgtx_command_one_arguments[0] = channel;
    open_cfw_test_ble_msgtx_command_one_arguments[1] = enabled;
    open_cfw_test_ble_msgtx_command_one_arguments[2] = argument_1;
    open_cfw_test_ble_msgtx_command_one_arguments[3] = argument_2;
    open_cfw_test_ble_msgtx_command_one_arguments[4] = length;
    open_cfw_test_ble_msgtx_command_one_data = (__UINTPTR_TYPE__)data;
}

unsigned int open_cfw_test_ble_msgtx_command_two_ready(
    unsigned int value
)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_COMMAND_TWO_READY
    );
    open_cfw_test_ble_msgtx_command_two_ready_argument = value;
    return open_cfw_test_ble_msgtx_command_two_ready_result;
}

void open_cfw_test_ble_msgtx_command_two(
    const void *data,
    unsigned int length
)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_COMMAND_TWO);
    open_cfw_test_ble_msgtx_command_two_data = (__UINTPTR_TYPE__)data;
    open_cfw_test_ble_msgtx_command_two_length = length;
}

void open_cfw_test_ble_msgtx_command_data(
    unsigned int event,
    unsigned int enabled,
    unsigned int argument_1,
    unsigned int argument_2,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_ble_msgtx_record(event);
    open_cfw_test_ble_msgtx_command_data_arguments[0] = enabled;
    open_cfw_test_ble_msgtx_command_data_arguments[1] = argument_1;
    open_cfw_test_ble_msgtx_command_data_arguments[2] = argument_2;
    open_cfw_test_ble_msgtx_command_data_arguments[3] = length;
    open_cfw_test_ble_msgtx_command_data_pointer =
        (__UINTPTR_TYPE__)data;
}

unsigned int open_cfw_test_ble_msgtx_log_level(void)
{
    unsigned int index = open_cfw_test_ble_msgtx_level_index++;
    unsigned int value = 0U;

    if (index < open_cfw_test_ble_msgtx_level_count) {
        value = open_cfw_test_ble_msgtx_level_values[index];
    }
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_LEVEL);
    return value;
}

void open_cfw_test_ble_msgtx_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message
)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_LOG);
    open_cfw_test_ble_msgtx_log_arguments[0] = level;
    open_cfw_test_ble_msgtx_log_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)module;
    open_cfw_test_ble_msgtx_log_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)file;
    open_cfw_test_ble_msgtx_log_arguments[3] =
        (unsigned int)(__UINTPTR_TYPE__)function;
    open_cfw_test_ble_msgtx_log_arguments[4] = line;
    open_cfw_test_ble_msgtx_log_arguments[5] =
        (unsigned int)(__UINTPTR_TYPE__)message;
}

void open_cfw_test_ble_msgtx_log_one(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int argument
)
{
    open_cfw_test_ble_msgtx_log(
        level,
        module,
        file,
        function,
        line,
        message
    );
    open_cfw_test_ble_msgtx_log_extra_arguments[0] = argument;
}

void open_cfw_test_ble_msgtx_log_two(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int argument_1,
    unsigned int argument_2
)
{
    open_cfw_test_ble_msgtx_log(
        level,
        module,
        file,
        function,
        line,
        message
    );
    open_cfw_test_ble_msgtx_log_extra_arguments[0] = argument_1;
    open_cfw_test_ble_msgtx_log_extra_arguments[1] = argument_2;
}

void open_cfw_test_ble_msgtx_trace(
    unsigned int level,
    const void *format,
    const void *argument
)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_TRACE);
    open_cfw_test_ble_msgtx_trace_arguments[0] = level;
    open_cfw_test_ble_msgtx_trace_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)format;
    open_cfw_test_ble_msgtx_trace_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)argument;
}

void open_cfw_test_ble_msgtx_trace_one(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int value
)
{
    open_cfw_test_ble_msgtx_trace(level, format, argument);
    open_cfw_test_ble_msgtx_trace_extra_arguments[0] = value;
}

void open_cfw_test_ble_msgtx_trace_two(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int value_1,
    unsigned int value_2
)
{
    open_cfw_test_ble_msgtx_trace(level, format, argument);
    open_cfw_test_ble_msgtx_trace_extra_arguments[0] = value_1;
    open_cfw_test_ble_msgtx_trace_extra_arguments[1] = value_2;
}

void open_cfw_test_ble_msgtx_wait_stage(unsigned int index)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_STAGE);
    open_cfw_test_ble_msgtx_stage_index = index;
}

void open_cfw_test_ble_msgtx_wait_backend(unsigned int timeout)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_WAIT);
    open_cfw_test_ble_msgtx_wait_timeout = timeout;
    ++open_cfw_test_ble_msgtx_wait_calls;
}

unsigned int open_cfw_test_ble_msgtx_wait_loop_continue(void)
{
    open_cfw_test_ble_msgtx_record(OPEN_CFW_TEST_BLE_MSGTX_CONTINUE);
    return open_cfw_test_ble_msgtx_continue_result;
}

#define OPEN_CFW_BLE_MSGTX_DISPATCH_STATE \
    ((volatile open_cfw_ble_msgtx_dispatch_state *) \
        &open_cfw_test_ble_msgtx_dispatch_state)
#define OPEN_CFW_BLE_MSGTX_QUEUE_GET(queue, message, priority, timeout) \
    open_cfw_test_ble_msgtx_queue_get( \
        (queue), \
        (void **)(message), \
        (priority), \
        (timeout) \
    )
#define OPEN_CFW_BLE_MSGTX_QUEUE_COUNT(queue) \
    open_cfw_test_ble_msgtx_queue_count_backend((queue))
#define OPEN_CFW_BLE_MSGTX_MESSAGE_FREE(message) \
    open_cfw_test_ble_msgtx_message_free((message))
#define OPEN_CFW_BLE_MSGTX_COMMAND_ONE( \
    channel, enabled, argument_1, argument_2, data, length \
) \
    open_cfw_test_ble_msgtx_command_one( \
        (channel), \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    )
#define OPEN_CFW_BLE_MSGTX_COMMAND_TWO_READY(value) \
    open_cfw_test_ble_msgtx_command_two_ready((value))
#define OPEN_CFW_BLE_MSGTX_COMMAND_TWO(data, length) \
    open_cfw_test_ble_msgtx_command_two((data), (length))
#define OPEN_CFW_BLE_MSGTX_COMMAND_FOUR( \
    enabled, argument_1, argument_2, data, length \
) \
    open_cfw_test_ble_msgtx_command_data( \
        OPEN_CFW_TEST_BLE_MSGTX_COMMAND_FOUR, \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    )
#define OPEN_CFW_BLE_MSGTX_COMMAND_EIGHT( \
    enabled, argument_1, argument_2, data, length \
) \
    open_cfw_test_ble_msgtx_command_data( \
        OPEN_CFW_TEST_BLE_MSGTX_COMMAND_EIGHT, \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (data), \
        (length) \
    )
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_LEVEL() \
    open_cfw_test_ble_msgtx_log_level()
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG( \
    level, module, file, function, line, message \
) \
    open_cfw_test_ble_msgtx_log( \
        (level), (module), (file), (function), (line), (message) \
    )
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_ONE( \
    level, module, file, function, line, message, argument \
) \
    open_cfw_test_ble_msgtx_log_one( \
        (level), (module), (file), (function), (line), (message), \
        (argument) \
    )
#define OPEN_CFW_BLE_MSGTX_DISPATCH_LOG_TWO( \
    level, module, file, function, line, message, argument_1, argument_2 \
) \
    open_cfw_test_ble_msgtx_log_two( \
        (level), (module), (file), (function), (line), (message), \
        (argument_1), (argument_2) \
    )
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE(level, format, argument) \
    open_cfw_test_ble_msgtx_trace((level), (format), (argument))
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_ONE( \
    level, format, argument, value \
) \
    open_cfw_test_ble_msgtx_trace_one( \
        (level), (format), (argument), (value) \
    )
#define OPEN_CFW_BLE_MSGTX_DISPATCH_TRACE_TWO( \
    level, format, argument, value_1, value_2 \
) \
    open_cfw_test_ble_msgtx_trace_two( \
        (level), (format), (argument), (value_1), (value_2) \
    )
#define OPEN_CFW_BLE_MSGTX_WAIT_STAGE(index) \
    open_cfw_test_ble_msgtx_wait_stage((index))
#define OPEN_CFW_BLE_MSGTX_WAIT_BACKEND(timeout) \
    open_cfw_test_ble_msgtx_wait_backend((timeout))
#define OPEN_CFW_BLE_MSGTX_WAIT_LOOP_CONTINUE() \
    open_cfw_test_ble_msgtx_wait_loop_continue()

#include "../../components/apollo_main/core_overlay/ble_msgtx_dispatch.c"
