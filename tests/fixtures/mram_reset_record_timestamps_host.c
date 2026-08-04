/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for Cordio AppDbResetRecordTimestamps.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT 128U
#define OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_WIDTH 9U
#define OPEN_CFW_TEST_MRAM_RENUMBER_RECORD_BYTES 2000U

unsigned int open_cfw_test_mram_renumber_update(
    const unsigned char *
);
unsigned int open_cfw_test_mram_renumber_log_level(void);
void open_cfw_test_mram_renumber_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_renumber_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_renumber_records[
    OPEN_CFW_TEST_MRAM_RENUMBER_RECORD_BYTES
];
unsigned int open_cfw_test_mram_renumber_counter;

#define OPEN_CFW_MRAM_RENUMBER_COUNTER \
    open_cfw_test_mram_renumber_counter
#define OPEN_CFW_MRAM_RENUMBER_RECORD_BASE \
    open_cfw_test_mram_renumber_records
#define OPEN_CFW_MRAM_RENUMBER_UPDATE(record) \
    open_cfw_test_mram_renumber_update((record))
#define OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL() \
    open_cfw_test_mram_renumber_log_level()
#define OPEN_CFW_MRAM_RENUMBER_LOG(...) \
    open_cfw_test_mram_renumber_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_RENUMBER_TRACE(...) \
    open_cfw_test_mram_renumber_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_reset_record_timestamps.c"

unsigned int open_cfw_test_mram_renumber_order[
    OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_renumber_order_count;
unsigned int open_cfw_test_mram_renumber_levels[
    OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_renumber_level_count;
unsigned int open_cfw_test_mram_renumber_level_index;
unsigned int open_cfw_test_mram_renumber_level_default;
open_cfw_mram_renumber_uintptr open_cfw_test_mram_renumber_logs[
    OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_renumber_log_count;
open_cfw_mram_renumber_uintptr open_cfw_test_mram_renumber_traces[
    OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_renumber_trace_count;
open_cfw_mram_renumber_uintptr open_cfw_test_mram_renumber_updates[
    OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_renumber_update_count;
unsigned int open_cfw_test_mram_renumber_update_result;

static void open_cfw_test_mram_renumber_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_renumber_order_count
        < OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_renumber_order[
            open_cfw_test_mram_renumber_order_count
        ] = event;
    }
    ++open_cfw_test_mram_renumber_order_count;
}

void open_cfw_test_mram_renumber_reset(void)
{
    memset(
        open_cfw_test_mram_renumber_records,
        0,
        sizeof(open_cfw_test_mram_renumber_records)
    );
    memset(
        open_cfw_test_mram_renumber_order,
        0,
        sizeof(open_cfw_test_mram_renumber_order)
    );
    memset(
        open_cfw_test_mram_renumber_levels,
        0,
        sizeof(open_cfw_test_mram_renumber_levels)
    );
    memset(
        open_cfw_test_mram_renumber_logs,
        0,
        sizeof(open_cfw_test_mram_renumber_logs)
    );
    memset(
        open_cfw_test_mram_renumber_traces,
        0,
        sizeof(open_cfw_test_mram_renumber_traces)
    );
    memset(
        open_cfw_test_mram_renumber_updates,
        0,
        sizeof(open_cfw_test_mram_renumber_updates)
    );
    open_cfw_test_mram_renumber_counter = 0U;
    open_cfw_test_mram_renumber_order_count = 0U;
    open_cfw_test_mram_renumber_level_count = 0U;
    open_cfw_test_mram_renumber_level_index = 0U;
    open_cfw_test_mram_renumber_level_default = 0U;
    open_cfw_test_mram_renumber_log_count = 0U;
    open_cfw_test_mram_renumber_trace_count = 0U;
    open_cfw_test_mram_renumber_update_count = 0U;
    open_cfw_test_mram_renumber_update_result = 0U;
}

unsigned int open_cfw_test_mram_renumber_log_level(void)
{
    unsigned int index = open_cfw_test_mram_renumber_level_index++;
    unsigned int result = open_cfw_test_mram_renumber_level_default;

    open_cfw_test_mram_renumber_order_append(1U);
    if (index < open_cfw_test_mram_renumber_level_count) {
        result = open_cfw_test_mram_renumber_levels[index];
    }
    return result;
}

void open_cfw_test_mram_renumber_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_renumber_log_count;
    unsigned int count = line == 0x835U ? 2U : 0U;
    va_list arguments;

    open_cfw_test_mram_renumber_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT) {
        open_cfw_mram_renumber_uintptr *output =
            open_cfw_test_mram_renumber_logs
            + call * OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = severity;
        output[1] = (open_cfw_mram_renumber_uintptr)module;
        output[2] = (open_cfw_mram_renumber_uintptr)file;
        output[3] = (open_cfw_mram_renumber_uintptr)function;
        output[4] = line;
        output[5] = (open_cfw_mram_renumber_uintptr)identity;
        output[6] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[7U + index] = va_arg(
                arguments,
                open_cfw_mram_renumber_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_renumber_log_count;
}

void open_cfw_test_mram_renumber_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_renumber_trace_count;
    unsigned int count = event == 0x10800000U ? 2U : 0U;
    va_list arguments;

    open_cfw_test_mram_renumber_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT) {
        open_cfw_mram_renumber_uintptr *output =
            open_cfw_test_mram_renumber_traces
            + call * OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_WIDTH;
        unsigned int index;

        output[0] = event;
        output[1] = (open_cfw_mram_renumber_uintptr)schema;
        output[2] = (open_cfw_mram_renumber_uintptr)identity;
        output[3] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[4U + index] = va_arg(
                arguments,
                open_cfw_mram_renumber_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_renumber_trace_count;
}

unsigned int open_cfw_test_mram_renumber_update(
    const unsigned char *record
)
{
    unsigned int call = open_cfw_test_mram_renumber_update_count;

    open_cfw_test_mram_renumber_order_append(4U);
    if (call < OPEN_CFW_TEST_MRAM_RENUMBER_CAPTURE_COUNT) {
        open_cfw_test_mram_renumber_updates[call] =
            (open_cfw_mram_renumber_uintptr)record;
    }
    ++open_cfw_test_mram_renumber_update_count;
    return open_cfw_test_mram_renumber_update_result;
}
