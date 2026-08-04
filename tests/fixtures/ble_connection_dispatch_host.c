/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the BLE connection-event dispatcher.
 */

#include <stdarg.h>

unsigned int open_cfw_test_ble_dispatch_profile(void);
unsigned int open_cfw_test_ble_dispatch_kind(unsigned char);
unsigned int open_cfw_test_ble_dispatch_log_level(void);
void open_cfw_test_ble_dispatch_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_ble_dispatch_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_ble_dispatch_apply_remote(const unsigned char *);
void open_cfw_test_ble_dispatch_handle_event(const unsigned char *);
void open_cfw_test_ble_dispatch_schedule(unsigned char, unsigned char *);
unsigned char open_cfw_test_ble_dispatch_remove(void *);
void open_cfw_test_ble_dispatch_coordinate(unsigned char);

unsigned char open_cfw_test_ble_dispatch_states[3U * 0x30U];
unsigned char open_cfw_test_ble_dispatch_pending;
unsigned char open_cfw_test_ble_dispatch_previous_mode;
const volatile unsigned short *open_cfw_test_ble_dispatch_defaults;
unsigned short open_cfw_test_ble_dispatch_short_primary[8];
unsigned short open_cfw_test_ble_dispatch_short_secondary[8];
unsigned short open_cfw_test_ble_dispatch_long_defaults[8];

#define OPEN_CFW_BLE_DISPATCH_STATE_BASE \
    open_cfw_test_ble_dispatch_states
#define OPEN_CFW_BLE_DISPATCH_PENDING \
    open_cfw_test_ble_dispatch_pending
#define OPEN_CFW_BLE_DISPATCH_PREVIOUS_MODE \
    open_cfw_test_ble_dispatch_previous_mode
#define OPEN_CFW_BLE_DISPATCH_DEFAULTS \
    open_cfw_test_ble_dispatch_defaults
#define OPEN_CFW_BLE_DISPATCH_SHORT_PRIMARY \
    open_cfw_test_ble_dispatch_short_primary
#define OPEN_CFW_BLE_DISPATCH_SHORT_SECONDARY \
    open_cfw_test_ble_dispatch_short_secondary
#define OPEN_CFW_BLE_DISPATCH_LONG_DEFAULTS \
    open_cfw_test_ble_dispatch_long_defaults
#define OPEN_CFW_BLE_DISPATCH_PROFILE() \
    open_cfw_test_ble_dispatch_profile()
#define OPEN_CFW_BLE_DISPATCH_KIND(identifier) \
    open_cfw_test_ble_dispatch_kind(identifier)
#define OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() \
    open_cfw_test_ble_dispatch_log_level()
#define OPEN_CFW_BLE_DISPATCH_LOG(...) \
    open_cfw_test_ble_dispatch_log(__VA_ARGS__)
#define OPEN_CFW_BLE_DISPATCH_TRACE(...) \
    open_cfw_test_ble_dispatch_trace(__VA_ARGS__)
#define OPEN_CFW_BLE_DISPATCH_APPLY_REMOTE(parameters) \
    open_cfw_test_ble_dispatch_apply_remote(parameters)
#define OPEN_CFW_BLE_DISPATCH_HANDLE_EVENT(event) \
    open_cfw_test_ble_dispatch_handle_event(event)
#define OPEN_CFW_BLE_DISPATCH_SCHEDULE(mode, state) \
    open_cfw_test_ble_dispatch_schedule((mode), (state))
#define OPEN_CFW_BLE_DISPATCH_REMOVE(callback) \
    open_cfw_test_ble_dispatch_remove((void *)(callback))
#define OPEN_CFW_BLE_DISPATCH_COORDINATE(mode) \
    open_cfw_test_ble_dispatch_coordinate(mode)

#include "../../components/apollo_main/core_overlay/ble_connection_dispatch.c"

#define OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH 12U

unsigned char open_cfw_test_ble_dispatch_message[16];
unsigned int open_cfw_test_ble_dispatch_profile_result;
unsigned int open_cfw_test_ble_dispatch_profile_calls;
unsigned int open_cfw_test_ble_dispatch_kind_result;
unsigned int open_cfw_test_ble_dispatch_kind_calls;
unsigned char open_cfw_test_ble_dispatch_kind_identifier;
unsigned int open_cfw_test_ble_dispatch_levels[64];
unsigned int open_cfw_test_ble_dispatch_level_count;
unsigned int open_cfw_test_ble_dispatch_level_index;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_log_records[
    16U * OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_dispatch_log_count;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_trace_records[
    16U * OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH
];
unsigned int open_cfw_test_ble_dispatch_trace_count;
unsigned int open_cfw_test_ble_dispatch_apply_remote_calls;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_apply_remote_pointer;
unsigned int open_cfw_test_ble_dispatch_handle_event_calls;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_handle_event_pointer;
unsigned int open_cfw_test_ble_dispatch_schedule_calls;
unsigned char open_cfw_test_ble_dispatch_schedule_mode;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_schedule_state;
unsigned int open_cfw_test_ble_dispatch_remove_calls;
open_cfw_ble_dispatch_uintptr open_cfw_test_ble_dispatch_remove_callback;
unsigned int open_cfw_test_ble_dispatch_coordinate_calls;
unsigned char open_cfw_test_ble_dispatch_coordinate_mode;

void open_cfw_test_ble_dispatch_reset(void)
{
    unsigned int index;

    for (index = 0U; index < sizeof(open_cfw_test_ble_dispatch_states);
         ++index) {
        open_cfw_test_ble_dispatch_states[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_ble_dispatch_message[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_ble_dispatch_short_primary[index] = 0U;
        open_cfw_test_ble_dispatch_short_secondary[index] = 0U;
        open_cfw_test_ble_dispatch_long_defaults[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_ble_dispatch_levels[index] = 0U;
    }
    for (
        index = 0U;
        index < 16U * OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_ble_dispatch_log_records[index] = 0U;
        open_cfw_test_ble_dispatch_trace_records[index] = 0U;
    }

    open_cfw_test_ble_dispatch_pending = 0U;
    open_cfw_test_ble_dispatch_previous_mode = 0U;
    open_cfw_test_ble_dispatch_defaults =
        (const volatile unsigned short *)0;
    open_cfw_test_ble_dispatch_profile_result = 0U;
    open_cfw_test_ble_dispatch_profile_calls = 0U;
    open_cfw_test_ble_dispatch_kind_result = 0U;
    open_cfw_test_ble_dispatch_kind_calls = 0U;
    open_cfw_test_ble_dispatch_kind_identifier = 0U;
    open_cfw_test_ble_dispatch_level_count = 0U;
    open_cfw_test_ble_dispatch_level_index = 0U;
    open_cfw_test_ble_dispatch_log_count = 0U;
    open_cfw_test_ble_dispatch_trace_count = 0U;
    open_cfw_test_ble_dispatch_apply_remote_calls = 0U;
    open_cfw_test_ble_dispatch_apply_remote_pointer = 0U;
    open_cfw_test_ble_dispatch_handle_event_calls = 0U;
    open_cfw_test_ble_dispatch_handle_event_pointer = 0U;
    open_cfw_test_ble_dispatch_schedule_calls = 0U;
    open_cfw_test_ble_dispatch_schedule_mode = 0U;
    open_cfw_test_ble_dispatch_schedule_state = 0U;
    open_cfw_test_ble_dispatch_remove_calls = 0U;
    open_cfw_test_ble_dispatch_remove_callback = 0U;
    open_cfw_test_ble_dispatch_coordinate_calls = 0U;
    open_cfw_test_ble_dispatch_coordinate_mode = 0U;
}

unsigned int open_cfw_test_ble_dispatch_profile(void)
{
    ++open_cfw_test_ble_dispatch_profile_calls;
    return open_cfw_test_ble_dispatch_profile_result;
}

unsigned int open_cfw_test_ble_dispatch_kind(unsigned char identifier)
{
    ++open_cfw_test_ble_dispatch_kind_calls;
    open_cfw_test_ble_dispatch_kind_identifier = identifier;
    return open_cfw_test_ble_dispatch_kind_result;
}

unsigned int open_cfw_test_ble_dispatch_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_ble_dispatch_level_index
        < open_cfw_test_ble_dispatch_level_count
    ) {
        result = open_cfw_test_ble_dispatch_levels[
            open_cfw_test_ble_dispatch_level_index
        ];
    }
    ++open_cfw_test_ble_dispatch_level_index;
    return result;
}

static unsigned int open_cfw_test_ble_dispatch_argument_count(
    open_cfw_ble_dispatch_uintptr identity
)
{
    if (
        identity == 0x007316C4U
        || identity == 0x00751D1CU
        || identity == 0x00731754U
        || identity == 0x00751D40U
        || identity == 0x00751D64U
    ) {
        return 1U;
    }
    if (
        identity == 0x00726C50U
        || identity == 0x00731724U
        || identity == 0x0073C00CU
    ) {
        return 2U;
    }
    if (identity == 0x0071BEB0U) {
        return 4U;
    }
    return 0U;
}

static int open_cfw_test_ble_dispatch_argument_is_state_pointer(
    open_cfw_ble_dispatch_uintptr identity
)
{
    return (
        identity == 0x00751D1CU
        || identity == 0x00751D40U
        || identity == 0x007316F4U
        || identity == 0x00731784U
    );
}

void open_cfw_test_ble_dispatch_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_ble_dispatch_uintptr *record;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (open_cfw_test_ble_dispatch_log_count >= 16U) {
        ++open_cfw_test_ble_dispatch_log_count;
        return;
    }
    record = &open_cfw_test_ble_dispatch_log_records[
        open_cfw_test_ble_dispatch_log_count
        * OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH
    ];
    record[0] = severity;
    record[1] = (open_cfw_ble_dispatch_uintptr)module;
    record[2] = (open_cfw_ble_dispatch_uintptr)file;
    record[3] = (open_cfw_ble_dispatch_uintptr)function;
    record[4] = line;
    record[5] = (open_cfw_ble_dispatch_uintptr)identity;
    count = open_cfw_test_ble_dispatch_argument_count(record[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        if (
            open_cfw_test_ble_dispatch_argument_is_state_pointer(
                record[5]
            )
        ) {
            record[6U + index] = (open_cfw_ble_dispatch_uintptr)va_arg(
                arguments,
                unsigned char *
            );
        }
        else {
            record[6U + index] = (unsigned int)va_arg(
                arguments,
                int
            );
        }
    }
    va_end(arguments);
    ++open_cfw_test_ble_dispatch_log_count;
}

static unsigned int open_cfw_test_ble_dispatch_trace_argument_count(
    open_cfw_ble_dispatch_uintptr identity
)
{
    if (
        identity == 0x0071249CU
        || identity == 0x007316F4U
        || identity == 0x00708FA4U
        || identity == 0x007124D8U
        || identity == 0x00712514U
        || identity == 0x00731784U
        || identity == 0x0071BE78U
        || identity == 0x007317B4U
    ) {
        return (
            identity == 0x00708FA4U
            || identity == 0x007124D8U
            || identity == 0x0071BE78U
        ) ? 2U : 1U;
    }
    if (identity == 0x0070016CU) {
        return 4U;
    }
    return 0U;
}

void open_cfw_test_ble_dispatch_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_ble_dispatch_uintptr *record;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (open_cfw_test_ble_dispatch_trace_count >= 16U) {
        ++open_cfw_test_ble_dispatch_trace_count;
        return;
    }
    record = &open_cfw_test_ble_dispatch_trace_records[
        open_cfw_test_ble_dispatch_trace_count
        * OPEN_CFW_TEST_BLE_DISPATCH_RECORD_WIDTH
    ];
    record[0] = event;
    record[1] = (open_cfw_ble_dispatch_uintptr)identity;
    record[2] = (open_cfw_ble_dispatch_uintptr)duplicate_identity;
    count = open_cfw_test_ble_dispatch_trace_argument_count(record[1]);
    va_start(arguments, duplicate_identity);
    for (index = 0U; index < count; ++index) {
        if (
            open_cfw_test_ble_dispatch_argument_is_state_pointer(
                record[1]
            )
        ) {
            record[3U + index] = (open_cfw_ble_dispatch_uintptr)va_arg(
                arguments,
                unsigned char *
            );
        }
        else {
            record[3U + index] = (unsigned int)va_arg(
                arguments,
                int
            );
        }
    }
    va_end(arguments);
    ++open_cfw_test_ble_dispatch_trace_count;
}

void open_cfw_test_ble_dispatch_apply_remote(
    const unsigned char *parameters
)
{
    ++open_cfw_test_ble_dispatch_apply_remote_calls;
    open_cfw_test_ble_dispatch_apply_remote_pointer =
        (open_cfw_ble_dispatch_uintptr)parameters;
}

void open_cfw_test_ble_dispatch_handle_event(const unsigned char *event)
{
    ++open_cfw_test_ble_dispatch_handle_event_calls;
    open_cfw_test_ble_dispatch_handle_event_pointer =
        (open_cfw_ble_dispatch_uintptr)event;
}

void open_cfw_test_ble_dispatch_schedule(
    unsigned char mode,
    unsigned char *state
)
{
    ++open_cfw_test_ble_dispatch_schedule_calls;
    open_cfw_test_ble_dispatch_schedule_mode = mode;
    open_cfw_test_ble_dispatch_schedule_state =
        (open_cfw_ble_dispatch_uintptr)state;
}

unsigned char open_cfw_test_ble_dispatch_remove(void *callback)
{
    ++open_cfw_test_ble_dispatch_remove_calls;
    open_cfw_test_ble_dispatch_remove_callback =
        (open_cfw_ble_dispatch_uintptr)callback;
    return 0U;
}

void open_cfw_test_ble_dispatch_coordinate(unsigned char mode)
{
    ++open_cfw_test_ble_dispatch_coordinate_calls;
    open_cfw_test_ble_dispatch_coordinate_mode = mode;
}
