/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for Cordio AppDbShowAllRecordsStatus.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_STATUS_RECORD_COUNT 10U
#define OPEN_CFW_TEST_MRAM_STATUS_RECORD_STRIDE 0x100U
#define OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT 128U
#define OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_WIDTH 14U

unsigned int open_cfw_test_mram_status_cache(
    const void *,
    unsigned int
);
unsigned int open_cfw_test_mram_status_log_level(void);
void open_cfw_test_mram_status_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_status_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_status_nvm[
    OPEN_CFW_TEST_MRAM_STATUS_RECORD_COUNT
    * OPEN_CFW_TEST_MRAM_STATUS_RECORD_STRIDE
];
unsigned int open_cfw_test_mram_status_timestamp_counter;

#define OPEN_CFW_MRAM_STATUS_NVM_BASE \
    open_cfw_test_mram_status_nvm
#define OPEN_CFW_MRAM_STATUS_TIMESTAMP_COUNTER \
    open_cfw_test_mram_status_timestamp_counter
#define OPEN_CFW_MRAM_STATUS_CACHE_INVALIDATE(range, clean) \
    open_cfw_test_mram_status_cache((range), (clean))
#define OPEN_CFW_MRAM_STATUS_LOG_LEVEL() \
    open_cfw_test_mram_status_log_level()
#define OPEN_CFW_MRAM_STATUS_LOG(...) \
    open_cfw_test_mram_status_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_STATUS_TRACE(...) \
    open_cfw_test_mram_status_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_show_records_status.c"

unsigned int open_cfw_test_mram_status_order[
    OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_status_order_count;
unsigned int open_cfw_test_mram_status_levels[
    OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_status_level_count;
unsigned int open_cfw_test_mram_status_level_index;
unsigned int open_cfw_test_mram_status_level_default;
open_cfw_mram_status_uintptr open_cfw_test_mram_status_logs[
    OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_status_log_count;
open_cfw_mram_status_uintptr open_cfw_test_mram_status_traces[
    OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_status_trace_count;
unsigned int open_cfw_test_mram_status_cache_count;
open_cfw_mram_status_uintptr open_cfw_test_mram_status_cache_range;
unsigned int open_cfw_test_mram_status_cache_clean;

static void open_cfw_test_mram_status_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_status_order_count
        < OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_status_order[
            open_cfw_test_mram_status_order_count
        ] = event;
    }
    ++open_cfw_test_mram_status_order_count;
}

void open_cfw_test_mram_status_reset(void)
{
    memset(
        open_cfw_test_mram_status_nvm,
        0,
        sizeof(open_cfw_test_mram_status_nvm)
    );
    memset(
        open_cfw_test_mram_status_order,
        0,
        sizeof(open_cfw_test_mram_status_order)
    );
    memset(
        open_cfw_test_mram_status_levels,
        0,
        sizeof(open_cfw_test_mram_status_levels)
    );
    memset(
        open_cfw_test_mram_status_logs,
        0,
        sizeof(open_cfw_test_mram_status_logs)
    );
    memset(
        open_cfw_test_mram_status_traces,
        0,
        sizeof(open_cfw_test_mram_status_traces)
    );
    open_cfw_test_mram_status_timestamp_counter = 0U;
    open_cfw_test_mram_status_order_count = 0U;
    open_cfw_test_mram_status_level_count = 0U;
    open_cfw_test_mram_status_level_index = 0U;
    open_cfw_test_mram_status_level_default = 0U;
    open_cfw_test_mram_status_log_count = 0U;
    open_cfw_test_mram_status_trace_count = 0U;
    open_cfw_test_mram_status_cache_count = 0U;
    open_cfw_test_mram_status_cache_range = 0U;
    open_cfw_test_mram_status_cache_clean = 0U;
}

unsigned int open_cfw_test_mram_status_log_level(void)
{
    unsigned int index = open_cfw_test_mram_status_level_index++;
    unsigned int result = open_cfw_test_mram_status_level_default;

    open_cfw_test_mram_status_order_append(1U);
    if (index < open_cfw_test_mram_status_level_count) {
        result = open_cfw_test_mram_status_levels[index];
    }
    return result;
}

static unsigned int open_cfw_test_mram_status_log_arguments(
    unsigned int line
)
{
    if (line == 0x7D4U || line == 0x7D5U) {
        return 1U;
    }
    if (
        line == 0x7F7U
        || line == 0x7F4U
        || line == 0x7FBU
        || line == 0x7FDU
        || line == 0x7FEU
    ) {
        return 2U;
    }
    if (line == 0x7E4U) {
        return 3U;
    }
    if (line == 0x7E7U) {
        return 7U;
    }
    return 0U;
}

void open_cfw_test_mram_status_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_status_log_count;
    unsigned int count = open_cfw_test_mram_status_log_arguments(line);
    va_list arguments;
    unsigned int index;

    open_cfw_test_mram_status_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT) {
        open_cfw_mram_status_uintptr *output =
            open_cfw_test_mram_status_logs
            + call * OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_WIDTH;

        output[0] = severity;
        output[1] = (open_cfw_mram_status_uintptr)module;
        output[2] = (open_cfw_mram_status_uintptr)file;
        output[3] = (open_cfw_mram_status_uintptr)function;
        output[4] = line;
        output[5] = (open_cfw_mram_status_uintptr)identity;
        output[6] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[7U + index] = va_arg(
                arguments,
                open_cfw_mram_status_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_status_log_count;
}

static unsigned int open_cfw_test_mram_status_trace_arguments(
    unsigned int event
)
{
    if (event == 0x10400000U) {
        return 1U;
    }
    if (event == 0x10800000U) {
        return 2U;
    }
    if (event == 0x10C00000U) {
        return 3U;
    }
    if (event == 0x11C00000U) {
        return 7U;
    }
    return 0U;
}

void open_cfw_test_mram_status_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_status_trace_count;
    unsigned int count =
        open_cfw_test_mram_status_trace_arguments(event);
    va_list arguments;
    unsigned int index;

    open_cfw_test_mram_status_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_COUNT) {
        open_cfw_mram_status_uintptr *output =
            open_cfw_test_mram_status_traces
            + call * OPEN_CFW_TEST_MRAM_STATUS_CAPTURE_WIDTH;

        output[0] = event;
        output[1] = (open_cfw_mram_status_uintptr)schema;
        output[2] = (open_cfw_mram_status_uintptr)identity;
        output[3] = count;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            output[4U + index] = va_arg(
                arguments,
                open_cfw_mram_status_uintptr
            );
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_status_trace_count;
}

unsigned int open_cfw_test_mram_status_cache(
    const void *range,
    unsigned int clean
)
{
    open_cfw_test_mram_status_order_append(4U);
    open_cfw_test_mram_status_cache_range =
        (open_cfw_mram_status_uintptr)range;
    open_cfw_test_mram_status_cache_clean = clean;
    ++open_cfw_test_mram_status_cache_count;
    return 0U;
}
