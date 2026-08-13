/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the BLE connection-parameter event handler.
 */

#include <stdarg.h>

unsigned char *open_cfw_test_ble_event_context(void);
unsigned int open_cfw_test_ble_event_kind(unsigned char);
unsigned int open_cfw_test_ble_event_tick(void);
unsigned int open_cfw_test_ble_event_log_level(void);
void open_cfw_test_ble_event_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_event_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

volatile unsigned short *open_cfw_test_ble_event_connection_pointer;
unsigned int open_cfw_test_ble_event_timestamp;
unsigned char open_cfw_test_ble_event_previous_mode;
unsigned char open_cfw_test_ble_event_current_mode;
unsigned char open_cfw_test_ble_event_remote_active;
unsigned char open_cfw_test_ble_event_retry_active;
unsigned char open_cfw_test_ble_event_pending;
const volatile unsigned short *open_cfw_test_ble_event_defaults_pointer;

#define OPEN_CFW_BLE_EVENT_CONTEXT() open_cfw_test_ble_event_context()
#define OPEN_CFW_BLE_EVENT_CONNECTION_KIND(identifier) \
    open_cfw_test_ble_event_kind(identifier)
#define OPEN_CFW_BLE_EVENT_TICK() open_cfw_test_ble_event_tick()
#define OPEN_CFW_BLE_EVENT_LOG_LEVEL() open_cfw_test_ble_event_log_level()
#define OPEN_CFW_BLE_EVENT_LOG(...) open_cfw_test_ble_event_log(__VA_ARGS__)
#define OPEN_CFW_BLE_EVENT_TRACE(...) \
    open_cfw_test_ble_event_trace(__VA_ARGS__)
#define OPEN_CFW_BLE_EVENT_CONNECTION_STATE \
    open_cfw_test_ble_event_connection_pointer
#define OPEN_CFW_BLE_EVENT_TIMESTAMP open_cfw_test_ble_event_timestamp
#define OPEN_CFW_BLE_EVENT_PREVIOUS_MODE \
    open_cfw_test_ble_event_previous_mode
#define OPEN_CFW_BLE_EVENT_CURRENT_MODE \
    open_cfw_test_ble_event_current_mode
#define OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE \
    open_cfw_test_ble_event_remote_active
#define OPEN_CFW_BLE_EVENT_RETRY_ACTIVE \
    open_cfw_test_ble_event_retry_active
#define OPEN_CFW_BLE_EVENT_PENDING open_cfw_test_ble_event_pending
#define OPEN_CFW_BLE_EVENT_DEFAULTS \
    open_cfw_test_ble_event_defaults_pointer

#include "../../components/apollo_main/core_overlay/ble_connection_event.c"

#define OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH 12U

unsigned char open_cfw_test_ble_event_bytes[16];
unsigned short open_cfw_test_ble_event_connection_storage[16];
unsigned short open_cfw_test_ble_event_defaults_storage[8];
unsigned char open_cfw_test_ble_event_context_storage[8];
unsigned int open_cfw_test_ble_event_context_calls;
unsigned int open_cfw_test_ble_event_kind_results[8];
unsigned int open_cfw_test_ble_event_kind_count;
unsigned int open_cfw_test_ble_event_kind_index;
unsigned char open_cfw_test_ble_event_kind_identifiers[8];
unsigned int open_cfw_test_ble_event_tick_result;
unsigned int open_cfw_test_ble_event_tick_calls;
unsigned int open_cfw_test_ble_event_levels[64];
unsigned int open_cfw_test_ble_event_level_count;
unsigned int open_cfw_test_ble_event_level_index;
open_cfw_ble_event_uintptr open_cfw_test_ble_event_log_records[
    16U * OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_event_log_count;
open_cfw_ble_event_uintptr open_cfw_test_ble_event_trace_records[
    16U * OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_event_trace_count;
unsigned int open_cfw_test_ble_event_remove_calls;
open_cfw_ble_event_uintptr open_cfw_test_ble_event_remove_callback;
unsigned int open_cfw_test_ble_event_push_calls;
open_cfw_ble_event_uintptr open_cfw_test_ble_event_push_callback;
open_cfw_ble_event_uintptr open_cfw_test_ble_event_push_argument;
unsigned int open_cfw_test_ble_event_push_delay;

void open_cfw_test_ble_event_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_event_bytes[index] = 0U;
        open_cfw_test_ble_event_connection_storage[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_event_defaults_storage[index] = 0U;
        open_cfw_test_ble_event_context_storage[index] = 0U;
        open_cfw_test_ble_event_kind_results[index] = 0U;
        open_cfw_test_ble_event_kind_identifiers[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_ble_event_levels[index] = 0U;
    }
    for (
        index = 0U;
        index < 16U * OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_ble_event_log_records[index] = 0U;
        open_cfw_test_ble_event_trace_records[index] = 0U;
    }

    open_cfw_test_ble_event_connection_pointer =
        open_cfw_test_ble_event_connection_storage;
    open_cfw_test_ble_event_defaults_pointer =
        open_cfw_test_ble_event_defaults_storage;
    open_cfw_test_ble_event_timestamp = 0U;
    open_cfw_test_ble_event_previous_mode = 0xA3U;
    open_cfw_test_ble_event_current_mode = 0U;
    open_cfw_test_ble_event_remote_active = 0U;
    open_cfw_test_ble_event_retry_active = 0U;
    open_cfw_test_ble_event_pending = 0U;
    open_cfw_test_ble_event_context_calls = 0U;
    open_cfw_test_ble_event_kind_count = 0U;
    open_cfw_test_ble_event_kind_index = 0U;
    open_cfw_test_ble_event_tick_result = 0U;
    open_cfw_test_ble_event_tick_calls = 0U;
    open_cfw_test_ble_event_level_count = 0U;
    open_cfw_test_ble_event_level_index = 0U;
    open_cfw_test_ble_event_log_count = 0U;
    open_cfw_test_ble_event_trace_count = 0U;
    open_cfw_test_ble_event_remove_calls = 0U;
    open_cfw_test_ble_event_remove_callback = 0U;
    open_cfw_test_ble_event_push_calls = 0U;
    open_cfw_test_ble_event_push_callback = 0U;
    open_cfw_test_ble_event_push_argument = 0U;
    open_cfw_test_ble_event_push_delay = 0U;
}

unsigned char *open_cfw_test_ble_event_context(void)
{
    ++open_cfw_test_ble_event_context_calls;
    return open_cfw_test_ble_event_context_storage;
}

unsigned int open_cfw_test_ble_event_kind(unsigned char identifier)
{
    unsigned int value = 0U;

    if (open_cfw_test_ble_event_kind_index < 8U) {
        open_cfw_test_ble_event_kind_identifiers[
            open_cfw_test_ble_event_kind_index
        ] = identifier;
    }
    if (
        open_cfw_test_ble_event_kind_index
        < open_cfw_test_ble_event_kind_count
    ) {
        value = open_cfw_test_ble_event_kind_results[
            open_cfw_test_ble_event_kind_index
        ];
    }
    ++open_cfw_test_ble_event_kind_index;
    return value;
}

unsigned int open_cfw_test_ble_event_tick(void)
{
    ++open_cfw_test_ble_event_tick_calls;
    return open_cfw_test_ble_event_tick_result;
}

unsigned int open_cfw_test_ble_event_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_event_level_index
        < open_cfw_test_ble_event_level_count
    ) {
        value = open_cfw_test_ble_event_levels[
            open_cfw_test_ble_event_level_index
        ];
    }
    ++open_cfw_test_ble_event_level_index;
    return value;
}

static unsigned int open_cfw_test_ble_event_argument_count(
    open_cfw_ble_event_uintptr identity
)
{
    if (
        identity == 0x0075DC70U
        || identity == 0x0073BF88U
    ) {
        return 6U;
    }
    if (
        identity == 0x00784E90U
        || identity == 0x0076921CU
    ) {
        return 3U;
    }
    if (
        identity == 0x00726BE8U
        || identity == 0x00708F24U
    ) {
        return 2U;
    }
    if (
        identity == 0x00712460U
        || identity == 0x007000E4U
    ) {
        return 0U;
    }
    return 1U;
}

static int open_cfw_test_ble_event_pointer_argument(
    open_cfw_ble_event_uintptr identity
)
{
    return (
        identity == 0x00712424U
        || identity == 0x007000A0U
        || identity == 0x007475E4U
        || identity == 0x00726C1CU
        || identity == 0x00751CF8U
        || identity == 0x00731694U
    );
}

void open_cfw_test_ble_event_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    open_cfw_ble_event_uintptr *record =
        &open_cfw_test_ble_event_log_records[
            open_cfw_test_ble_event_log_count
            * OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH
        ];
    open_cfw_ble_event_uintptr identity =
        (open_cfw_ble_event_uintptr)message;
    unsigned int count = open_cfw_test_ble_event_argument_count(identity);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_event_log_count;
    record[0] = level;
    record[1] = (open_cfw_ble_event_uintptr)module;
    record[2] = (open_cfw_ble_event_uintptr)file;
    record[3] = (open_cfw_ble_event_uintptr)function;
    record[4] = line;
    record[5] = identity;
    va_start(arguments, message);
    for (index = 0U; index < count; ++index) {
        if (
            index == 0U
            && open_cfw_test_ble_event_pointer_argument(identity)
        ) {
            record[6] =
                (open_cfw_ble_event_uintptr)va_arg(arguments, const void *);
        }
        else {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

void open_cfw_test_ble_event_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    open_cfw_ble_event_uintptr *record =
        &open_cfw_test_ble_event_trace_records[
            open_cfw_test_ble_event_trace_count
            * OPEN_CFW_TEST_BLE_EVENT_RECORD_WIDTH
        ];
    open_cfw_ble_event_uintptr identity =
        (open_cfw_ble_event_uintptr)first;
    unsigned int count = open_cfw_test_ble_event_argument_count(identity);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_event_trace_count;
    record[0] = level;
    record[1] = identity;
    record[2] = (open_cfw_ble_event_uintptr)second;
    va_start(arguments, second);
    for (index = 0U; index < count; ++index) {
        if (
            index == 0U
            && open_cfw_test_ble_event_pointer_argument(identity)
        ) {
            record[3] =
                (open_cfw_ble_event_uintptr)va_arg(arguments, const void *);
        }
        else {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_event_callback callback
)
{
    ++open_cfw_test_ble_event_remove_calls;
    open_cfw_test_ble_event_remove_callback =
        (open_cfw_ble_event_uintptr)callback;
    return 0U;
}

void open_cfw_event_loop_push_delayed(
    open_cfw_ble_event_callback callback,
    void *argument,
    unsigned int delay
)
{
    ++open_cfw_test_ble_event_push_calls;
    open_cfw_test_ble_event_push_callback =
        (open_cfw_ble_event_uintptr)callback;
    open_cfw_test_ble_event_push_argument =
        (open_cfw_ble_event_uintptr)argument;
    open_cfw_test_ble_event_push_delay = delay;
}
