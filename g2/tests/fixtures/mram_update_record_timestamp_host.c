/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for Cordio AppDbUpdateRecordTimestamp.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT 64U
#define OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_WIDTH 9U

void open_cfw_test_mram_timestamp_reset_timestamps(void);
unsigned int open_cfw_test_mram_timestamp_update(
    const unsigned char *
);
unsigned int open_cfw_test_mram_timestamp_verify(
    const unsigned char *
);
unsigned int open_cfw_test_mram_timestamp_log_level(void);
void open_cfw_test_mram_timestamp_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_timestamp_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned int open_cfw_test_mram_timestamp_counter;

#define OPEN_CFW_MRAM_TIMESTAMP_COUNTER \
    open_cfw_test_mram_timestamp_counter
#define OPEN_CFW_MRAM_TIMESTAMP_RESET() \
    open_cfw_test_mram_timestamp_reset_timestamps()
#define OPEN_CFW_MRAM_TIMESTAMP_UPDATE(record) \
    open_cfw_test_mram_timestamp_update((record))
#define OPEN_CFW_MRAM_TIMESTAMP_VERIFY(record) \
    open_cfw_test_mram_timestamp_verify((record))
#define OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL() \
    open_cfw_test_mram_timestamp_log_level()
#define OPEN_CFW_MRAM_TIMESTAMP_LOG(...) \
    open_cfw_test_mram_timestamp_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_TIMESTAMP_TRACE(...) \
    open_cfw_test_mram_timestamp_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_update_record_timestamp.c"

unsigned int open_cfw_test_mram_timestamp_order[
    OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_timestamp_order_count;
unsigned int open_cfw_test_mram_timestamp_levels[
    OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_timestamp_level_count;
unsigned int open_cfw_test_mram_timestamp_level_index;
unsigned int open_cfw_test_mram_timestamp_level_default;
open_cfw_mram_timestamp_uintptr open_cfw_test_mram_timestamp_logs[
    OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_timestamp_log_count;
open_cfw_mram_timestamp_uintptr open_cfw_test_mram_timestamp_traces[
    OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_timestamp_trace_count;
unsigned int open_cfw_test_mram_timestamp_reset_count;
unsigned int open_cfw_test_mram_timestamp_reset_value;
unsigned int open_cfw_test_mram_timestamp_update_count;
open_cfw_mram_timestamp_uintptr open_cfw_test_mram_timestamp_update_record;
unsigned int open_cfw_test_mram_timestamp_update_result;
unsigned int open_cfw_test_mram_timestamp_verify_count;
open_cfw_mram_timestamp_uintptr open_cfw_test_mram_timestamp_verify_record;
unsigned int open_cfw_test_mram_timestamp_verify_result;

static void open_cfw_test_mram_timestamp_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_timestamp_order_count
        < OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_timestamp_order[
            open_cfw_test_mram_timestamp_order_count
        ] = event;
    }
    ++open_cfw_test_mram_timestamp_order_count;
}

void open_cfw_test_mram_timestamp_reset(void)
{
    memset(
        open_cfw_test_mram_timestamp_order,
        0,
        sizeof(open_cfw_test_mram_timestamp_order)
    );
    memset(
        open_cfw_test_mram_timestamp_levels,
        0,
        sizeof(open_cfw_test_mram_timestamp_levels)
    );
    memset(
        open_cfw_test_mram_timestamp_logs,
        0,
        sizeof(open_cfw_test_mram_timestamp_logs)
    );
    memset(
        open_cfw_test_mram_timestamp_traces,
        0,
        sizeof(open_cfw_test_mram_timestamp_traces)
    );
    open_cfw_test_mram_timestamp_counter = 0U;
    open_cfw_test_mram_timestamp_order_count = 0U;
    open_cfw_test_mram_timestamp_level_count = 0U;
    open_cfw_test_mram_timestamp_level_index = 0U;
    open_cfw_test_mram_timestamp_level_default = 0U;
    open_cfw_test_mram_timestamp_log_count = 0U;
    open_cfw_test_mram_timestamp_trace_count = 0U;
    open_cfw_test_mram_timestamp_reset_count = 0U;
    open_cfw_test_mram_timestamp_reset_value = 0U;
    open_cfw_test_mram_timestamp_update_count = 0U;
    open_cfw_test_mram_timestamp_update_record = 0U;
    open_cfw_test_mram_timestamp_update_result = 0U;
    open_cfw_test_mram_timestamp_verify_count = 0U;
    open_cfw_test_mram_timestamp_verify_record = 0U;
    open_cfw_test_mram_timestamp_verify_result = 0U;
}

unsigned int open_cfw_test_mram_timestamp_log_level(void)
{
    unsigned int index = open_cfw_test_mram_timestamp_level_index++;
    unsigned int result = open_cfw_test_mram_timestamp_level_default;

    open_cfw_test_mram_timestamp_order_append(1U);
    if (index < open_cfw_test_mram_timestamp_level_count) {
        result = open_cfw_test_mram_timestamp_levels[index];
    }
    return result;
}

void open_cfw_test_mram_timestamp_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_timestamp_log_count;
    unsigned int count = line == 0x818U ? 1U : 0U;
    va_list arguments;

    open_cfw_test_mram_timestamp_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT) {
        open_cfw_mram_timestamp_uintptr *output =
            open_cfw_test_mram_timestamp_logs
            + call * OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_WIDTH;

        output[0] = severity;
        output[1] = (open_cfw_mram_timestamp_uintptr)module;
        output[2] = (open_cfw_mram_timestamp_uintptr)file;
        output[3] = (open_cfw_mram_timestamp_uintptr)function;
        output[4] = line;
        output[5] = (open_cfw_mram_timestamp_uintptr)identity;
        output[6] = count;
        va_start(arguments, identity);
        if (count != 0U) {
            output[7] = va_arg(
                arguments,
                open_cfw_mram_timestamp_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_timestamp_log_count;
}

void open_cfw_test_mram_timestamp_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_timestamp_trace_count;
    unsigned int count = event == 0x10400000U ? 1U : 0U;
    va_list arguments;

    open_cfw_test_mram_timestamp_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_COUNT) {
        open_cfw_mram_timestamp_uintptr *output =
            open_cfw_test_mram_timestamp_traces
            + call * OPEN_CFW_TEST_MRAM_TIMESTAMP_CAPTURE_WIDTH;

        output[0] = event;
        output[1] = (open_cfw_mram_timestamp_uintptr)schema;
        output[2] = (open_cfw_mram_timestamp_uintptr)identity;
        output[3] = count;
        va_start(arguments, identity);
        if (count != 0U) {
            output[4] = va_arg(
                arguments,
                open_cfw_mram_timestamp_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_timestamp_trace_count;
}

void open_cfw_test_mram_timestamp_reset_timestamps(void)
{
    open_cfw_test_mram_timestamp_order_append(4U);
    ++open_cfw_test_mram_timestamp_reset_count;
    open_cfw_test_mram_timestamp_counter =
        open_cfw_test_mram_timestamp_reset_value;
}

unsigned int open_cfw_test_mram_timestamp_update(
    const unsigned char *record
)
{
    open_cfw_test_mram_timestamp_order_append(5U);
    ++open_cfw_test_mram_timestamp_update_count;
    open_cfw_test_mram_timestamp_update_record =
        (open_cfw_mram_timestamp_uintptr)record;
    return open_cfw_test_mram_timestamp_update_result;
}

unsigned int open_cfw_test_mram_timestamp_verify(
    const unsigned char *record
)
{
    open_cfw_test_mram_timestamp_order_append(6U);
    ++open_cfw_test_mram_timestamp_verify_count;
    open_cfw_test_mram_timestamp_verify_record =
        (open_cfw_mram_timestamp_uintptr)record;
    return open_cfw_test_mram_timestamp_verify_result;
}
