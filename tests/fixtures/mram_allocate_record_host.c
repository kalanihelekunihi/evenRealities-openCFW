/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record allocator.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT 32U
#define OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_WIDTH 12U

unsigned int open_cfw_test_mram_allocate_count_type(unsigned int);
unsigned char *open_cfw_test_mram_allocate_oldest_type(unsigned int);
unsigned int open_cfw_test_mram_allocate_deactivate(unsigned char *);
void open_cfw_test_mram_allocate_zero(unsigned char *, unsigned int);
void open_cfw_test_mram_allocate_release(
    unsigned int,
    unsigned char *,
    unsigned int
);
unsigned int open_cfw_test_mram_allocate_map_owner(unsigned int);
void open_cfw_test_mram_allocate_initialize(unsigned char *, const void *);
unsigned int open_cfw_test_mram_allocate_log_level(void);
void open_cfw_test_mram_allocate_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_allocate_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_allocate_records[2000];
unsigned int open_cfw_test_mram_allocate_counter;

#define OPEN_CFW_MRAM_ALLOCATE_RECORDS \
    open_cfw_test_mram_allocate_records
#define OPEN_CFW_MRAM_ALLOCATE_COUNTER \
    open_cfw_test_mram_allocate_counter
#define OPEN_CFW_MRAM_ALLOCATE_COUNT_TYPE(type) \
    open_cfw_test_mram_allocate_count_type(type)
#define OPEN_CFW_MRAM_ALLOCATE_OLDEST_TYPE(type) \
    open_cfw_test_mram_allocate_oldest_type(type)
#define OPEN_CFW_MRAM_ALLOCATE_DEACTIVATE(record) \
    open_cfw_test_mram_allocate_deactivate(record)
#define OPEN_CFW_MRAM_ALLOCATE_ZERO(record, size) \
    open_cfw_test_mram_allocate_zero((record), (size))
#define OPEN_CFW_MRAM_ALLOCATE_RELEASE(owner, record, flags) \
    open_cfw_test_mram_allocate_release((owner), (record), (flags))
#define OPEN_CFW_MRAM_ALLOCATE_MAP_OWNER(owner) \
    open_cfw_test_mram_allocate_map_owner(owner)
#define OPEN_CFW_MRAM_ALLOCATE_INITIALIZE(record, value) \
    open_cfw_test_mram_allocate_initialize((record), (value))
#define OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL() \
    open_cfw_test_mram_allocate_log_level()
#define OPEN_CFW_MRAM_ALLOCATE_LOG(...) \
    open_cfw_test_mram_allocate_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_ALLOCATE_TRACE(...) \
    open_cfw_test_mram_allocate_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_allocate_record.c"

unsigned int open_cfw_test_mram_allocate_order[
    OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_allocate_order_count;
unsigned int open_cfw_test_mram_allocate_count_result;
unsigned int open_cfw_test_mram_allocate_count_type_argument;
unsigned int open_cfw_test_mram_allocate_oldest_type_argument;
unsigned char *open_cfw_test_mram_allocate_oldest_result;
unsigned char *open_cfw_test_mram_allocate_release_record;
unsigned int open_cfw_test_mram_allocate_release_owner;
unsigned int open_cfw_test_mram_allocate_release_flags;
unsigned char *open_cfw_test_mram_allocate_deactivate_record;
unsigned int open_cfw_test_mram_allocate_deactivate_result;
unsigned char *open_cfw_test_mram_allocate_zero_record;
unsigned int open_cfw_test_mram_allocate_zero_size;
unsigned int open_cfw_test_mram_allocate_map_owner_argument;
unsigned int open_cfw_test_mram_allocate_map_owner_result;
unsigned char *open_cfw_test_mram_allocate_initialize_record;
const void *open_cfw_test_mram_allocate_initialize_value;
unsigned int open_cfw_test_mram_allocate_levels[
    OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_allocate_level_count;
unsigned int open_cfw_test_mram_allocate_level_index;
open_cfw_mram_allocate_uintptr open_cfw_test_mram_allocate_logs[
    OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_allocate_log_count;
open_cfw_mram_allocate_uintptr open_cfw_test_mram_allocate_traces[
    OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_allocate_trace_count;

static void open_cfw_test_mram_allocate_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_allocate_order_count
        < OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_allocate_order[
            open_cfw_test_mram_allocate_order_count
        ] = event;
    }
    ++open_cfw_test_mram_allocate_order_count;
}

void open_cfw_test_mram_allocate_reset(void)
{
    memset(
        open_cfw_test_mram_allocate_records,
        0,
        sizeof(open_cfw_test_mram_allocate_records)
    );
    memset(
        open_cfw_test_mram_allocate_order,
        0,
        sizeof(open_cfw_test_mram_allocate_order)
    );
    memset(
        open_cfw_test_mram_allocate_levels,
        0,
        sizeof(open_cfw_test_mram_allocate_levels)
    );
    memset(
        open_cfw_test_mram_allocate_logs,
        0,
        sizeof(open_cfw_test_mram_allocate_logs)
    );
    memset(
        open_cfw_test_mram_allocate_traces,
        0,
        sizeof(open_cfw_test_mram_allocate_traces)
    );
    open_cfw_test_mram_allocate_counter = 0U;
    open_cfw_test_mram_allocate_order_count = 0U;
    open_cfw_test_mram_allocate_count_result = 0U;
    open_cfw_test_mram_allocate_count_type_argument = 0U;
    open_cfw_test_mram_allocate_oldest_type_argument = 0U;
    open_cfw_test_mram_allocate_oldest_result = (unsigned char *)0;
    open_cfw_test_mram_allocate_release_record = (unsigned char *)0;
    open_cfw_test_mram_allocate_release_owner = 0U;
    open_cfw_test_mram_allocate_release_flags = 0U;
    open_cfw_test_mram_allocate_deactivate_record = (unsigned char *)0;
    open_cfw_test_mram_allocate_deactivate_result = 0U;
    open_cfw_test_mram_allocate_zero_record = (unsigned char *)0;
    open_cfw_test_mram_allocate_zero_size = 0U;
    open_cfw_test_mram_allocate_map_owner_argument = 0U;
    open_cfw_test_mram_allocate_map_owner_result = 0U;
    open_cfw_test_mram_allocate_initialize_record = (unsigned char *)0;
    open_cfw_test_mram_allocate_initialize_value = (const void *)0;
    open_cfw_test_mram_allocate_level_count = 0U;
    open_cfw_test_mram_allocate_level_index = 0U;
    open_cfw_test_mram_allocate_log_count = 0U;
    open_cfw_test_mram_allocate_trace_count = 0U;
}

unsigned int open_cfw_test_mram_allocate_count_type(unsigned int type)
{
    open_cfw_test_mram_allocate_order_append(1U);
    open_cfw_test_mram_allocate_count_type_argument = type;
    return open_cfw_test_mram_allocate_count_result;
}

unsigned char *open_cfw_test_mram_allocate_oldest_type(unsigned int type)
{
    open_cfw_test_mram_allocate_order_append(2U);
    open_cfw_test_mram_allocate_oldest_type_argument = type;
    return open_cfw_test_mram_allocate_oldest_result;
}

void open_cfw_test_mram_allocate_release(
    unsigned int owner,
    unsigned char *record,
    unsigned int flags
)
{
    open_cfw_test_mram_allocate_order_append(3U);
    open_cfw_test_mram_allocate_release_owner = owner;
    open_cfw_test_mram_allocate_release_record = record;
    open_cfw_test_mram_allocate_release_flags = flags;
}

unsigned int open_cfw_test_mram_allocate_deactivate(unsigned char *record)
{
    open_cfw_test_mram_allocate_order_append(4U);
    open_cfw_test_mram_allocate_deactivate_record = record;
    record[0x2FU] = 0U;
    record[0x30U] = 0U;
    return open_cfw_test_mram_allocate_deactivate_result;
}

void open_cfw_test_mram_allocate_zero(
    unsigned char *record,
    unsigned int size
)
{
    open_cfw_test_mram_allocate_order_append(5U);
    open_cfw_test_mram_allocate_zero_record = record;
    open_cfw_test_mram_allocate_zero_size = size;
    memset(record, 0, size);
}

unsigned int open_cfw_test_mram_allocate_map_owner(unsigned int owner)
{
    open_cfw_test_mram_allocate_order_append(6U);
    open_cfw_test_mram_allocate_map_owner_argument = owner;
    return open_cfw_test_mram_allocate_map_owner_result;
}

void open_cfw_test_mram_allocate_initialize(
    unsigned char *record,
    const void *value
)
{
    open_cfw_test_mram_allocate_order_append(7U);
    open_cfw_test_mram_allocate_initialize_record = record;
    open_cfw_test_mram_allocate_initialize_value = value;
    record[7U] = 0xA5U;
}

unsigned int open_cfw_test_mram_allocate_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_allocate_level_index
        < open_cfw_test_mram_allocate_level_count
    ) {
        result = open_cfw_test_mram_allocate_levels[
            open_cfw_test_mram_allocate_level_index
        ];
    }
    ++open_cfw_test_mram_allocate_level_index;
    return result;
}

void open_cfw_test_mram_allocate_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_allocate_uintptr *row;
    va_list arguments;

    if (
        open_cfw_test_mram_allocate_log_count
        >= OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_allocate_log_count;
        return;
    }
    row = &open_cfw_test_mram_allocate_logs[
        open_cfw_test_mram_allocate_log_count
        * OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_WIDTH
    ];
    row[0] = severity;
    row[1] = (open_cfw_mram_allocate_uintptr)module;
    row[2] = (open_cfw_mram_allocate_uintptr)file;
    row[3] = (open_cfw_mram_allocate_uintptr)function;
    row[4] = line;
    row[5] = (open_cfw_mram_allocate_uintptr)identity;
    va_start(arguments, identity);
    if (row[5] == 0x0071BFC8U) {
        row[6] = (open_cfw_mram_allocate_uintptr)
            va_arg(arguments, const void *);
        row[7] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_mram_allocate_log_count;
}

void open_cfw_test_mram_allocate_trace(
    unsigned int event,
    const void *identity_a,
    const void *identity_b,
    ...
)
{
    open_cfw_mram_allocate_uintptr *row;
    va_list arguments;

    if (
        open_cfw_test_mram_allocate_trace_count
        >= OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_allocate_trace_count;
        return;
    }
    row = &open_cfw_test_mram_allocate_traces[
        open_cfw_test_mram_allocate_trace_count
        * OPEN_CFW_TEST_MRAM_ALLOCATE_CAPTURE_WIDTH
    ];
    row[0] = event;
    row[1] = (open_cfw_mram_allocate_uintptr)identity_a;
    row[2] = (open_cfw_mram_allocate_uintptr)identity_b;
    va_start(arguments, identity_b);
    if (row[1] == 0x007002C0U) {
        row[3] = (open_cfw_mram_allocate_uintptr)
            va_arg(arguments, const void *);
    }
    va_end(arguments);
    ++open_cfw_test_mram_allocate_trace_count;
}
