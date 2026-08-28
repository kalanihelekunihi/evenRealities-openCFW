/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Cordio resolving-list reload wrapper.
 */

#include <string.h>

#define OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT 32U

unsigned int open_cfw_test_mram_reload_log_level(void);
void open_cfw_test_mram_reload_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_reload_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_reload_request(void);
void open_cfw_test_mram_reload_sync(void);

#define OPEN_CFW_MRAM_RELOAD_LOG_LEVEL() \
    open_cfw_test_mram_reload_log_level()
#define OPEN_CFW_MRAM_RELOAD_LOG(...) \
    open_cfw_test_mram_reload_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_RELOAD_TRACE(...) \
    open_cfw_test_mram_reload_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_RELOAD_REQUEST() \
    open_cfw_test_mram_reload_request()
#define OPEN_CFW_MRAM_RELOAD_SYNC() \
    open_cfw_test_mram_reload_sync()

#include "../../components/apollo_main/core_overlay/mram_reload_resolving_list.c"

unsigned int open_cfw_test_mram_reload_order[
    OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_reload_order_count;
unsigned int open_cfw_test_mram_reload_levels[
    OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_reload_level_count;
unsigned int open_cfw_test_mram_reload_level_index;
unsigned int open_cfw_test_mram_reload_level_default;
open_cfw_mram_reload_uintptr open_cfw_test_mram_reload_logs[
    OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT * 6U
];
unsigned int open_cfw_test_mram_reload_log_count;
open_cfw_mram_reload_uintptr open_cfw_test_mram_reload_traces[
    OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT * 3U
];
unsigned int open_cfw_test_mram_reload_trace_count;
unsigned int open_cfw_test_mram_reload_request_count;
unsigned int open_cfw_test_mram_reload_sync_count;

static void open_cfw_test_mram_reload_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_reload_order_count
        < OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_reload_order[
            open_cfw_test_mram_reload_order_count
        ] = event;
    }
    ++open_cfw_test_mram_reload_order_count;
}

void open_cfw_test_mram_reload_reset(void)
{
    memset(
        open_cfw_test_mram_reload_order,
        0,
        sizeof(open_cfw_test_mram_reload_order)
    );
    memset(
        open_cfw_test_mram_reload_levels,
        0,
        sizeof(open_cfw_test_mram_reload_levels)
    );
    memset(
        open_cfw_test_mram_reload_logs,
        0,
        sizeof(open_cfw_test_mram_reload_logs)
    );
    memset(
        open_cfw_test_mram_reload_traces,
        0,
        sizeof(open_cfw_test_mram_reload_traces)
    );
    open_cfw_test_mram_reload_order_count = 0U;
    open_cfw_test_mram_reload_level_count = 0U;
    open_cfw_test_mram_reload_level_index = 0U;
    open_cfw_test_mram_reload_level_default = 0U;
    open_cfw_test_mram_reload_log_count = 0U;
    open_cfw_test_mram_reload_trace_count = 0U;
    open_cfw_test_mram_reload_request_count = 0U;
    open_cfw_test_mram_reload_sync_count = 0U;
}

unsigned int open_cfw_test_mram_reload_log_level(void)
{
    unsigned int index = open_cfw_test_mram_reload_level_index++;
    unsigned int result = open_cfw_test_mram_reload_level_default;

    open_cfw_test_mram_reload_order_append(1U);
    if (index < open_cfw_test_mram_reload_level_count) {
        result = open_cfw_test_mram_reload_levels[index];
    }
    return result;
}

void open_cfw_test_mram_reload_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_reload_log_count;

    open_cfw_test_mram_reload_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT) {
        open_cfw_mram_reload_uintptr *record =
            open_cfw_test_mram_reload_logs + call * 6U;

        record[0] = severity;
        record[1] = (open_cfw_mram_reload_uintptr)module;
        record[2] = (open_cfw_mram_reload_uintptr)file;
        record[3] = (open_cfw_mram_reload_uintptr)function;
        record[4] = line;
        record[5] = (open_cfw_mram_reload_uintptr)identity;
    }
    ++open_cfw_test_mram_reload_log_count;
}

void open_cfw_test_mram_reload_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_reload_trace_count;

    open_cfw_test_mram_reload_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_RELOAD_CAPTURE_COUNT) {
        open_cfw_mram_reload_uintptr *record =
            open_cfw_test_mram_reload_traces + call * 3U;

        record[0] = event;
        record[1] = (open_cfw_mram_reload_uintptr)schema;
        record[2] = (open_cfw_mram_reload_uintptr)identity;
    }
    ++open_cfw_test_mram_reload_trace_count;
}

void open_cfw_test_mram_reload_request(void)
{
    open_cfw_test_mram_reload_order_append(4U);
    ++open_cfw_test_mram_reload_request_count;
}

void open_cfw_test_mram_reload_sync(void)
{
    open_cfw_test_mram_reload_order_append(5U);
    ++open_cfw_test_mram_reload_sync_count;
}
