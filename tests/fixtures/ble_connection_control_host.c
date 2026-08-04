/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the BLE connection-mode control helpers.
 */

#include <stdarg.h>

unsigned int open_cfw_test_ble_control_tick(void);
unsigned int open_cfw_test_ble_control_log_level(void);
void open_cfw_test_ble_control_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_control_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_ble_control_current_mode;
unsigned char open_cfw_test_ble_control_remote_active;
unsigned char open_cfw_test_ble_control_retry_active;
unsigned int open_cfw_test_ble_control_timestamp;

#define OPEN_CFW_BLE_CONTROL_CURRENT_MODE \
    open_cfw_test_ble_control_current_mode
#define OPEN_CFW_BLE_CONTROL_REMOTE_ACTIVE \
    open_cfw_test_ble_control_remote_active
#define OPEN_CFW_BLE_CONTROL_RETRY_ACTIVE \
    open_cfw_test_ble_control_retry_active
#define OPEN_CFW_BLE_CONTROL_TIMESTAMP \
    open_cfw_test_ble_control_timestamp
#define OPEN_CFW_BLE_CONTROL_TICK() open_cfw_test_ble_control_tick()
#define OPEN_CFW_BLE_CONTROL_LOG_LEVEL() \
    open_cfw_test_ble_control_log_level()
#define OPEN_CFW_BLE_CONTROL_LOG(...) \
    open_cfw_test_ble_control_log(__VA_ARGS__)
#define OPEN_CFW_BLE_CONTROL_TRACE(...) \
    open_cfw_test_ble_control_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_control.c"

#define OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH 8U

unsigned int open_cfw_test_ble_control_tick_result;
unsigned int open_cfw_test_ble_control_tick_calls;
unsigned int open_cfw_test_ble_control_levels[16];
unsigned int open_cfw_test_ble_control_level_count;
unsigned int open_cfw_test_ble_control_level_index;
open_cfw_ble_control_uintptr open_cfw_test_ble_control_log_records[
    4U * OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_control_log_count;
open_cfw_ble_control_uintptr open_cfw_test_ble_control_trace_records[
    4U * OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_control_trace_count;
unsigned int open_cfw_test_ble_control_remove_count;
open_cfw_ble_control_uintptr open_cfw_test_ble_control_remove_callbacks[8];
unsigned int open_cfw_test_ble_control_push_count;
open_cfw_ble_control_uintptr open_cfw_test_ble_control_push_callbacks[8];
open_cfw_ble_control_uintptr open_cfw_test_ble_control_push_arguments[8];
unsigned int open_cfw_test_ble_control_push_delays[8];

void open_cfw_test_ble_control_reset(void)
{
    unsigned int index;

    open_cfw_test_ble_control_current_mode = 0U;
    open_cfw_test_ble_control_remote_active = 0U;
    open_cfw_test_ble_control_retry_active = 0U;
    open_cfw_test_ble_control_timestamp = 0U;
    open_cfw_test_ble_control_tick_result = 0U;
    open_cfw_test_ble_control_tick_calls = 0U;
    open_cfw_test_ble_control_level_count = 0U;
    open_cfw_test_ble_control_level_index = 0U;
    open_cfw_test_ble_control_log_count = 0U;
    open_cfw_test_ble_control_trace_count = 0U;
    open_cfw_test_ble_control_remove_count = 0U;
    open_cfw_test_ble_control_push_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_control_levels[index] = 0U;
    }
    for (index = 0U; index < 4U * OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH;
         ++index) {
        open_cfw_test_ble_control_log_records[index] = 0U;
        open_cfw_test_ble_control_trace_records[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_control_remove_callbacks[index] = 0U;
        open_cfw_test_ble_control_push_callbacks[index] = 0U;
        open_cfw_test_ble_control_push_arguments[index] = 0U;
        open_cfw_test_ble_control_push_delays[index] = 0U;
    }
}

unsigned int open_cfw_test_ble_control_tick(void)
{
    ++open_cfw_test_ble_control_tick_calls;
    return open_cfw_test_ble_control_tick_result;
}

unsigned int open_cfw_test_ble_control_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_ble_control_level_index
        < open_cfw_test_ble_control_level_count
    ) {
        result = open_cfw_test_ble_control_levels[
            open_cfw_test_ble_control_level_index
        ];
    }
    ++open_cfw_test_ble_control_level_index;
    return result;
}

void open_cfw_test_ble_control_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    open_cfw_ble_control_uintptr *record;
    va_list arguments;

    if (open_cfw_test_ble_control_log_count >= 4U) {
        ++open_cfw_test_ble_control_log_count;
        return;
    }
    record = &open_cfw_test_ble_control_log_records[
        open_cfw_test_ble_control_log_count
        * OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH
    ];
    record[0] = severity;
    record[1] = (open_cfw_ble_control_uintptr)module;
    record[2] = (open_cfw_ble_control_uintptr)file;
    record[3] = (open_cfw_ble_control_uintptr)function;
    record[4] = line;
    record[5] = (open_cfw_ble_control_uintptr)format;
    va_start(arguments, format);
    if ((open_cfw_ble_control_uintptr)format == 0x006D8454U) {
        record[6] = va_arg(arguments, unsigned int);
        record[7] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_ble_control_log_count;
}

void open_cfw_test_ble_control_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_ble_control_uintptr *record;
    va_list arguments;

    if (open_cfw_test_ble_control_trace_count >= 4U) {
        ++open_cfw_test_ble_control_trace_count;
        return;
    }
    record = &open_cfw_test_ble_control_trace_records[
        open_cfw_test_ble_control_trace_count
        * OPEN_CFW_TEST_BLE_CONTROL_RECORD_WIDTH
    ];
    record[0] = event;
    record[1] = (open_cfw_ble_control_uintptr)identity;
    record[2] = (open_cfw_ble_control_uintptr)duplicate_identity;
    va_start(arguments, duplicate_identity);
    if ((open_cfw_ble_control_uintptr)identity == 0x0069E20CU) {
        record[3] = va_arg(arguments, unsigned int);
        record[4] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_ble_control_trace_count;
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_control_callback callback
)
{
    if (open_cfw_test_ble_control_remove_count < 8U) {
        open_cfw_test_ble_control_remove_callbacks[
            open_cfw_test_ble_control_remove_count
        ] = (open_cfw_ble_control_uintptr)callback;
    }
    ++open_cfw_test_ble_control_remove_count;
    return 0U;
}

void open_cfw_event_loop_push_delayed(
    open_cfw_ble_control_callback callback,
    void *argument,
    unsigned int delay
)
{
    if (open_cfw_test_ble_control_push_count < 8U) {
        open_cfw_test_ble_control_push_callbacks[
            open_cfw_test_ble_control_push_count
        ] = (open_cfw_ble_control_uintptr)callback;
        open_cfw_test_ble_control_push_arguments[
            open_cfw_test_ble_control_push_count
        ] = (open_cfw_ble_control_uintptr)argument;
        open_cfw_test_ble_control_push_delays[
            open_cfw_test_ble_control_push_count
        ] = delay;
    }
    ++open_cfw_test_ble_control_push_count;
}
