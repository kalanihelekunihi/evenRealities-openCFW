/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the BLE remote connection-parameter handler.
 */

#include <stdarg.h>

unsigned int open_cfw_test_ble_remote_role(void);
unsigned int open_cfw_test_ble_remote_log_level(void);
void open_cfw_test_ble_remote_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_remote_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

volatile unsigned short *open_cfw_test_ble_remote_connection_pointer;
unsigned char open_cfw_test_ble_remote_previous_mode;
unsigned char open_cfw_test_ble_remote_current_mode;
unsigned char open_cfw_test_ble_remote_active;

#define OPEN_CFW_BLE_REMOTE_CONNECTION_STATE \
    open_cfw_test_ble_remote_connection_pointer
#define OPEN_CFW_BLE_REMOTE_PREVIOUS_MODE \
    open_cfw_test_ble_remote_previous_mode
#define OPEN_CFW_BLE_REMOTE_CURRENT_MODE \
    open_cfw_test_ble_remote_current_mode
#define OPEN_CFW_BLE_REMOTE_ACTIVE \
    open_cfw_test_ble_remote_active
#define OPEN_CFW_BLE_REMOTE_ROLE() \
    open_cfw_test_ble_remote_role()
#define OPEN_CFW_BLE_REMOTE_LOG_LEVEL() \
    open_cfw_test_ble_remote_log_level()
#define OPEN_CFW_BLE_REMOTE_LOG(...) \
    open_cfw_test_ble_remote_log(__VA_ARGS__)
#define OPEN_CFW_BLE_REMOTE_TRACE(...) \
    open_cfw_test_ble_remote_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_remote_parameters.c"

#define OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH 12U

unsigned char open_cfw_test_ble_remote_parameters[24];
unsigned short open_cfw_test_ble_remote_connection_storage[16];
unsigned int open_cfw_test_ble_remote_levels[32];
unsigned int open_cfw_test_ble_remote_level_count;
unsigned int open_cfw_test_ble_remote_level_index;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_log_records[
    8U * OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_remote_log_count;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_trace_records[
    8U * OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_remote_trace_count;
unsigned int open_cfw_test_ble_remote_secondary_calls;
unsigned int open_cfw_test_ble_remote_secondary_result;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_secondary_state;
unsigned int open_cfw_test_ble_remote_role_result;
unsigned int open_cfw_test_ble_remote_role_calls;
unsigned int open_cfw_test_ble_remote_remove_calls;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_remove_callback;
unsigned int open_cfw_test_ble_remote_push_calls;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_push_callback;
open_cfw_ble_remote_uintptr open_cfw_test_ble_remote_push_argument;
unsigned int open_cfw_test_ble_remote_push_delay;

void open_cfw_test_ble_remote_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 24U; ++index) {
        open_cfw_test_ble_remote_parameters[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_remote_connection_storage[index] = 0U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ble_remote_levels[index] = 0U;
    }
    for (
        index = 0U;
        index < 8U * OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_ble_remote_log_records[index] = 0U;
        open_cfw_test_ble_remote_trace_records[index] = 0U;
    }

    open_cfw_test_ble_remote_connection_pointer =
        open_cfw_test_ble_remote_connection_storage;
    open_cfw_test_ble_remote_previous_mode = 0U;
    open_cfw_test_ble_remote_current_mode = 0U;
    open_cfw_test_ble_remote_active = 0U;
    open_cfw_test_ble_remote_level_count = 0U;
    open_cfw_test_ble_remote_level_index = 0U;
    open_cfw_test_ble_remote_log_count = 0U;
    open_cfw_test_ble_remote_trace_count = 0U;
    open_cfw_test_ble_remote_secondary_calls = 0U;
    open_cfw_test_ble_remote_secondary_result = 0xA4U;
    open_cfw_test_ble_remote_secondary_state = 0U;
    open_cfw_test_ble_remote_role_result = 0U;
    open_cfw_test_ble_remote_role_calls = 0U;
    open_cfw_test_ble_remote_remove_calls = 0U;
    open_cfw_test_ble_remote_remove_callback = 0U;
    open_cfw_test_ble_remote_push_calls = 0U;
    open_cfw_test_ble_remote_push_callback = 0U;
    open_cfw_test_ble_remote_push_argument = 0U;
    open_cfw_test_ble_remote_push_delay = 0U;
}

unsigned int open_cfw_test_ble_remote_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_remote_level_index
        < open_cfw_test_ble_remote_level_count
    ) {
        value = open_cfw_test_ble_remote_levels[
            open_cfw_test_ble_remote_level_index
        ];
    }
    ++open_cfw_test_ble_remote_level_index;
    return value;
}

static unsigned int open_cfw_test_ble_remote_argument_count(
    open_cfw_ble_remote_uintptr identity
)
{
    if (
        identity == 0x0077DD58U
        || identity == 0x0075DCD0U
    ) {
        return 0U;
    }
    if (
        identity == 0x00747594U
        || identity == 0x00731664U
    ) {
        return 6U;
    }
    if (
        identity == 0x007475BCU
        || identity == 0x00726BB4U
    ) {
        return 2U;
    }
    return 1U;
}

void open_cfw_test_ble_remote_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    open_cfw_ble_remote_uintptr *record =
        &open_cfw_test_ble_remote_log_records[
            open_cfw_test_ble_remote_log_count
            * OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH
        ];
    open_cfw_ble_remote_uintptr message_value =
        (open_cfw_ble_remote_uintptr)message;
    unsigned int count =
        open_cfw_test_ble_remote_argument_count(message_value);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_remote_log_count;
    record[0] = level;
    record[1] = (open_cfw_ble_remote_uintptr)module;
    record[2] = (open_cfw_ble_remote_uintptr)file;
    record[3] = (open_cfw_ble_remote_uintptr)function;
    record[4] = line;
    record[5] = message_value;
    va_start(arguments, message);
    for (index = 0U; index < count; ++index) {
        if (
            message_value == 0x007475BCU
            && index == 1U
        ) {
            record[6U + index] =
                (open_cfw_ble_remote_uintptr)va_arg(arguments, const void *);
        }
        else {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

void open_cfw_test_ble_remote_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    open_cfw_ble_remote_uintptr *record =
        &open_cfw_test_ble_remote_trace_records[
            open_cfw_test_ble_remote_trace_count
            * OPEN_CFW_TEST_BLE_REMOTE_RECORD_WIDTH
        ];
    open_cfw_ble_remote_uintptr identity =
        (open_cfw_ble_remote_uintptr)first;
    unsigned int count = open_cfw_test_ble_remote_argument_count(identity);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_remote_trace_count;
    record[0] = level;
    record[1] = identity;
    record[2] = (open_cfw_ble_remote_uintptr)second;
    va_start(arguments, second);
    for (index = 0U; index < count; ++index) {
        if (
            identity == 0x00726BB4U
            && index == 1U
        ) {
            record[3U + index] =
                (open_cfw_ble_remote_uintptr)va_arg(arguments, const void *);
        }
        else {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

unsigned int open_cfw_ble_connection_select_secondary(
    const volatile unsigned short *state
)
{
    ++open_cfw_test_ble_remote_secondary_calls;
    open_cfw_test_ble_remote_secondary_state =
        (open_cfw_ble_remote_uintptr)state;
    return open_cfw_test_ble_remote_secondary_result;
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_remote_callback callback
)
{
    ++open_cfw_test_ble_remote_remove_calls;
    open_cfw_test_ble_remote_remove_callback =
        (open_cfw_ble_remote_uintptr)callback;
    return 0U;
}

void open_cfw_event_loop_push_delayed(
    open_cfw_ble_remote_callback callback,
    void *argument,
    unsigned int delay
)
{
    ++open_cfw_test_ble_remote_push_calls;
    open_cfw_test_ble_remote_push_callback =
        (open_cfw_ble_remote_uintptr)callback;
    open_cfw_test_ble_remote_push_argument =
        (open_cfw_ble_remote_uintptr)argument;
    open_cfw_test_ble_remote_push_delay = delay;
}

unsigned int open_cfw_test_ble_remote_role(void)
{
    ++open_cfw_test_ble_remote_role_calls;
    return open_cfw_test_ble_remote_role_result;
}
