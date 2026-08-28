/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the BLE connection-parameter delayed callback.
 */

#include <stdarg.h>

unsigned char *open_cfw_test_ble_callback_controller(void);
unsigned char *open_cfw_test_ble_callback_context(void);
unsigned int open_cfw_test_ble_callback_role(void);
void *open_cfw_test_ble_callback_allocate(unsigned int);
void open_cfw_test_ble_callback_send(unsigned char, void *);
unsigned int open_cfw_test_ble_callback_log_level(void);
void open_cfw_test_ble_callback_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_callback_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_BLE_CALLBACK_CONTROLLER() \
    open_cfw_test_ble_callback_controller()
#define OPEN_CFW_BLE_CALLBACK_CONTEXT() \
    open_cfw_test_ble_callback_context()
#define OPEN_CFW_BLE_CALLBACK_ROLE() \
    open_cfw_test_ble_callback_role()
#define OPEN_CFW_BLE_CALLBACK_ALLOCATE(size) \
    open_cfw_test_ble_callback_allocate(size)
#define OPEN_CFW_BLE_CALLBACK_SEND(endpoint, packet) \
    open_cfw_test_ble_callback_send((endpoint), (packet))
#define OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() \
    open_cfw_test_ble_callback_log_level()
#define OPEN_CFW_BLE_CALLBACK_LOG(...) \
    open_cfw_test_ble_callback_log(__VA_ARGS__)
#define OPEN_CFW_BLE_CALLBACK_TRACE(...) \
    open_cfw_test_ble_callback_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/ble_connection_callback.c"

unsigned char open_cfw_test_ble_callback_controller_storage[0x57];
unsigned char open_cfw_test_ble_callback_context_storage[8];
unsigned char open_cfw_test_ble_callback_packet[12];
unsigned char *open_cfw_test_ble_callback_controller_pointer;
unsigned char *open_cfw_test_ble_callback_context_pointer;
unsigned int open_cfw_test_ble_callback_controller_calls;
unsigned int open_cfw_test_ble_callback_context_calls;
unsigned int open_cfw_test_ble_callback_role_calls;
unsigned int open_cfw_test_ble_callback_role_result;
void *open_cfw_test_ble_callback_allocation_result;
unsigned int open_cfw_test_ble_callback_allocate_calls;
unsigned int open_cfw_test_ble_callback_allocate_size;
unsigned int open_cfw_test_ble_callback_send_calls;
unsigned char open_cfw_test_ble_callback_send_endpoint;
open_cfw_ble_callback_uintptr open_cfw_test_ble_callback_send_packet;
unsigned int open_cfw_test_ble_callback_levels[8];
unsigned int open_cfw_test_ble_callback_level_count;
unsigned int open_cfw_test_ble_callback_level_index;
open_cfw_ble_callback_uintptr open_cfw_test_ble_callback_log_record[7];
unsigned int open_cfw_test_ble_callback_log_count;
open_cfw_ble_callback_uintptr open_cfw_test_ble_callback_trace_record[3];
unsigned int open_cfw_test_ble_callback_trace_count;

void open_cfw_test_ble_callback_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 0x57U; ++index) {
        open_cfw_test_ble_callback_controller_storage[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_callback_context_storage[index] = 0U;
        open_cfw_test_ble_callback_levels[index] = 0U;
    }
    for (index = 0U; index < 12U; ++index) {
        open_cfw_test_ble_callback_packet[index] = 0xA5U;
    }
    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_ble_callback_log_record[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_ble_callback_trace_record[index] = 0U;
    }
    open_cfw_test_ble_callback_controller_pointer =
        open_cfw_test_ble_callback_controller_storage;
    open_cfw_test_ble_callback_context_pointer =
        open_cfw_test_ble_callback_context_storage;
    open_cfw_test_ble_callback_controller_calls = 0U;
    open_cfw_test_ble_callback_context_calls = 0U;
    open_cfw_test_ble_callback_role_calls = 0U;
    open_cfw_test_ble_callback_role_result = 0U;
    open_cfw_test_ble_callback_allocation_result = (void *)0;
    open_cfw_test_ble_callback_allocate_calls = 0U;
    open_cfw_test_ble_callback_allocate_size = 0U;
    open_cfw_test_ble_callback_send_calls = 0U;
    open_cfw_test_ble_callback_send_endpoint = 0U;
    open_cfw_test_ble_callback_send_packet = 0U;
    open_cfw_test_ble_callback_level_count = 0U;
    open_cfw_test_ble_callback_level_index = 0U;
    open_cfw_test_ble_callback_log_count = 0U;
    open_cfw_test_ble_callback_trace_count = 0U;
}

unsigned char *open_cfw_test_ble_callback_controller(void)
{
    ++open_cfw_test_ble_callback_controller_calls;
    return open_cfw_test_ble_callback_controller_pointer;
}

unsigned char *open_cfw_test_ble_callback_context(void)
{
    ++open_cfw_test_ble_callback_context_calls;
    return open_cfw_test_ble_callback_context_pointer;
}

unsigned int open_cfw_test_ble_callback_role(void)
{
    ++open_cfw_test_ble_callback_role_calls;
    return open_cfw_test_ble_callback_role_result;
}

void *open_cfw_test_ble_callback_allocate(unsigned int size)
{
    ++open_cfw_test_ble_callback_allocate_calls;
    open_cfw_test_ble_callback_allocate_size = size;
    return open_cfw_test_ble_callback_allocation_result;
}

void open_cfw_test_ble_callback_send(
    unsigned char endpoint,
    void *packet
)
{
    ++open_cfw_test_ble_callback_send_calls;
    open_cfw_test_ble_callback_send_endpoint = endpoint;
    open_cfw_test_ble_callback_send_packet =
        (open_cfw_ble_callback_uintptr)packet;
}

unsigned int open_cfw_test_ble_callback_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_callback_level_index
        < open_cfw_test_ble_callback_level_count
    ) {
        value = open_cfw_test_ble_callback_levels[
            open_cfw_test_ble_callback_level_index
        ];
    }
    ++open_cfw_test_ble_callback_level_index;
    return value;
}

void open_cfw_test_ble_callback_log(
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

    ++open_cfw_test_ble_callback_log_count;
    open_cfw_test_ble_callback_log_record[0] = level;
    open_cfw_test_ble_callback_log_record[1] =
        (open_cfw_ble_callback_uintptr)module;
    open_cfw_test_ble_callback_log_record[2] =
        (open_cfw_ble_callback_uintptr)file;
    open_cfw_test_ble_callback_log_record[3] =
        (open_cfw_ble_callback_uintptr)function;
    open_cfw_test_ble_callback_log_record[4] = line;
    open_cfw_test_ble_callback_log_record[5] =
        (open_cfw_ble_callback_uintptr)message;
    va_start(arguments, message);
    open_cfw_test_ble_callback_log_record[6] =
        va_arg(arguments, unsigned int);
    va_end(arguments);
}

void open_cfw_test_ble_callback_trace(
    unsigned int level,
    const void *first,
    const void *second,
    ...
)
{
    ++open_cfw_test_ble_callback_trace_count;
    open_cfw_test_ble_callback_trace_record[0] = level;
    open_cfw_test_ble_callback_trace_record[1] =
        (open_cfw_ble_callback_uintptr)first;
    open_cfw_test_ble_callback_trace_record[2] =
        (open_cfw_ble_callback_uintptr)second;
}
