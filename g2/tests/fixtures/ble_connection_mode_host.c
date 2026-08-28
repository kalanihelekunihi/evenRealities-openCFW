/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the BLE connection-parameter mode selectors.
 */

#include <stdarg.h>

unsigned int open_cfw_test_ble_mode_log_level(void);
void open_cfw_test_ble_mode_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_mode_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

const volatile unsigned short *open_cfw_test_ble_mode_defaults_pointer;

#define OPEN_CFW_BLE_MODE_DEFAULTS \
    open_cfw_test_ble_mode_defaults_pointer
#define OPEN_CFW_BLE_MODE_LOG_LEVEL() \
    open_cfw_test_ble_mode_log_level()
#define OPEN_CFW_BLE_MODE_LOG(...) \
    open_cfw_test_ble_mode_log(__VA_ARGS__)
#define OPEN_CFW_BLE_MODE_TRACE(...) \
    open_cfw_test_ble_mode_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_mode.c"

#define OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH 12U

unsigned int open_cfw_test_ble_mode_levels[32];
unsigned int open_cfw_test_ble_mode_level_count;
unsigned int open_cfw_test_ble_mode_level_index;
unsigned short open_cfw_test_ble_mode_defaults[6];
open_cfw_ble_mode_uintptr
    open_cfw_test_ble_mode_log_records[
        5U * OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH
    ];
unsigned int open_cfw_test_ble_mode_log_count;
open_cfw_ble_mode_uintptr
    open_cfw_test_ble_mode_trace_records[
        5U * OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH
    ];
unsigned int open_cfw_test_ble_mode_trace_count;

void open_cfw_test_ble_mode_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ble_mode_levels[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_ble_mode_defaults[index] = 0U;
    }
    for (
        index = 0U;
        index < 5U * OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_ble_mode_log_records[index] = 0U;
        open_cfw_test_ble_mode_trace_records[index] = 0U;
    }
    open_cfw_test_ble_mode_defaults_pointer =
        open_cfw_test_ble_mode_defaults;
    open_cfw_test_ble_mode_level_count = 0U;
    open_cfw_test_ble_mode_level_index = 0U;
    open_cfw_test_ble_mode_log_count = 0U;
    open_cfw_test_ble_mode_trace_count = 0U;
}

unsigned int open_cfw_test_ble_mode_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_mode_level_index
        < open_cfw_test_ble_mode_level_count
    ) {
        value = open_cfw_test_ble_mode_levels[
            open_cfw_test_ble_mode_level_index
        ];
    }
    ++open_cfw_test_ble_mode_level_index;
    return value;
}

void open_cfw_test_ble_mode_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    open_cfw_ble_mode_uintptr *record =
        &open_cfw_test_ble_mode_log_records[
            open_cfw_test_ble_mode_log_count
            * OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH
        ];
    open_cfw_ble_mode_uintptr message_value =
        (open_cfw_ble_mode_uintptr)message;
    unsigned int argument_count = 0U;
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_mode_log_count;
    record[0] = level;
    record[1] = (open_cfw_ble_mode_uintptr)module;
    record[2] = (open_cfw_ble_mode_uintptr)file;
    record[3] = (open_cfw_ble_mode_uintptr)function;
    record[4] = line;
    record[5] = message_value;
    if (message_value == 0x00777760U) {
        argument_count = 6U;
    }
    else if (message_value == 0x0077776CU) {
        argument_count = 2U;
    }
    else if (
        message_value == 0x00777A6CU
        || message_value == 0x00777A74U
    ) {
        argument_count = 1U;
    }
    va_start(arguments, message);
    for (index = 0U; index < argument_count; ++index) {
        record[6U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
}

void open_cfw_test_ble_mode_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    open_cfw_ble_mode_uintptr *record =
        &open_cfw_test_ble_mode_trace_records[
            open_cfw_test_ble_mode_trace_count
            * OPEN_CFW_TEST_BLE_MODE_RECORD_WIDTH
        ];
    open_cfw_ble_mode_uintptr first_value =
        (open_cfw_ble_mode_uintptr)first;
    unsigned int argument_count = 0U;
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_mode_trace_count;
    record[0] = level;
    record[1] = first_value;
    record[2] = (open_cfw_ble_mode_uintptr)second;
    if (first_value == 0x00777768U) {
        argument_count = 6U;
    }
    else if (first_value == 0x00777770U) {
        argument_count = 2U;
    }
    else if (
        first_value == 0x00777A70U
        || first_value == 0x00777A78U
    ) {
        argument_count = 1U;
    }
    va_start(arguments, second);
    for (index = 0U; index < argument_count; ++index) {
        record[3U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
}
