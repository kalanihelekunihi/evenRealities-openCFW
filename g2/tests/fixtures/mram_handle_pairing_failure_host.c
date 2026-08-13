/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for Cordio AppDbHandlePairingFailure.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT 128U
#define OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_WIDTH 16U

void open_cfw_test_mram_pairing_failure_show(void);
unsigned char *open_cfw_test_mram_pairing_failure_lookup(unsigned int);
void open_cfw_test_mram_pairing_failure_clear(unsigned int);
unsigned int open_cfw_test_mram_pairing_failure_level(void);
void open_cfw_test_mram_pairing_failure_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_pairing_failure_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_PAIRING_FAILURE_SHOW_NVM() \
    open_cfw_test_mram_pairing_failure_show()
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOOKUP(conn_id) \
    open_cfw_test_mram_pairing_failure_lookup(conn_id)
#define OPEN_CFW_MRAM_PAIRING_FAILURE_CLEAR(conn_id) \
    open_cfw_test_mram_pairing_failure_clear(conn_id)
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL() \
    open_cfw_test_mram_pairing_failure_level()
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(...) \
    open_cfw_test_mram_pairing_failure_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(...) \
    open_cfw_test_mram_pairing_failure_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_handle_pairing_failure.c"

unsigned char open_cfw_test_mram_pairing_failure_record[256];
unsigned int open_cfw_test_mram_pairing_failure_order[
    OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_pairing_failure_order_count;
unsigned int open_cfw_test_mram_pairing_failure_levels[
    OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_pairing_failure_level_count;
unsigned int open_cfw_test_mram_pairing_failure_level_index;
unsigned int open_cfw_test_mram_pairing_failure_level_default;
open_cfw_mram_pairing_failure_uintptr
open_cfw_test_mram_pairing_failure_logs[
    OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_pairing_failure_log_count;
open_cfw_mram_pairing_failure_uintptr
open_cfw_test_mram_pairing_failure_traces[
    OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_pairing_failure_trace_count;
unsigned int open_cfw_test_mram_pairing_failure_show_count;
unsigned int open_cfw_test_mram_pairing_failure_lookup_count;
unsigned int open_cfw_test_mram_pairing_failure_lookup_connection;
unsigned char *open_cfw_test_mram_pairing_failure_lookup_result;
unsigned int open_cfw_test_mram_pairing_failure_clear_count;
unsigned int open_cfw_test_mram_pairing_failure_clear_connection;
unsigned int open_cfw_test_mram_pairing_failure_clear_valid;
unsigned int open_cfw_test_mram_pairing_failure_clear_in_use;

static void open_cfw_test_mram_pairing_failure_order_append(
    unsigned int event
)
{
    if (
        open_cfw_test_mram_pairing_failure_order_count
        < OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_pairing_failure_order[
            open_cfw_test_mram_pairing_failure_order_count
        ] = event;
    }
    ++open_cfw_test_mram_pairing_failure_order_count;
}

static unsigned int open_cfw_test_mram_pairing_failure_log_arguments(
    unsigned int line
)
{
    if (line == 0x872U) {
        return 2U;
    }
    if (line == 0x880U) {
        return 6U;
    }
    if (line == 0x896U || line == 0x8A6U) {
        return 1U;
    }
    if (line == 0x89FU) {
        return 3U;
    }
    return 0U;
}

static unsigned int open_cfw_test_mram_pairing_failure_trace_arguments(
    unsigned int event
)
{
    if (event == 0x10800000U) {
        return 2U;
    }
    if (event == 0x09800000U) {
        return 6U;
    }
    if (event == 0x08400000U || event == 0x10400000U) {
        return 1U;
    }
    if (event == 0x10C00000U) {
        return 3U;
    }
    return 0U;
}

void open_cfw_test_mram_pairing_failure_reset(void)
{
    memset(
        open_cfw_test_mram_pairing_failure_record,
        0,
        sizeof(open_cfw_test_mram_pairing_failure_record)
    );
    memset(
        open_cfw_test_mram_pairing_failure_order,
        0,
        sizeof(open_cfw_test_mram_pairing_failure_order)
    );
    memset(
        open_cfw_test_mram_pairing_failure_levels,
        0,
        sizeof(open_cfw_test_mram_pairing_failure_levels)
    );
    memset(
        open_cfw_test_mram_pairing_failure_logs,
        0,
        sizeof(open_cfw_test_mram_pairing_failure_logs)
    );
    memset(
        open_cfw_test_mram_pairing_failure_traces,
        0,
        sizeof(open_cfw_test_mram_pairing_failure_traces)
    );
    open_cfw_test_mram_pairing_failure_order_count = 0U;
    open_cfw_test_mram_pairing_failure_level_count = 0U;
    open_cfw_test_mram_pairing_failure_level_index = 0U;
    open_cfw_test_mram_pairing_failure_level_default = 0U;
    open_cfw_test_mram_pairing_failure_log_count = 0U;
    open_cfw_test_mram_pairing_failure_trace_count = 0U;
    open_cfw_test_mram_pairing_failure_show_count = 0U;
    open_cfw_test_mram_pairing_failure_lookup_count = 0U;
    open_cfw_test_mram_pairing_failure_lookup_connection = 0U;
    open_cfw_test_mram_pairing_failure_lookup_result =
        (unsigned char *)0;
    open_cfw_test_mram_pairing_failure_clear_count = 0U;
    open_cfw_test_mram_pairing_failure_clear_connection = 0U;
    open_cfw_test_mram_pairing_failure_clear_valid = 0U;
    open_cfw_test_mram_pairing_failure_clear_in_use = 0U;
}

unsigned int open_cfw_test_mram_pairing_failure_level(void)
{
    unsigned int index =
        open_cfw_test_mram_pairing_failure_level_index++;
    unsigned int result =
        open_cfw_test_mram_pairing_failure_level_default;

    open_cfw_test_mram_pairing_failure_order_append(1U);
    if (index < open_cfw_test_mram_pairing_failure_level_count) {
        result = open_cfw_test_mram_pairing_failure_levels[index];
    }
    return result;
}

void open_cfw_test_mram_pairing_failure_show(void)
{
    open_cfw_test_mram_pairing_failure_order_append(4U);
    ++open_cfw_test_mram_pairing_failure_show_count;
}

unsigned char *open_cfw_test_mram_pairing_failure_lookup(
    unsigned int connection
)
{
    open_cfw_test_mram_pairing_failure_order_append(5U);
    ++open_cfw_test_mram_pairing_failure_lookup_count;
    open_cfw_test_mram_pairing_failure_lookup_connection = connection;
    return open_cfw_test_mram_pairing_failure_lookup_result;
}

void open_cfw_test_mram_pairing_failure_clear(unsigned int connection)
{
    open_cfw_test_mram_pairing_failure_order_append(6U);
    ++open_cfw_test_mram_pairing_failure_clear_count;
    open_cfw_test_mram_pairing_failure_clear_connection = connection;
    open_cfw_test_mram_pairing_failure_clear_valid =
        open_cfw_test_mram_pairing_failure_record[0x30U];
    open_cfw_test_mram_pairing_failure_clear_in_use =
        open_cfw_test_mram_pairing_failure_record[0x2FU];
}

void open_cfw_test_mram_pairing_failure_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_pairing_failure_log_count;
    unsigned int count =
        open_cfw_test_mram_pairing_failure_log_arguments(line);
    va_list arguments;

    open_cfw_test_mram_pairing_failure_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT) {
        open_cfw_mram_pairing_failure_uintptr *output =
            open_cfw_test_mram_pairing_failure_logs
            + call * OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = severity;
        output[1] = (open_cfw_mram_pairing_failure_uintptr)module;
        output[2] = (open_cfw_mram_pairing_failure_uintptr)file;
        output[3] = (open_cfw_mram_pairing_failure_uintptr)function;
        output[4] = line;
        output[5] = (open_cfw_mram_pairing_failure_uintptr)identity;
        output[6] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[7U + index] = va_arg(
                arguments,
                open_cfw_mram_pairing_failure_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_pairing_failure_log_count;
}

void open_cfw_test_mram_pairing_failure_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_pairing_failure_trace_count;
    unsigned int count =
        open_cfw_test_mram_pairing_failure_trace_arguments(event);
    va_list arguments;

    open_cfw_test_mram_pairing_failure_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_COUNT) {
        open_cfw_mram_pairing_failure_uintptr *output =
            open_cfw_test_mram_pairing_failure_traces
            + call * OPEN_CFW_TEST_MRAM_PAIRING_FAILURE_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = event;
        output[1] = (open_cfw_mram_pairing_failure_uintptr)schema;
        output[2] = (open_cfw_mram_pairing_failure_uintptr)identity;
        output[3] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[4U + index] = va_arg(
                arguments,
                open_cfw_mram_pairing_failure_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_pairing_failure_trace_count;
}
