/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for BLE connection-parameter update scheduling.
 */

#include <stdarg.h>

unsigned int open_cfw_test_ble_connection_status(unsigned char);
void open_cfw_test_ble_connection_update(
    unsigned char,
    const unsigned short *
);
unsigned int open_cfw_test_ble_connection_log_level(void);
void open_cfw_test_ble_connection_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_connection_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

const volatile unsigned short *open_cfw_test_ble_connection_defaults_pointer;

#define OPEN_CFW_BLE_CONNECTION_DEFAULTS \
    open_cfw_test_ble_connection_defaults_pointer
#define OPEN_CFW_BLE_CONNECTION_STATUS(index) \
    open_cfw_test_ble_connection_status(index)
#define OPEN_CFW_BLE_CONNECTION_UPDATE(index, parameters) \
    open_cfw_test_ble_connection_update((index), (parameters))
#define OPEN_CFW_BLE_CONNECTION_LOG_LEVEL() \
    open_cfw_test_ble_connection_log_level()
#define OPEN_CFW_BLE_CONNECTION_LOG(...) \
    open_cfw_test_ble_connection_log(__VA_ARGS__)
#define OPEN_CFW_BLE_CONNECTION_TRACE(...) \
    open_cfw_test_ble_connection_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_schedule.c"

unsigned int open_cfw_test_ble_connection_levels[32];
unsigned int open_cfw_test_ble_connection_level_count;
unsigned int open_cfw_test_ble_connection_level_index;
unsigned int open_cfw_test_ble_connection_status_results[16];
unsigned int open_cfw_test_ble_connection_status_count;
unsigned int open_cfw_test_ble_connection_status_calls;
unsigned char open_cfw_test_ble_connection_status_indices[16];
unsigned short open_cfw_test_ble_connection_defaults[6];
unsigned int open_cfw_test_ble_connection_update_calls;
unsigned char open_cfw_test_ble_connection_update_index;
unsigned short open_cfw_test_ble_connection_update_parameters[6];
__UINTPTR_TYPE__ open_cfw_test_ble_connection_log_record[9];
unsigned int open_cfw_test_ble_connection_log_count;
__UINTPTR_TYPE__ open_cfw_test_ble_connection_trace_record[6];
unsigned int open_cfw_test_ble_connection_trace_count;
unsigned int open_cfw_test_ble_connection_remove_calls;
__UINTPTR_TYPE__ open_cfw_test_ble_connection_remove_callback;
unsigned int open_cfw_test_ble_connection_remove_result;
unsigned int open_cfw_test_ble_connection_push_calls;
__UINTPTR_TYPE__ open_cfw_test_ble_connection_push_callback;
__UINTPTR_TYPE__ open_cfw_test_ble_connection_push_argument;
unsigned int open_cfw_test_ble_connection_push_delay;

void open_cfw_test_ble_connection_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ble_connection_levels[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_connection_status_results[index] = 0U;
        open_cfw_test_ble_connection_status_indices[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_ble_connection_defaults[index] = 0U;
        open_cfw_test_ble_connection_update_parameters[index] = 0U;
        open_cfw_test_ble_connection_trace_record[index] = 0U;
    }
    for (index = 0U; index < 9U; ++index) {
        open_cfw_test_ble_connection_log_record[index] = 0U;
    }
    open_cfw_test_ble_connection_defaults_pointer =
        open_cfw_test_ble_connection_defaults;
    open_cfw_test_ble_connection_level_count = 0U;
    open_cfw_test_ble_connection_level_index = 0U;
    open_cfw_test_ble_connection_status_count = 0U;
    open_cfw_test_ble_connection_status_calls = 0U;
    open_cfw_test_ble_connection_update_calls = 0U;
    open_cfw_test_ble_connection_update_index = 0U;
    open_cfw_test_ble_connection_log_count = 0U;
    open_cfw_test_ble_connection_trace_count = 0U;
    open_cfw_test_ble_connection_remove_calls = 0U;
    open_cfw_test_ble_connection_remove_callback = 0U;
    open_cfw_test_ble_connection_remove_result = 0U;
    open_cfw_test_ble_connection_push_calls = 0U;
    open_cfw_test_ble_connection_push_callback = 0U;
    open_cfw_test_ble_connection_push_argument = 0U;
    open_cfw_test_ble_connection_push_delay = 0U;
}

unsigned int open_cfw_test_ble_connection_status(unsigned char index)
{
    unsigned int call = open_cfw_test_ble_connection_status_calls++;

    open_cfw_test_ble_connection_status_indices[call] = index;
    if (call < open_cfw_test_ble_connection_status_count) {
        return open_cfw_test_ble_connection_status_results[call];
    }
    return 0U;
}

unsigned int open_cfw_test_ble_connection_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_connection_level_index
        < open_cfw_test_ble_connection_level_count
    ) {
        value = open_cfw_test_ble_connection_levels[
            open_cfw_test_ble_connection_level_index
        ];
    }
    ++open_cfw_test_ble_connection_level_index;
    return value;
}

void open_cfw_test_ble_connection_update(
    unsigned char index,
    const unsigned short *parameters
)
{
    unsigned int offset;

    ++open_cfw_test_ble_connection_update_calls;
    open_cfw_test_ble_connection_update_index = index;
    for (offset = 0U; offset < 6U; ++offset) {
        open_cfw_test_ble_connection_update_parameters[offset] =
            parameters[offset];
    }
}

void open_cfw_test_ble_connection_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    va_list arguments;

    ++open_cfw_test_ble_connection_log_count;
    open_cfw_test_ble_connection_log_record[0] = level;
    open_cfw_test_ble_connection_log_record[1] =
        (__UINTPTR_TYPE__)module;
    open_cfw_test_ble_connection_log_record[2] = (__UINTPTR_TYPE__)file;
    open_cfw_test_ble_connection_log_record[3] =
        (__UINTPTR_TYPE__)function;
    open_cfw_test_ble_connection_log_record[4] = line;
    open_cfw_test_ble_connection_log_record[5] =
        (__UINTPTR_TYPE__)message;
    va_start(arguments, message);
    open_cfw_test_ble_connection_log_record[6] =
        va_arg(arguments, unsigned int);
    open_cfw_test_ble_connection_log_record[7] =
        va_arg(arguments, unsigned int);
    open_cfw_test_ble_connection_log_record[8] =
        va_arg(arguments, unsigned int);
    va_end(arguments);
}

void open_cfw_test_ble_connection_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    va_list arguments;

    ++open_cfw_test_ble_connection_trace_count;
    open_cfw_test_ble_connection_trace_record[0] = level;
    open_cfw_test_ble_connection_trace_record[1] =
        (__UINTPTR_TYPE__)first;
    open_cfw_test_ble_connection_trace_record[2] =
        (__UINTPTR_TYPE__)second;
    va_start(arguments, second);
    open_cfw_test_ble_connection_trace_record[3] =
        va_arg(arguments, unsigned int);
    open_cfw_test_ble_connection_trace_record[4] =
        va_arg(arguments, unsigned int);
    open_cfw_test_ble_connection_trace_record[5] =
        va_arg(arguments, unsigned int);
    va_end(arguments);
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_connection_callback callback
)
{
    ++open_cfw_test_ble_connection_remove_calls;
    open_cfw_test_ble_connection_remove_callback =
        (__UINTPTR_TYPE__)callback;
    return (unsigned char)open_cfw_test_ble_connection_remove_result;
}

void open_cfw_event_loop_push_delayed(
    open_cfw_ble_connection_callback callback,
    void *argument,
    unsigned int delay
)
{
    ++open_cfw_test_ble_connection_push_calls;
    open_cfw_test_ble_connection_push_callback =
        (__UINTPTR_TYPE__)callback;
    open_cfw_test_ble_connection_push_argument =
        (__UINTPTR_TYPE__)argument;
    open_cfw_test_ble_connection_push_delay = delay;
}
