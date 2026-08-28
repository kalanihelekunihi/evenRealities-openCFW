/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for Cordio AppDbClearRecordByConnId.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT 128U
#define OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_WIDTH 16U

unsigned char *open_cfw_test_mram_clear_connection_lookup(unsigned int);
unsigned int open_cfw_test_mram_clear_connection_clear(
    unsigned int,
    const unsigned char *
);
void open_cfw_test_mram_clear_connection_reload(void);
unsigned int open_cfw_test_mram_clear_connection_level(void);
void open_cfw_test_mram_clear_connection_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_clear_connection_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOOKUP(conn_id) \
    open_cfw_test_mram_clear_connection_lookup(conn_id)
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_CLEAR(owner, address) \
    open_cfw_test_mram_clear_connection_clear((owner), (address))
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_RELOAD() \
    open_cfw_test_mram_clear_connection_reload()
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() \
    open_cfw_test_mram_clear_connection_level()
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(...) \
    open_cfw_test_mram_clear_connection_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(...) \
    open_cfw_test_mram_clear_connection_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_clear_record_by_connection.c"

unsigned char open_cfw_test_mram_clear_connection_record[256];
unsigned int open_cfw_test_mram_clear_connection_order[
    OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_clear_connection_order_count;
unsigned int open_cfw_test_mram_clear_connection_levels[
    OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_clear_connection_level_count;
unsigned int open_cfw_test_mram_clear_connection_level_index;
unsigned int open_cfw_test_mram_clear_connection_level_default;
open_cfw_mram_clear_connection_uintptr
open_cfw_test_mram_clear_connection_logs[
    OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_clear_connection_log_count;
open_cfw_mram_clear_connection_uintptr
open_cfw_test_mram_clear_connection_traces[
    OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_clear_connection_trace_count;
unsigned int open_cfw_test_mram_clear_connection_lookup_count;
unsigned int open_cfw_test_mram_clear_connection_lookup_connection;
unsigned char *open_cfw_test_mram_clear_connection_lookup_result;
unsigned int open_cfw_test_mram_clear_connection_clear_count;
unsigned int open_cfw_test_mram_clear_connection_clear_owner;
open_cfw_mram_clear_connection_uintptr
open_cfw_test_mram_clear_connection_clear_address;
unsigned int open_cfw_test_mram_clear_connection_clear_result;
unsigned int open_cfw_test_mram_clear_connection_reload_count;

static void open_cfw_test_mram_clear_connection_order_append(
    unsigned int event
)
{
    if (
        open_cfw_test_mram_clear_connection_order_count
        < OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_clear_connection_order[
            open_cfw_test_mram_clear_connection_order_count
        ] = event;
    }
    ++open_cfw_test_mram_clear_connection_order_count;
}

static unsigned int open_cfw_test_mram_clear_connection_log_arguments(
    unsigned int line
)
{
    if (line == 0x8BBU) {
        return 6U;
    }
    if (line == 0x8C9U) {
        return 3U;
    }
    if (line == 0x8D0U) {
        return 1U;
    }
    return 0U;
}

static unsigned int open_cfw_test_mram_clear_connection_trace_arguments(
    unsigned int event
)
{
    if (event == 0x09800000U) {
        return 6U;
    }
    if (event == 0x10C00000U) {
        return 3U;
    }
    if (event == 0x10400000U) {
        return 1U;
    }
    return 0U;
}

void open_cfw_test_mram_clear_connection_reset(void)
{
    memset(
        open_cfw_test_mram_clear_connection_record,
        0,
        sizeof(open_cfw_test_mram_clear_connection_record)
    );
    memset(
        open_cfw_test_mram_clear_connection_order,
        0,
        sizeof(open_cfw_test_mram_clear_connection_order)
    );
    memset(
        open_cfw_test_mram_clear_connection_levels,
        0,
        sizeof(open_cfw_test_mram_clear_connection_levels)
    );
    memset(
        open_cfw_test_mram_clear_connection_logs,
        0,
        sizeof(open_cfw_test_mram_clear_connection_logs)
    );
    memset(
        open_cfw_test_mram_clear_connection_traces,
        0,
        sizeof(open_cfw_test_mram_clear_connection_traces)
    );
    open_cfw_test_mram_clear_connection_order_count = 0U;
    open_cfw_test_mram_clear_connection_level_count = 0U;
    open_cfw_test_mram_clear_connection_level_index = 0U;
    open_cfw_test_mram_clear_connection_level_default = 0U;
    open_cfw_test_mram_clear_connection_log_count = 0U;
    open_cfw_test_mram_clear_connection_trace_count = 0U;
    open_cfw_test_mram_clear_connection_lookup_count = 0U;
    open_cfw_test_mram_clear_connection_lookup_connection = 0U;
    open_cfw_test_mram_clear_connection_lookup_result = (unsigned char *)0;
    open_cfw_test_mram_clear_connection_clear_count = 0U;
    open_cfw_test_mram_clear_connection_clear_owner = 0U;
    open_cfw_test_mram_clear_connection_clear_address = 0U;
    open_cfw_test_mram_clear_connection_clear_result = 0U;
    open_cfw_test_mram_clear_connection_reload_count = 0U;
}

unsigned int open_cfw_test_mram_clear_connection_level(void)
{
    unsigned int index =
        open_cfw_test_mram_clear_connection_level_index++;
    unsigned int result =
        open_cfw_test_mram_clear_connection_level_default;

    open_cfw_test_mram_clear_connection_order_append(1U);
    if (index < open_cfw_test_mram_clear_connection_level_count) {
        result = open_cfw_test_mram_clear_connection_levels[index];
    }
    return result;
}

unsigned char *open_cfw_test_mram_clear_connection_lookup(
    unsigned int connection
)
{
    open_cfw_test_mram_clear_connection_order_append(4U);
    ++open_cfw_test_mram_clear_connection_lookup_count;
    open_cfw_test_mram_clear_connection_lookup_connection = connection;
    return open_cfw_test_mram_clear_connection_lookup_result;
}

unsigned int open_cfw_test_mram_clear_connection_clear(
    unsigned int owner,
    const unsigned char *address
)
{
    open_cfw_test_mram_clear_connection_order_append(5U);
    ++open_cfw_test_mram_clear_connection_clear_count;
    open_cfw_test_mram_clear_connection_clear_owner = owner;
    open_cfw_test_mram_clear_connection_clear_address =
        (open_cfw_mram_clear_connection_uintptr)address;
    return open_cfw_test_mram_clear_connection_clear_result;
}

void open_cfw_test_mram_clear_connection_reload(void)
{
    open_cfw_test_mram_clear_connection_order_append(6U);
    ++open_cfw_test_mram_clear_connection_reload_count;
}

void open_cfw_test_mram_clear_connection_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_clear_connection_log_count;
    unsigned int count =
        open_cfw_test_mram_clear_connection_log_arguments(line);
    va_list arguments;

    open_cfw_test_mram_clear_connection_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT) {
        open_cfw_mram_clear_connection_uintptr *output =
            open_cfw_test_mram_clear_connection_logs
            + call * OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = severity;
        output[1] = (open_cfw_mram_clear_connection_uintptr)module;
        output[2] = (open_cfw_mram_clear_connection_uintptr)file;
        output[3] = (open_cfw_mram_clear_connection_uintptr)function;
        output[4] = line;
        output[5] = (open_cfw_mram_clear_connection_uintptr)identity;
        output[6] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[7U + index] = va_arg(
                arguments,
                open_cfw_mram_clear_connection_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_clear_connection_log_count;
}

void open_cfw_test_mram_clear_connection_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_clear_connection_trace_count;
    unsigned int count =
        open_cfw_test_mram_clear_connection_trace_arguments(event);
    va_list arguments;

    open_cfw_test_mram_clear_connection_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_COUNT) {
        open_cfw_mram_clear_connection_uintptr *output =
            open_cfw_test_mram_clear_connection_traces
            + call * OPEN_CFW_TEST_MRAM_CLEAR_CONNECTION_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = event;
        output[1] = (open_cfw_mram_clear_connection_uintptr)schema;
        output[2] = (open_cfw_mram_clear_connection_uintptr)identity;
        output[3] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[4U + index] = va_arg(
                arguments,
                open_cfw_mram_clear_connection_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_clear_connection_trace_count;
}
