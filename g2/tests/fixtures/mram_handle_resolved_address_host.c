/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for Cordio AppDbHandleResolvedAddr.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT 24U
#define OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_WIDTH 13U

unsigned int open_cfw_test_mram_resolved_log_level(void);
void open_cfw_test_mram_resolved_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_resolved_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_resolved_records[2000];

#define OPEN_CFW_MRAM_RESOLVED_RECORDS \
    open_cfw_test_mram_resolved_records
#define OPEN_CFW_MRAM_RESOLVED_LOG_LEVEL() \
    open_cfw_test_mram_resolved_log_level()
#define OPEN_CFW_MRAM_RESOLVED_LOG(...) \
    open_cfw_test_mram_resolved_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_RESOLVED_TRACE(...) \
    open_cfw_test_mram_resolved_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_handle_resolved_address.c"

unsigned int open_cfw_test_mram_resolved_order[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolved_order_count;
unsigned int open_cfw_test_mram_resolved_levels[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolved_level_count;
unsigned int open_cfw_test_mram_resolved_level_index;
open_cfw_mram_resolved_uintptr open_cfw_test_mram_resolved_logs[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_resolved_log_widths[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolved_log_count;
open_cfw_mram_resolved_uintptr open_cfw_test_mram_resolved_traces[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_resolved_trace_widths[
    OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolved_trace_count;

static void open_cfw_test_mram_resolved_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_resolved_order_count
        < OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_resolved_order[
            open_cfw_test_mram_resolved_order_count
        ] = event;
    }
    ++open_cfw_test_mram_resolved_order_count;
}

void open_cfw_test_mram_resolved_reset(void)
{
    memset(
        open_cfw_test_mram_resolved_records,
        0,
        sizeof(open_cfw_test_mram_resolved_records)
    );
    memset(
        open_cfw_test_mram_resolved_order,
        0,
        sizeof(open_cfw_test_mram_resolved_order)
    );
    memset(
        open_cfw_test_mram_resolved_levels,
        0,
        sizeof(open_cfw_test_mram_resolved_levels)
    );
    memset(
        open_cfw_test_mram_resolved_logs,
        0,
        sizeof(open_cfw_test_mram_resolved_logs)
    );
    memset(
        open_cfw_test_mram_resolved_log_widths,
        0,
        sizeof(open_cfw_test_mram_resolved_log_widths)
    );
    memset(
        open_cfw_test_mram_resolved_traces,
        0,
        sizeof(open_cfw_test_mram_resolved_traces)
    );
    memset(
        open_cfw_test_mram_resolved_trace_widths,
        0,
        sizeof(open_cfw_test_mram_resolved_trace_widths)
    );
    open_cfw_test_mram_resolved_order_count = 0U;
    open_cfw_test_mram_resolved_level_count = 0U;
    open_cfw_test_mram_resolved_level_index = 0U;
    open_cfw_test_mram_resolved_log_count = 0U;
    open_cfw_test_mram_resolved_trace_count = 0U;
}

unsigned int open_cfw_test_mram_resolved_log_level(void)
{
    unsigned int index =
        open_cfw_test_mram_resolved_level_index++;

    open_cfw_test_mram_resolved_order_append(1U);
    if (index < open_cfw_test_mram_resolved_level_count) {
        return open_cfw_test_mram_resolved_levels[index];
    }
    return 0U;
}

void open_cfw_test_mram_resolved_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    unsigned int count = open_cfw_test_mram_resolved_log_count;
    open_cfw_mram_resolved_uintptr *capture =
        &open_cfw_test_mram_resolved_logs[
            count * OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_WIDTH
        ];
    unsigned int extra = line == 0x43BU ? 7U : 0U;
    va_list arguments;

    open_cfw_test_mram_resolved_order_append(2U);
    capture[0] = severity;
    capture[1] = (open_cfw_mram_resolved_uintptr)module;
    capture[2] = (open_cfw_mram_resolved_uintptr)file;
    capture[3] = (open_cfw_mram_resolved_uintptr)function;
    capture[4] = line;
    capture[5] = (open_cfw_mram_resolved_uintptr)message;
    va_start(arguments, message);
    for (unsigned int index = 0U; index < extra; ++index) {
        capture[6U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_mram_resolved_log_widths[count] = 6U + extra;
    ++open_cfw_test_mram_resolved_log_count;
}

void open_cfw_test_mram_resolved_trace(
    unsigned int event,
    const void *identity_a,
    const void *identity_b,
    ...
)
{
    unsigned int count = open_cfw_test_mram_resolved_trace_count;
    open_cfw_mram_resolved_uintptr *capture =
        &open_cfw_test_mram_resolved_traces[
            count * OPEN_CFW_TEST_MRAM_RESOLVED_CAPTURE_WIDTH
        ];
    unsigned int extra = event == 0x11C00000U ? 7U : 0U;
    va_list arguments;

    open_cfw_test_mram_resolved_order_append(3U);
    capture[0] = event;
    capture[1] = (open_cfw_mram_resolved_uintptr)identity_a;
    capture[2] = (open_cfw_mram_resolved_uintptr)identity_b;
    va_start(arguments, identity_b);
    for (unsigned int index = 0U; index < extra; ++index) {
        capture[3U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_mram_resolved_trace_widths[count] = 3U + extra;
    ++open_cfw_test_mram_resolved_trace_count;
}
