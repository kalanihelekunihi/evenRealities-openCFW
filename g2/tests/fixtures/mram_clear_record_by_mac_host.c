/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Cordio record-clearing wrapper.
 */

#include <string.h>

#define OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT 64U

unsigned char *open_cfw_test_mram_clear_find(
    unsigned int,
    const unsigned char *
);
unsigned int open_cfw_test_mram_clear_deactivate(unsigned char *);
void open_cfw_test_mram_clear_release(
    unsigned int,
    unsigned char *,
    unsigned int
);
unsigned int open_cfw_test_mram_clear_log_level(void);
void open_cfw_test_mram_clear_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_clear_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_CLEAR_FIND(owner, address) \
    open_cfw_test_mram_clear_find((owner), (address))
#define OPEN_CFW_MRAM_CLEAR_DEACTIVATE(record) \
    open_cfw_test_mram_clear_deactivate(record)
#define OPEN_CFW_MRAM_CLEAR_RELEASE(owner, record, flags) \
    open_cfw_test_mram_clear_release((owner), (record), (flags))
#define OPEN_CFW_MRAM_CLEAR_LOG_LEVEL() \
    open_cfw_test_mram_clear_log_level()
#define OPEN_CFW_MRAM_CLEAR_LOG(...) \
    open_cfw_test_mram_clear_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_CLEAR_TRACE(...) \
    open_cfw_test_mram_clear_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_clear_record_by_mac.c"

unsigned int open_cfw_test_mram_clear_order[
    OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_clear_order_count;
unsigned int open_cfw_test_mram_clear_levels[
    OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_clear_level_count;
unsigned int open_cfw_test_mram_clear_level_index;
unsigned int open_cfw_test_mram_clear_level_default;
open_cfw_mram_clear_uintptr open_cfw_test_mram_clear_logs[
    OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT * 6U
];
unsigned int open_cfw_test_mram_clear_log_count;
open_cfw_mram_clear_uintptr open_cfw_test_mram_clear_traces[
    OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT * 3U
];
unsigned int open_cfw_test_mram_clear_trace_count;
unsigned char *open_cfw_test_mram_clear_find_result;
unsigned int open_cfw_test_mram_clear_find_count;
unsigned int open_cfw_test_mram_clear_find_owner;
open_cfw_mram_clear_uintptr open_cfw_test_mram_clear_find_address;
unsigned int open_cfw_test_mram_clear_deactivate_count;
open_cfw_mram_clear_uintptr open_cfw_test_mram_clear_deactivate_record;
unsigned int open_cfw_test_mram_clear_deactivate_result;
unsigned int open_cfw_test_mram_clear_release_count;
unsigned int open_cfw_test_mram_clear_release_owner;
open_cfw_mram_clear_uintptr open_cfw_test_mram_clear_release_record;
unsigned int open_cfw_test_mram_clear_release_flags;

static void open_cfw_test_mram_clear_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_clear_order_count
        < OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_clear_order[
            open_cfw_test_mram_clear_order_count
        ] = event;
    }
    ++open_cfw_test_mram_clear_order_count;
}

void open_cfw_test_mram_clear_reset(void)
{
    memset(
        open_cfw_test_mram_clear_order,
        0,
        sizeof(open_cfw_test_mram_clear_order)
    );
    memset(
        open_cfw_test_mram_clear_levels,
        0,
        sizeof(open_cfw_test_mram_clear_levels)
    );
    memset(
        open_cfw_test_mram_clear_logs,
        0,
        sizeof(open_cfw_test_mram_clear_logs)
    );
    memset(
        open_cfw_test_mram_clear_traces,
        0,
        sizeof(open_cfw_test_mram_clear_traces)
    );
    open_cfw_test_mram_clear_order_count = 0U;
    open_cfw_test_mram_clear_level_count = 0U;
    open_cfw_test_mram_clear_level_index = 0U;
    open_cfw_test_mram_clear_level_default = 0U;
    open_cfw_test_mram_clear_log_count = 0U;
    open_cfw_test_mram_clear_trace_count = 0U;
    open_cfw_test_mram_clear_find_result = (unsigned char *)0;
    open_cfw_test_mram_clear_find_count = 0U;
    open_cfw_test_mram_clear_find_owner = 0U;
    open_cfw_test_mram_clear_find_address = 0U;
    open_cfw_test_mram_clear_deactivate_count = 0U;
    open_cfw_test_mram_clear_deactivate_record = 0U;
    open_cfw_test_mram_clear_deactivate_result = 0U;
    open_cfw_test_mram_clear_release_count = 0U;
    open_cfw_test_mram_clear_release_owner = 0U;
    open_cfw_test_mram_clear_release_record = 0U;
    open_cfw_test_mram_clear_release_flags = 0U;
}

unsigned int open_cfw_test_mram_clear_log_level(void)
{
    unsigned int index = open_cfw_test_mram_clear_level_index++;
    unsigned int result = open_cfw_test_mram_clear_level_default;

    open_cfw_test_mram_clear_order_append(1U);
    if (index < open_cfw_test_mram_clear_level_count) {
        result = open_cfw_test_mram_clear_levels[index];
    }
    return result;
}

void open_cfw_test_mram_clear_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_clear_log_count;

    open_cfw_test_mram_clear_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT) {
        open_cfw_mram_clear_uintptr *record =
            open_cfw_test_mram_clear_logs + call * 6U;

        record[0] = severity;
        record[1] = (open_cfw_mram_clear_uintptr)module;
        record[2] = (open_cfw_mram_clear_uintptr)file;
        record[3] = (open_cfw_mram_clear_uintptr)function;
        record[4] = line;
        record[5] = (open_cfw_mram_clear_uintptr)identity;
    }
    ++open_cfw_test_mram_clear_log_count;
}

void open_cfw_test_mram_clear_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_clear_trace_count;

    open_cfw_test_mram_clear_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_CLEAR_CAPTURE_COUNT) {
        open_cfw_mram_clear_uintptr *record =
            open_cfw_test_mram_clear_traces + call * 3U;

        record[0] = event;
        record[1] = (open_cfw_mram_clear_uintptr)schema;
        record[2] = (open_cfw_mram_clear_uintptr)identity;
    }
    ++open_cfw_test_mram_clear_trace_count;
}

unsigned char *open_cfw_test_mram_clear_find(
    unsigned int owner,
    const unsigned char *address
)
{
    open_cfw_test_mram_clear_order_append(4U);
    ++open_cfw_test_mram_clear_find_count;
    open_cfw_test_mram_clear_find_owner = owner;
    open_cfw_test_mram_clear_find_address =
        (open_cfw_mram_clear_uintptr)address;
    return open_cfw_test_mram_clear_find_result;
}

unsigned int open_cfw_test_mram_clear_deactivate(unsigned char *record)
{
    open_cfw_test_mram_clear_order_append(5U);
    ++open_cfw_test_mram_clear_deactivate_count;
    open_cfw_test_mram_clear_deactivate_record =
        (open_cfw_mram_clear_uintptr)record;
    return open_cfw_test_mram_clear_deactivate_result;
}

void open_cfw_test_mram_clear_release(
    unsigned int owner,
    unsigned char *record,
    unsigned int flags
)
{
    open_cfw_test_mram_clear_order_append(6U);
    ++open_cfw_test_mram_clear_release_count;
    open_cfw_test_mram_clear_release_owner = owner;
    open_cfw_test_mram_clear_release_record =
        (open_cfw_mram_clear_uintptr)record;
    open_cfw_test_mram_clear_release_flags = flags;
}
