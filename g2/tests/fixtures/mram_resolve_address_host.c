/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for Cordio application-database address resolution.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT 32U
#define OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_WIDTH 12U

unsigned int open_cfw_test_mram_resolve_map_owner(unsigned int);
unsigned int open_cfw_test_mram_resolve_compare(
    const unsigned char *,
    const unsigned char *
);
void open_cfw_test_mram_resolve_queue(
    const unsigned char *,
    const unsigned char *,
    unsigned int
);
unsigned int open_cfw_test_mram_resolve_log_level(void);
void open_cfw_test_mram_resolve_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_resolve_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_resolve_records[2000];

#define OPEN_CFW_MRAM_RESOLVE_RECORDS \
    open_cfw_test_mram_resolve_records
#define OPEN_CFW_MRAM_RESOLVE_MAP_OWNER(owner) \
    open_cfw_test_mram_resolve_map_owner(owner)
#define OPEN_CFW_MRAM_RESOLVE_COMPARE(record, address) \
    open_cfw_test_mram_resolve_compare((record), (address))
#define OPEN_CFW_MRAM_RESOLVE_QUEUE(address, irk, index) \
    open_cfw_test_mram_resolve_queue((address), (irk), (index))
#define OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() \
    open_cfw_test_mram_resolve_log_level()
#define OPEN_CFW_MRAM_RESOLVE_LOG(...) \
    open_cfw_test_mram_resolve_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_RESOLVE_TRACE(...) \
    open_cfw_test_mram_resolve_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_resolve_address.c"

unsigned int open_cfw_test_mram_resolve_order[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolve_order_count;
unsigned int open_cfw_test_mram_resolve_map_argument;
unsigned int open_cfw_test_mram_resolve_map_result;
const unsigned char *open_cfw_test_mram_resolve_compare_record;
const unsigned char *open_cfw_test_mram_resolve_compare_address;
unsigned int open_cfw_test_mram_resolve_compare_count;
int open_cfw_test_mram_resolve_compare_match_index;
const unsigned char *open_cfw_test_mram_resolve_queue_address;
const unsigned char *open_cfw_test_mram_resolve_queue_irk;
unsigned int open_cfw_test_mram_resolve_queue_index;
unsigned int open_cfw_test_mram_resolve_queue_count;
unsigned int open_cfw_test_mram_resolve_levels[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolve_level_count;
unsigned int open_cfw_test_mram_resolve_level_index;
open_cfw_mram_resolve_uintptr open_cfw_test_mram_resolve_logs[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_resolve_log_widths[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolve_log_count;
open_cfw_mram_resolve_uintptr open_cfw_test_mram_resolve_traces[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_resolve_trace_widths[
    OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_resolve_trace_count;

static void open_cfw_test_mram_resolve_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_resolve_order_count
        < OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_resolve_order[
            open_cfw_test_mram_resolve_order_count
        ] = event;
    }
    ++open_cfw_test_mram_resolve_order_count;
}

void open_cfw_test_mram_resolve_reset(void)
{
    memset(
        open_cfw_test_mram_resolve_records,
        0,
        sizeof(open_cfw_test_mram_resolve_records)
    );
    memset(
        open_cfw_test_mram_resolve_order,
        0,
        sizeof(open_cfw_test_mram_resolve_order)
    );
    memset(
        open_cfw_test_mram_resolve_levels,
        0,
        sizeof(open_cfw_test_mram_resolve_levels)
    );
    memset(
        open_cfw_test_mram_resolve_logs,
        0,
        sizeof(open_cfw_test_mram_resolve_logs)
    );
    memset(
        open_cfw_test_mram_resolve_log_widths,
        0,
        sizeof(open_cfw_test_mram_resolve_log_widths)
    );
    memset(
        open_cfw_test_mram_resolve_traces,
        0,
        sizeof(open_cfw_test_mram_resolve_traces)
    );
    memset(
        open_cfw_test_mram_resolve_trace_widths,
        0,
        sizeof(open_cfw_test_mram_resolve_trace_widths)
    );
    open_cfw_test_mram_resolve_order_count = 0U;
    open_cfw_test_mram_resolve_map_argument = 0U;
    open_cfw_test_mram_resolve_map_result = 0U;
    open_cfw_test_mram_resolve_compare_record =
        (const unsigned char *)0;
    open_cfw_test_mram_resolve_compare_address =
        (const unsigned char *)0;
    open_cfw_test_mram_resolve_compare_count = 0U;
    open_cfw_test_mram_resolve_compare_match_index = -1;
    open_cfw_test_mram_resolve_queue_address =
        (const unsigned char *)0;
    open_cfw_test_mram_resolve_queue_irk =
        (const unsigned char *)0;
    open_cfw_test_mram_resolve_queue_index = 0U;
    open_cfw_test_mram_resolve_queue_count = 0U;
    open_cfw_test_mram_resolve_level_count = 0U;
    open_cfw_test_mram_resolve_level_index = 0U;
    open_cfw_test_mram_resolve_log_count = 0U;
    open_cfw_test_mram_resolve_trace_count = 0U;
}

unsigned int open_cfw_test_mram_resolve_map_owner(unsigned int owner)
{
    open_cfw_test_mram_resolve_order_append(4U);
    open_cfw_test_mram_resolve_map_argument = owner;
    return open_cfw_test_mram_resolve_map_result;
}

unsigned int open_cfw_test_mram_resolve_compare(
    const unsigned char *record,
    const unsigned char *address
)
{
    unsigned int index =
        (unsigned int)(
            (record - open_cfw_test_mram_resolve_records) / 200
        );

    open_cfw_test_mram_resolve_order_append(5U);
    open_cfw_test_mram_resolve_compare_record = record;
    open_cfw_test_mram_resolve_compare_address = address;
    ++open_cfw_test_mram_resolve_compare_count;
    return index == (unsigned int)
        open_cfw_test_mram_resolve_compare_match_index;
}

void open_cfw_test_mram_resolve_queue(
    const unsigned char *address,
    const unsigned char *irk,
    unsigned int index
)
{
    open_cfw_test_mram_resolve_order_append(6U);
    open_cfw_test_mram_resolve_queue_address = address;
    open_cfw_test_mram_resolve_queue_irk = irk;
    open_cfw_test_mram_resolve_queue_index = index;
    ++open_cfw_test_mram_resolve_queue_count;
}

unsigned int open_cfw_test_mram_resolve_log_level(void)
{
    unsigned int index =
        open_cfw_test_mram_resolve_level_index++;

    open_cfw_test_mram_resolve_order_append(1U);
    if (index < open_cfw_test_mram_resolve_level_count) {
        return open_cfw_test_mram_resolve_levels[index];
    }
    return 0U;
}

void open_cfw_test_mram_resolve_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    unsigned int count = open_cfw_test_mram_resolve_log_count;
    open_cfw_mram_resolve_uintptr *capture =
        &open_cfw_test_mram_resolve_logs[
            count * OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_WIDTH
        ];
    unsigned int extra = 0U;
    va_list arguments;

    open_cfw_test_mram_resolve_order_append(2U);
    capture[0] = severity;
    capture[1] = (open_cfw_mram_resolve_uintptr)module;
    capture[2] = (open_cfw_mram_resolve_uintptr)file;
    capture[3] = (open_cfw_mram_resolve_uintptr)function;
    capture[4] = line;
    capture[5] = (open_cfw_mram_resolve_uintptr)message;
    if (line == 0x3EEU) {
        extra = 6U;
    }
    else if (line == 0x3F8U) {
        extra = 1U;
    }
    va_start(arguments, message);
    for (unsigned int index = 0U; index < extra; ++index) {
        capture[6U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_mram_resolve_log_widths[count] = 6U + extra;
    ++open_cfw_test_mram_resolve_log_count;
}

void open_cfw_test_mram_resolve_trace(
    unsigned int event,
    const void *identity_a,
    const void *identity_b,
    ...
)
{
    unsigned int count = open_cfw_test_mram_resolve_trace_count;
    open_cfw_mram_resolve_uintptr *capture =
        &open_cfw_test_mram_resolve_traces[
            count * OPEN_CFW_TEST_MRAM_RESOLVE_CAPTURE_WIDTH
        ];
    unsigned int extra = 0U;
    va_list arguments;

    open_cfw_test_mram_resolve_order_append(3U);
    capture[0] = event;
    capture[1] = (open_cfw_mram_resolve_uintptr)identity_a;
    capture[2] = (open_cfw_mram_resolve_uintptr)identity_b;
    if (event == 0x11800000U) {
        extra = 6U;
    }
    else if (event == 0x10400000U) {
        extra = 1U;
    }
    va_start(arguments, identity_b);
    for (unsigned int index = 0U; index < extra; ++index) {
        capture[3U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    open_cfw_test_mram_resolve_trace_widths[count] = 3U + extra;
    ++open_cfw_test_mram_resolve_trace_count;
}
