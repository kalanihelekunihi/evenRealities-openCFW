/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the bounded protobuf-direct BLE transmit wrappers.
 */

#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() \
    open_cfw_test_ble_msgtx_pb_direct_ota_active()
#define OPEN_CFW_BLE_MSGTX_PB_SEND_SIDE_REJECTED() \
    open_cfw_test_ble_msgtx_pb_send_side_rejected()
#define OPEN_CFW_BLE_MSGTX_PB_NOTIFY_COMMAND_ROLE() \
    open_cfw_test_ble_msgtx_pb_notify_command_role()
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE( \
    transport, enabled, argument_1, argument_2, payload, length \
) \
    open_cfw_test_ble_msgtx_pb_direct_enqueue( \
        (transport), \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (payload), \
        (length) \
    )
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL() \
    open_cfw_test_ble_msgtx_pb_direct_log_level()
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG( \
    level, module, file, function, line, message \
) \
    open_cfw_test_ble_msgtx_pb_direct_log( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    )
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_TRACE(level, format, argument) \
    open_cfw_test_ble_msgtx_pb_direct_trace( \
        (level), \
        (format), \
        (argument) \
    )

unsigned int open_cfw_test_ble_msgtx_pb_direct_events[16];
unsigned int open_cfw_test_ble_msgtx_pb_direct_event_count;
unsigned int open_cfw_test_ble_msgtx_pb_direct_ota_result;
unsigned int open_cfw_test_ble_msgtx_pb_direct_ota_calls;
unsigned int open_cfw_test_ble_msgtx_pb_send_side_result;
unsigned int open_cfw_test_ble_msgtx_pb_send_side_calls;
unsigned int open_cfw_test_ble_msgtx_pb_notify_command_result;
unsigned int open_cfw_test_ble_msgtx_pb_notify_command_calls;
int open_cfw_test_ble_msgtx_pb_direct_enqueue_result;
unsigned int open_cfw_test_ble_msgtx_pb_direct_enqueue_calls;
unsigned int open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[5];
__UINTPTR_TYPE__ open_cfw_test_ble_msgtx_pb_direct_enqueue_payload;
unsigned int open_cfw_test_ble_msgtx_pb_direct_levels[8];
unsigned int open_cfw_test_ble_msgtx_pb_direct_level_count;
unsigned int open_cfw_test_ble_msgtx_pb_direct_level_index;
unsigned int open_cfw_test_ble_msgtx_pb_direct_log_calls;
unsigned int open_cfw_test_ble_msgtx_pb_direct_log_arguments[6];
unsigned int open_cfw_test_ble_msgtx_pb_direct_trace_calls;
unsigned int open_cfw_test_ble_msgtx_pb_direct_trace_arguments[3];

static void open_cfw_test_ble_msgtx_pb_direct_record(unsigned int event)
{
    open_cfw_test_ble_msgtx_pb_direct_events[
        open_cfw_test_ble_msgtx_pb_direct_event_count++
    ] = event;
}

void open_cfw_test_ble_msgtx_pb_direct_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_msgtx_pb_direct_events[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_msgtx_pb_direct_levels[index] = 0U;
    }
    for (index = 0U; index < 5U; ++index) {
        open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_ble_msgtx_pb_direct_log_arguments[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_ble_msgtx_pb_direct_trace_arguments[index] = 0U;
    }

    open_cfw_test_ble_msgtx_pb_direct_event_count = 0U;
    open_cfw_test_ble_msgtx_pb_direct_ota_result = 0U;
    open_cfw_test_ble_msgtx_pb_direct_ota_calls = 0U;
    open_cfw_test_ble_msgtx_pb_send_side_result = 0U;
    open_cfw_test_ble_msgtx_pb_send_side_calls = 0U;
    open_cfw_test_ble_msgtx_pb_notify_command_result = 1U;
    open_cfw_test_ble_msgtx_pb_notify_command_calls = 0U;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_result = 0;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_calls = 0U;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_payload = 0U;
    open_cfw_test_ble_msgtx_pb_direct_level_count = 0U;
    open_cfw_test_ble_msgtx_pb_direct_level_index = 0U;
    open_cfw_test_ble_msgtx_pb_direct_log_calls = 0U;
    open_cfw_test_ble_msgtx_pb_direct_trace_calls = 0U;
}

unsigned int open_cfw_test_ble_msgtx_pb_direct_ota_active(void)
{
    ++open_cfw_test_ble_msgtx_pb_direct_ota_calls;
    open_cfw_test_ble_msgtx_pb_direct_record(1U);
    return open_cfw_test_ble_msgtx_pb_direct_ota_result;
}

unsigned int open_cfw_test_ble_msgtx_pb_send_side_rejected(void)
{
    ++open_cfw_test_ble_msgtx_pb_send_side_calls;
    open_cfw_test_ble_msgtx_pb_direct_record(6U);
    return open_cfw_test_ble_msgtx_pb_send_side_result;
}

unsigned int open_cfw_test_ble_msgtx_pb_notify_command_role(void)
{
    ++open_cfw_test_ble_msgtx_pb_notify_command_calls;
    open_cfw_test_ble_msgtx_pb_direct_record(7U);
    return open_cfw_test_ble_msgtx_pb_notify_command_result;
}

int open_cfw_test_ble_msgtx_pb_direct_enqueue(
    unsigned char transport,
    unsigned char enabled,
    unsigned char argument_1,
    unsigned char argument_2,
    const void *payload,
    unsigned short length
)
{
    ++open_cfw_test_ble_msgtx_pb_direct_enqueue_calls;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[0] = transport;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[1] = enabled;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[2] = argument_1;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[3] = argument_2;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_arguments[4] = length;
    open_cfw_test_ble_msgtx_pb_direct_enqueue_payload =
        (__UINTPTR_TYPE__)payload;
    open_cfw_test_ble_msgtx_pb_direct_record(2U);
    return open_cfw_test_ble_msgtx_pb_direct_enqueue_result;
}

unsigned int open_cfw_test_ble_msgtx_pb_direct_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_ble_msgtx_pb_direct_level_index
        < open_cfw_test_ble_msgtx_pb_direct_level_count
    ) {
        value = open_cfw_test_ble_msgtx_pb_direct_levels[
            open_cfw_test_ble_msgtx_pb_direct_level_index
        ];
    }
    ++open_cfw_test_ble_msgtx_pb_direct_level_index;
    open_cfw_test_ble_msgtx_pb_direct_record(3U);
    return value;
}

void open_cfw_test_ble_msgtx_pb_direct_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message
)
{
    ++open_cfw_test_ble_msgtx_pb_direct_log_calls;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[0] = level;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)module;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)file;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[3] =
        (unsigned int)(__UINTPTR_TYPE__)function;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[4] = line;
    open_cfw_test_ble_msgtx_pb_direct_log_arguments[5] =
        (unsigned int)(__UINTPTR_TYPE__)message;
    open_cfw_test_ble_msgtx_pb_direct_record(4U);
}

void open_cfw_test_ble_msgtx_pb_direct_trace(
    unsigned int level,
    const void *format,
    const void *argument
)
{
    ++open_cfw_test_ble_msgtx_pb_direct_trace_calls;
    open_cfw_test_ble_msgtx_pb_direct_trace_arguments[0] = level;
    open_cfw_test_ble_msgtx_pb_direct_trace_arguments[1] =
        (unsigned int)(__UINTPTR_TYPE__)format;
    open_cfw_test_ble_msgtx_pb_direct_trace_arguments[2] =
        (unsigned int)(__UINTPTR_TYPE__)argument;
    open_cfw_test_ble_msgtx_pb_direct_record(5U);
}

#include "../../components/apollo_main/core_overlay/ble_msgtx_pb_direct.c"
