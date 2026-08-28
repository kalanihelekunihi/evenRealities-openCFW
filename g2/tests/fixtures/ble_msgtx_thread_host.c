/*
 * SPDX-License-Identifier: MIT
 *
 * Native lifecycle, flag-wait, dispatch, and diagnostic fixture for the BLE
 * message-transmit thread entry.
 */

#define OPEN_CFW_TEST_BLE_MSGTX_LIMIT 32U

unsigned int open_cfw_test_ble_msgtx_events[
    OPEN_CFW_TEST_BLE_MSGTX_LIMIT
];
unsigned int open_cfw_test_ble_msgtx_event_values[
    OPEN_CFW_TEST_BLE_MSGTX_LIMIT
];
unsigned int open_cfw_test_ble_msgtx_event_count;
unsigned int open_cfw_test_ble_msgtx_wait_values[
    OPEN_CFW_TEST_BLE_MSGTX_LIMIT
];
unsigned int open_cfw_test_ble_msgtx_wait_value_count;
unsigned int open_cfw_test_ble_msgtx_wait_index;
unsigned int open_cfw_test_ble_msgtx_level_values[
    OPEN_CFW_TEST_BLE_MSGTX_LIMIT
];
unsigned int open_cfw_test_ble_msgtx_level_value_count;
unsigned int open_cfw_test_ble_msgtx_level_index;
unsigned int open_cfw_test_ble_msgtx_wait_flags;
unsigned int open_cfw_test_ble_msgtx_wait_options;
unsigned int open_cfw_test_ble_msgtx_wait_timeout;
unsigned int open_cfw_test_ble_msgtx_continue_result;
unsigned int open_cfw_test_ble_msgtx_log_arguments[6];
unsigned int open_cfw_test_ble_msgtx_trace_arguments[3];

enum {
    OPEN_CFW_TEST_BLE_MSGTX_STAGE_ENTER = 1U,
    OPEN_CFW_TEST_BLE_MSGTX_QUEUE_INITIALIZE = 2U,
    OPEN_CFW_TEST_BLE_MSGTX_APPLICATION_INITIALIZE = 3U,
    OPEN_CFW_TEST_BLE_MSGTX_THREAD_INITIALIZE = 4U,
    OPEN_CFW_TEST_BLE_MSGTX_STAGE_LEAVE = 5U,
    OPEN_CFW_TEST_BLE_MSGTX_WAIT = 6U,
    OPEN_CFW_TEST_BLE_MSGTX_DISPATCH = 7U,
    OPEN_CFW_TEST_BLE_MSGTX_LEVEL = 8U,
    OPEN_CFW_TEST_BLE_MSGTX_LOG = 9U,
    OPEN_CFW_TEST_BLE_MSGTX_TRACE = 10U,
    OPEN_CFW_TEST_BLE_MSGTX_CONTINUE = 11U
};

static void open_cfw_test_ble_msgtx_record(
    unsigned int event,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_ble_msgtx_event_count;

    if (index < OPEN_CFW_TEST_BLE_MSGTX_LIMIT) {
        open_cfw_test_ble_msgtx_events[index] = event;
        open_cfw_test_ble_msgtx_event_values[index] = value;
    }
    open_cfw_test_ble_msgtx_event_count = index + 1U;
}

void open_cfw_test_ble_msgtx_reset(void)
{
    unsigned int index;

    for (index = 0U; index < OPEN_CFW_TEST_BLE_MSGTX_LIMIT; ++index) {
        open_cfw_test_ble_msgtx_events[index] = 0U;
        open_cfw_test_ble_msgtx_event_values[index] = 0U;
        open_cfw_test_ble_msgtx_wait_values[index] = 0U;
        open_cfw_test_ble_msgtx_level_values[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_ble_msgtx_log_arguments[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_ble_msgtx_trace_arguments[index] = 0U;
    }
    open_cfw_test_ble_msgtx_event_count = 0U;
    open_cfw_test_ble_msgtx_wait_value_count = 0U;
    open_cfw_test_ble_msgtx_wait_index = 0U;
    open_cfw_test_ble_msgtx_level_value_count = 0U;
    open_cfw_test_ble_msgtx_level_index = 0U;
    open_cfw_test_ble_msgtx_wait_flags = 0U;
    open_cfw_test_ble_msgtx_wait_options = 0U;
    open_cfw_test_ble_msgtx_wait_timeout = 0U;
    open_cfw_test_ble_msgtx_continue_result = 0U;
}

void open_cfw_test_ble_msgtx_stage_enter(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_STAGE_ENTER,
        0U
    );
}

void open_cfw_test_ble_msgtx_queue_initialize(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_QUEUE_INITIALIZE,
        0U
    );
}

void open_cfw_test_ble_msgtx_application_initialize(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_APPLICATION_INITIALIZE,
        0U
    );
}

void open_cfw_test_ble_msgtx_thread_initialize(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_THREAD_INITIALIZE,
        0U
    );
}

void open_cfw_test_ble_msgtx_stage_leave(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_STAGE_LEAVE,
        0U
    );
}

unsigned int open_cfw_test_ble_msgtx_wait(
    unsigned int flags,
    unsigned int options,
    unsigned int timeout
)
{
    unsigned int index = open_cfw_test_ble_msgtx_wait_index++;
    unsigned int value = 0U;

    open_cfw_test_ble_msgtx_wait_flags = flags;
    open_cfw_test_ble_msgtx_wait_options = options;
    open_cfw_test_ble_msgtx_wait_timeout = timeout;
    if (index < open_cfw_test_ble_msgtx_wait_value_count) {
        value = open_cfw_test_ble_msgtx_wait_values[index];
    }
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_WAIT,
        value
    );
    return value;
}

void open_cfw_test_ble_msgtx_dispatch(unsigned int flags)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_DISPATCH,
        flags
    );
}

unsigned int open_cfw_test_ble_msgtx_log_level(void)
{
    unsigned int index = open_cfw_test_ble_msgtx_level_index++;
    unsigned int value = 0U;

    if (index < open_cfw_test_ble_msgtx_level_value_count) {
        value = open_cfw_test_ble_msgtx_level_values[index];
    }
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_LEVEL,
        value
    );
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
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_LOG,
        level
    );
}

void open_cfw_test_ble_msgtx_trace(
    unsigned int level,
    const void *format,
    const void *argument
)
{
    open_cfw_test_ble_msgtx_trace_arguments[0] = level;
    open_cfw_test_ble_msgtx_trace_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)format;
    open_cfw_test_ble_msgtx_trace_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)argument;
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_TRACE,
        level
    );
}

unsigned int open_cfw_test_ble_msgtx_loop_continue(void)
{
    open_cfw_test_ble_msgtx_record(
        OPEN_CFW_TEST_BLE_MSGTX_CONTINUE,
        open_cfw_test_ble_msgtx_continue_result
    );
    return open_cfw_test_ble_msgtx_continue_result;
}

#define OPEN_CFW_BLE_MSGTX_STAGE_ENTER() \
    open_cfw_test_ble_msgtx_stage_enter()
#define OPEN_CFW_BLE_MSGTX_QUEUE_INITIALIZE() \
    open_cfw_test_ble_msgtx_queue_initialize()
#define OPEN_CFW_BLE_MSGTX_APPLICATION_INITIALIZE() \
    open_cfw_test_ble_msgtx_application_initialize()
#define OPEN_CFW_BLE_MSGTX_THREAD_INITIALIZE() \
    open_cfw_test_ble_msgtx_thread_initialize()
#define OPEN_CFW_BLE_MSGTX_STAGE_LEAVE() \
    open_cfw_test_ble_msgtx_stage_leave()
#define OPEN_CFW_BLE_MSGTX_WAIT(flags, options, timeout) \
    open_cfw_test_ble_msgtx_wait((flags), (options), (timeout))
#define OPEN_CFW_BLE_MSGTX_DISPATCH(flags) \
    open_cfw_test_ble_msgtx_dispatch((flags))
#define OPEN_CFW_BLE_MSGTX_LOG_LEVEL() \
    open_cfw_test_ble_msgtx_log_level()
#define OPEN_CFW_BLE_MSGTX_LOG( \
    level, module, file, function, line, message \
) \
    open_cfw_test_ble_msgtx_log( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    )
#define OPEN_CFW_BLE_MSGTX_TRACE(level, format, argument) \
    open_cfw_test_ble_msgtx_trace((level), (format), (argument))
#define OPEN_CFW_BLE_MSGTX_LOOP_CONTINUE() \
    open_cfw_test_ble_msgtx_loop_continue()

#include "../../components/apollo_main/core_overlay/ble_msgtx_thread.c"
