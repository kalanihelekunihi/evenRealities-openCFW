/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the BLE connection-parameter coordinator.
 */

#include <stdarg.h>

unsigned char *open_cfw_test_ble_coordinator_context(void);
void *open_cfw_test_ble_coordinator_allocate(unsigned int);
void open_cfw_test_ble_coordinator_send(unsigned char, void *);
unsigned int open_cfw_test_ble_coordinator_log_level(void);
void open_cfw_test_ble_coordinator_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_coordinator_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char *open_cfw_test_ble_coordinator_context_pointer;
unsigned char open_cfw_test_ble_coordinator_pending;
unsigned char open_cfw_test_ble_coordinator_previous_mode;
unsigned char open_cfw_test_ble_coordinator_current_mode;
const volatile unsigned short *
    open_cfw_test_ble_coordinator_connection_pointer;
unsigned char open_cfw_test_ble_coordinator_endpoint;
void *open_cfw_test_ble_coordinator_allocation_result;

#define OPEN_CFW_BLE_COORDINATOR_CONTEXT() \
    open_cfw_test_ble_coordinator_context()
#define OPEN_CFW_BLE_COORDINATOR_PENDING \
    open_cfw_test_ble_coordinator_pending
#define OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE \
    open_cfw_test_ble_coordinator_previous_mode
#define OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE \
    open_cfw_test_ble_coordinator_current_mode
#define OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE \
    open_cfw_test_ble_coordinator_connection_pointer
#define OPEN_CFW_BLE_COORDINATOR_ENDPOINT \
    open_cfw_test_ble_coordinator_endpoint
#define OPEN_CFW_BLE_COORDINATOR_ALLOCATE(size) \
    open_cfw_test_ble_coordinator_allocate(size)
#define OPEN_CFW_BLE_COORDINATOR_SEND(endpoint, packet) \
    open_cfw_test_ble_coordinator_send((endpoint), (packet))
#define OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() \
    open_cfw_test_ble_coordinator_log_level()
#define OPEN_CFW_BLE_COORDINATOR_LOG(...) \
    open_cfw_test_ble_coordinator_log(__VA_ARGS__)
#define OPEN_CFW_BLE_COORDINATOR_TRACE(...) \
    open_cfw_test_ble_coordinator_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_coordinator.c"

#define OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH 10U

unsigned char open_cfw_test_ble_coordinator_context_storage[8];
unsigned short open_cfw_test_ble_coordinator_connection_storage[16];
unsigned char open_cfw_test_ble_coordinator_packet[12];
unsigned int open_cfw_test_ble_coordinator_levels[32];
unsigned int open_cfw_test_ble_coordinator_level_count;
unsigned int open_cfw_test_ble_coordinator_level_index;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_log_records[
        8U * OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH
    ];
unsigned int open_cfw_test_ble_coordinator_log_count;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_trace_records[
        8U * OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH
    ];
unsigned int open_cfw_test_ble_coordinator_trace_count;
unsigned int open_cfw_test_ble_coordinator_primary_calls;
unsigned int open_cfw_test_ble_coordinator_primary_result;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_primary_state;
unsigned int open_cfw_test_ble_coordinator_secondary_calls;
unsigned int open_cfw_test_ble_coordinator_secondary_result;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_secondary_state;
unsigned int open_cfw_test_ble_coordinator_allocate_calls;
unsigned int open_cfw_test_ble_coordinator_allocate_size;
unsigned int open_cfw_test_ble_coordinator_send_calls;
unsigned char open_cfw_test_ble_coordinator_send_endpoint;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_send_packet;
unsigned int open_cfw_test_ble_coordinator_remove_calls;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_remove_callback;
unsigned int open_cfw_test_ble_coordinator_push_calls;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_push_callback;
open_cfw_ble_coordinator_uintptr
    open_cfw_test_ble_coordinator_push_argument;
unsigned int open_cfw_test_ble_coordinator_push_delay;

void open_cfw_test_ble_coordinator_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_coordinator_context_storage[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_coordinator_connection_storage[index] = 0U;
    }
    for (index = 0U; index < 12U; ++index) {
        open_cfw_test_ble_coordinator_packet[index] = 0xA5U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_ble_coordinator_levels[index] = 0U;
    }
    for (
        index = 0U;
        index < 8U * OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_ble_coordinator_log_records[index] = 0U;
        open_cfw_test_ble_coordinator_trace_records[index] = 0U;
    }
    open_cfw_test_ble_coordinator_context_pointer =
        open_cfw_test_ble_coordinator_context_storage;
    open_cfw_test_ble_coordinator_connection_pointer =
        open_cfw_test_ble_coordinator_connection_storage;
    open_cfw_test_ble_coordinator_pending = 0U;
    open_cfw_test_ble_coordinator_previous_mode = 0U;
    open_cfw_test_ble_coordinator_current_mode = 0U;
    open_cfw_test_ble_coordinator_endpoint = 0U;
    open_cfw_test_ble_coordinator_allocation_result = (void *)0;
    open_cfw_test_ble_coordinator_level_count = 0U;
    open_cfw_test_ble_coordinator_level_index = 0U;
    open_cfw_test_ble_coordinator_log_count = 0U;
    open_cfw_test_ble_coordinator_trace_count = 0U;
    open_cfw_test_ble_coordinator_primary_calls = 0U;
    open_cfw_test_ble_coordinator_primary_result = 0U;
    open_cfw_test_ble_coordinator_primary_state = 0U;
    open_cfw_test_ble_coordinator_secondary_calls = 0U;
    open_cfw_test_ble_coordinator_secondary_result = 0U;
    open_cfw_test_ble_coordinator_secondary_state = 0U;
    open_cfw_test_ble_coordinator_allocate_calls = 0U;
    open_cfw_test_ble_coordinator_allocate_size = 0U;
    open_cfw_test_ble_coordinator_send_calls = 0U;
    open_cfw_test_ble_coordinator_send_endpoint = 0U;
    open_cfw_test_ble_coordinator_send_packet = 0U;
    open_cfw_test_ble_coordinator_remove_calls = 0U;
    open_cfw_test_ble_coordinator_remove_callback = 0U;
    open_cfw_test_ble_coordinator_push_calls = 0U;
    open_cfw_test_ble_coordinator_push_callback = 0U;
    open_cfw_test_ble_coordinator_push_argument = 0U;
    open_cfw_test_ble_coordinator_push_delay = 0U;
}

unsigned char *open_cfw_test_ble_coordinator_context(void)
{
    return open_cfw_test_ble_coordinator_context_pointer;
}

unsigned int open_cfw_test_ble_coordinator_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_coordinator_level_index
        < open_cfw_test_ble_coordinator_level_count
    ) {
        value = open_cfw_test_ble_coordinator_levels[
            open_cfw_test_ble_coordinator_level_index
        ];
    }
    ++open_cfw_test_ble_coordinator_level_index;
    return value;
}

static unsigned int open_cfw_test_ble_coordinator_log_argument_count(
    open_cfw_ble_coordinator_uintptr message
)
{
    if (message == 0x0073BFB4U) {
        return 4U;
    }
    if (
        message == 0x00712370U
        || message == 0x007123ACU
    ) {
        return 3U;
    }
    return 1U;
}

void open_cfw_test_ble_coordinator_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    open_cfw_ble_coordinator_uintptr *record =
        &open_cfw_test_ble_coordinator_log_records[
            open_cfw_test_ble_coordinator_log_count
            * OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH
        ];
    open_cfw_ble_coordinator_uintptr message_value =
        (open_cfw_ble_coordinator_uintptr)message;
    unsigned int argument_count =
        open_cfw_test_ble_coordinator_log_argument_count(message_value);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_coordinator_log_count;
    record[0] = level;
    record[1] = (open_cfw_ble_coordinator_uintptr)module;
    record[2] = (open_cfw_ble_coordinator_uintptr)file;
    record[3] = (open_cfw_ble_coordinator_uintptr)function;
    record[4] = line;
    record[5] = message_value;
    va_start(arguments, message);
    if (message_value == 0x0071BE08U) {
        record[6] = (open_cfw_ble_coordinator_uintptr)
            va_arg(arguments, void *);
    }
    else {
        for (index = 0U; index < argument_count; ++index) {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

static unsigned int open_cfw_test_ble_coordinator_trace_argument_count(
    open_cfw_ble_coordinator_uintptr trace
)
{
    if (trace == 0x00726B4CU) {
        return 3U;
    }
    if (
        trace == 0x006F8204U
        || trace == 0x006F824CU
    ) {
        return 3U;
    }
    return 1U;
}

void open_cfw_test_ble_coordinator_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    open_cfw_ble_coordinator_uintptr *record =
        &open_cfw_test_ble_coordinator_trace_records[
            open_cfw_test_ble_coordinator_trace_count
            * OPEN_CFW_TEST_BLE_COORDINATOR_RECORD_WIDTH
        ];
    open_cfw_ble_coordinator_uintptr first_value =
        (open_cfw_ble_coordinator_uintptr)first;
    unsigned int argument_count =
        open_cfw_test_ble_coordinator_trace_argument_count(first_value);
    unsigned int index;
    va_list arguments;

    ++open_cfw_test_ble_coordinator_trace_count;
    record[0] = level;
    record[1] = first_value;
    record[2] = (open_cfw_ble_coordinator_uintptr)second;
    va_start(arguments, second);
    if (first_value == 0x0070005CU) {
        record[3] = (open_cfw_ble_coordinator_uintptr)
            va_arg(arguments, void *);
    }
    else {
        for (index = 0U; index < argument_count; ++index) {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
}

unsigned int open_cfw_ble_connection_select_primary(
    const volatile unsigned short *state
)
{
    ++open_cfw_test_ble_coordinator_primary_calls;
    open_cfw_test_ble_coordinator_primary_state =
        (open_cfw_ble_coordinator_uintptr)state;
    return open_cfw_test_ble_coordinator_primary_result;
}

unsigned int open_cfw_ble_connection_select_secondary(
    const volatile unsigned short *state
)
{
    ++open_cfw_test_ble_coordinator_secondary_calls;
    open_cfw_test_ble_coordinator_secondary_state =
        (open_cfw_ble_coordinator_uintptr)state;
    return open_cfw_test_ble_coordinator_secondary_result;
}

void *open_cfw_test_ble_coordinator_allocate(unsigned int size)
{
    ++open_cfw_test_ble_coordinator_allocate_calls;
    open_cfw_test_ble_coordinator_allocate_size = size;
    return open_cfw_test_ble_coordinator_allocation_result;
}

void open_cfw_test_ble_coordinator_send(
    unsigned char endpoint,
    void *packet
)
{
    ++open_cfw_test_ble_coordinator_send_calls;
    open_cfw_test_ble_coordinator_send_endpoint = endpoint;
    open_cfw_test_ble_coordinator_send_packet =
        (open_cfw_ble_coordinator_uintptr)packet;
}

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_coordinator_callback callback
)
{
    ++open_cfw_test_ble_coordinator_remove_calls;
    open_cfw_test_ble_coordinator_remove_callback =
        (open_cfw_ble_coordinator_uintptr)callback;
    return 0U;
}

void open_cfw_event_loop_push_delayed(
    open_cfw_ble_coordinator_callback callback,
    void *argument,
    unsigned int delay
)
{
    ++open_cfw_test_ble_coordinator_push_calls;
    open_cfw_test_ble_coordinator_push_callback =
        (open_cfw_ble_coordinator_uintptr)callback;
    open_cfw_test_ble_coordinator_push_argument =
        (open_cfw_ble_coordinator_uintptr)argument;
    open_cfw_test_ble_coordinator_push_delay = delay;
}
