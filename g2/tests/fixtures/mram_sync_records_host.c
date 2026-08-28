/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Apollo MRAM record synchronizer.
 */

#include <stdarg.h>

#define OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT 10U
#define OPEN_CFW_TEST_MRAM_SYNC_RECORD_SIZE 0xC8U
#define OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT 32U
#define OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH 10U

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);
unsigned int open_cfw_test_mram_sync_timestamp(void);
void open_cfw_test_mram_sync_publish(
    unsigned int,
    const void *,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int
);
void open_cfw_test_mram_sync_commit(unsigned int);
unsigned int open_cfw_test_mram_sync_log_level(void);
void open_cfw_test_mram_sync_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_sync_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_sync_records[
    OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT
    * OPEN_CFW_TEST_MRAM_SYNC_RECORD_SIZE
];
unsigned char open_cfw_test_mram_sync_alternate_records[
    OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT
    * OPEN_CFW_TEST_MRAM_SYNC_RECORD_SIZE
];
unsigned char open_cfw_test_mram_sync_key[16];
volatile unsigned char *open_cfw_test_mram_sync_record_base;

#define OPEN_CFW_MRAM_SYNC_HOST 1
#define OPEN_CFW_MRAM_SYNC_RECORD_BASE \
    open_cfw_test_mram_sync_record_base
#define OPEN_CFW_MRAM_SYNC_COMPARE_KEY open_cfw_test_mram_sync_key
#define OPEN_CFW_MRAM_SYNC_TIMESTAMP() \
    open_cfw_test_mram_sync_timestamp()
#define OPEN_CFW_MRAM_SYNC_PUBLISH(...) \
    open_cfw_test_mram_sync_publish(__VA_ARGS__)
#define OPEN_CFW_MRAM_SYNC_COMMIT(value) \
    open_cfw_test_mram_sync_commit(value)
#define OPEN_CFW_MRAM_SYNC_LOG_LEVEL() \
    open_cfw_test_mram_sync_log_level()
#define OPEN_CFW_MRAM_SYNC_LOG(...) \
    open_cfw_test_mram_sync_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_SYNC_TRACE(...) \
    open_cfw_test_mram_sync_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_sync_records.c"

int open_cfw_test_mram_sync_compare_results[
    OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT
];
open_cfw_mram_sync_uintptr open_cfw_test_mram_sync_compare_records[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
];
open_cfw_mram_sync_uintptr open_cfw_test_mram_sync_compare_keys[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_sync_compare_sizes[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_sync_compare_calls;
unsigned int open_cfw_test_mram_sync_timestamps[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_sync_timestamp_calls;
open_cfw_mram_sync_uintptr open_cfw_test_mram_sync_publish_records[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_sync_publish_calls;
unsigned int open_cfw_test_mram_sync_commit_calls;
unsigned int open_cfw_test_mram_sync_commit_value;
unsigned int open_cfw_test_mram_sync_levels[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_sync_level_count;
unsigned int open_cfw_test_mram_sync_level_index;
unsigned int open_cfw_test_mram_sync_switch_base_level_index;
open_cfw_mram_sync_uintptr open_cfw_test_mram_sync_log_records[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_sync_log_count;
open_cfw_mram_sync_uintptr open_cfw_test_mram_sync_trace_records[
    OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_sync_trace_count;

void open_cfw_test_mram_sync_reset(void)
{
    unsigned int index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_mram_sync_records);
        ++index
    ) {
        open_cfw_test_mram_sync_records[index] = 0U;
        open_cfw_test_mram_sync_alternate_records[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_mram_sync_key[index] = (unsigned char)index;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT;
        ++index
    ) {
        open_cfw_test_mram_sync_compare_results[index] = 1;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT;
        ++index
    ) {
        open_cfw_test_mram_sync_compare_records[index] = 0U;
        open_cfw_test_mram_sync_compare_keys[index] = 0U;
        open_cfw_test_mram_sync_compare_sizes[index] = 0U;
        open_cfw_test_mram_sync_timestamps[index] =
            0xA5000000U + index;
        open_cfw_test_mram_sync_levels[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT
                * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_sync_publish_records[index] = 0U;
        open_cfw_test_mram_sync_log_records[index] = 0U;
        open_cfw_test_mram_sync_trace_records[index] = 0U;
    }

    open_cfw_test_mram_sync_record_base =
        open_cfw_test_mram_sync_records;
    open_cfw_test_mram_sync_compare_calls = 0U;
    open_cfw_test_mram_sync_timestamp_calls = 0U;
    open_cfw_test_mram_sync_publish_calls = 0U;
    open_cfw_test_mram_sync_commit_calls = 0U;
    open_cfw_test_mram_sync_commit_value = 0U;
    open_cfw_test_mram_sync_level_count = 0U;
    open_cfw_test_mram_sync_level_index = 0U;
    open_cfw_test_mram_sync_switch_base_level_index = 0xFFFFFFFFU;
    open_cfw_test_mram_sync_log_count = 0U;
    open_cfw_test_mram_sync_trace_count = 0U;
}

static int open_cfw_test_mram_sync_record_index(const void *pointer)
{
    open_cfw_mram_sync_uintptr address =
        (open_cfw_mram_sync_uintptr)pointer;
    open_cfw_mram_sync_uintptr base =
        (open_cfw_mram_sync_uintptr)open_cfw_test_mram_sync_records;
    open_cfw_mram_sync_uintptr alternate =
        (open_cfw_mram_sync_uintptr)
            open_cfw_test_mram_sync_alternate_records;
    open_cfw_mram_sync_uintptr extent =
        sizeof(open_cfw_test_mram_sync_records);

    if (address >= base + 7U && address < base + extent) {
        return (int)((address - base - 7U)
            / OPEN_CFW_TEST_MRAM_SYNC_RECORD_SIZE);
    }
    if (
        address >= alternate + 7U
        && address < alternate + extent
    ) {
        return (int)((address - alternate - 7U)
            / OPEN_CFW_TEST_MRAM_SYNC_RECORD_SIZE);
    }
    return -1;
}

int open_cfw_memory_compare(
    const void *left,
    const void *right,
    unsigned int size
)
{
    unsigned int call = open_cfw_test_mram_sync_compare_calls;
    int index = open_cfw_test_mram_sync_record_index(left);

    if (call < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT) {
        open_cfw_test_mram_sync_compare_records[call] =
            (open_cfw_mram_sync_uintptr)left;
        open_cfw_test_mram_sync_compare_keys[call] =
            (open_cfw_mram_sync_uintptr)right;
        open_cfw_test_mram_sync_compare_sizes[call] = size;
    }
    ++open_cfw_test_mram_sync_compare_calls;
    if (
        index < 0
        || index >= (int)OPEN_CFW_TEST_MRAM_SYNC_RECORD_COUNT
    ) {
        return 0;
    }
    return open_cfw_test_mram_sync_compare_results[index];
}

unsigned int open_cfw_test_mram_sync_timestamp(void)
{
    unsigned int call = open_cfw_test_mram_sync_timestamp_calls++;

    if (call >= OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT) {
        return 0U;
    }
    return open_cfw_test_mram_sync_timestamps[call];
}

void open_cfw_test_mram_sync_publish(
    unsigned int selector,
    const void *metadata,
    const void *identifier,
    unsigned int timestamp,
    unsigned int last,
    unsigned int reserved
)
{
    unsigned int call = open_cfw_test_mram_sync_publish_calls;

    if (call < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT) {
        open_cfw_mram_sync_uintptr *record =
            &open_cfw_test_mram_sync_publish_records[
                call * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
            ];

        record[0] = selector;
        record[1] = (open_cfw_mram_sync_uintptr)metadata;
        record[2] = (open_cfw_mram_sync_uintptr)identifier;
        record[3] = timestamp;
        record[4] = last;
        record[5] = reserved;
    }
    ++open_cfw_test_mram_sync_publish_calls;
}

void open_cfw_test_mram_sync_commit(unsigned int value)
{
    ++open_cfw_test_mram_sync_commit_calls;
    open_cfw_test_mram_sync_commit_value = value;
}

unsigned int open_cfw_test_mram_sync_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_sync_level_index
        == open_cfw_test_mram_sync_switch_base_level_index
    ) {
        open_cfw_test_mram_sync_record_base =
            open_cfw_test_mram_sync_alternate_records;
    }
    if (
        open_cfw_test_mram_sync_level_index
        < open_cfw_test_mram_sync_level_count
    ) {
        result = open_cfw_test_mram_sync_levels[
            open_cfw_test_mram_sync_level_index
        ];
    }
    ++open_cfw_test_mram_sync_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_sync_argument_count(
    open_cfw_mram_sync_uintptr identity
)
{
    return (
        identity == 0x007477C4U
        || identity == 0x00726D20U
    ) ? 1U : 0U;
}

void open_cfw_test_mram_sync_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_sync_log_count;

    if (call < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT) {
        open_cfw_mram_sync_uintptr *record =
            &open_cfw_test_mram_sync_log_records[
                call * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
            ];
        unsigned int count =
            open_cfw_test_mram_sync_argument_count(
                (open_cfw_mram_sync_uintptr)identity
            );
        unsigned int index;
        va_list arguments;

        record[0] = severity;
        record[1] = (open_cfw_mram_sync_uintptr)module;
        record[2] = (open_cfw_mram_sync_uintptr)file;
        record[3] = (open_cfw_mram_sync_uintptr)function;
        record[4] = line;
        record[5] = (open_cfw_mram_sync_uintptr)identity;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_sync_log_count;
}

void open_cfw_test_mram_sync_trace(
    unsigned int event,
    const void *first_identity,
    const void *second_identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_sync_trace_count;

    if (call < OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_COUNT) {
        open_cfw_mram_sync_uintptr *record =
            &open_cfw_test_mram_sync_trace_records[
                call * OPEN_CFW_TEST_MRAM_SYNC_CAPTURE_WIDTH
            ];
        unsigned int count =
            open_cfw_test_mram_sync_argument_count(
                (open_cfw_mram_sync_uintptr)first_identity
            );
        unsigned int index;
        va_list arguments;

        record[0] = event;
        record[1] = (open_cfw_mram_sync_uintptr)first_identity;
        record[2] = (open_cfw_mram_sync_uintptr)second_identity;
        va_start(arguments, second_identity);
        for (index = 0U; index < count; ++index) {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_sync_trace_count;
}
