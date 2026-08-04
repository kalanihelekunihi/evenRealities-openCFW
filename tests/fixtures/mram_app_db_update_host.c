/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record-database updater.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_DB_RECORD_COUNT 10U
#define OPEN_CFW_TEST_MRAM_DB_RECORD_STRIDE 0x100U
#define OPEN_CFW_TEST_MRAM_DB_RECORD_BYTES 0xC8U
#define OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT 512U
#define OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_COUNT 256U
#define OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_WIDTH 16U

unsigned int open_cfw_test_mram_db_cache_invalidate(
    const void *,
    unsigned int
);
void open_cfw_test_mram_db_update_record(
    const unsigned char *,
    unsigned char
);
void open_cfw_test_mram_db_dump_record(
    const void *,
    unsigned int
);
unsigned int open_cfw_test_mram_db_log_level(void);
void open_cfw_test_mram_db_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_db_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);

unsigned char open_cfw_test_mram_db_nvm[
    OPEN_CFW_TEST_MRAM_DB_RECORD_COUNT
    * OPEN_CFW_TEST_MRAM_DB_RECORD_STRIDE
];

#define OPEN_CFW_MRAM_DB_NVM_BASE open_cfw_test_mram_db_nvm
#define OPEN_CFW_MRAM_DB_CACHE_INVALIDATE(range, all) \
    open_cfw_test_mram_db_cache_invalidate((range), (all))
#define OPEN_CFW_MRAM_DB_UPDATE_RECORD(record, index) \
    open_cfw_test_mram_db_update_record((record), (index))
#define OPEN_CFW_MRAM_DB_DUMP_RECORD(record, index) \
    open_cfw_test_mram_db_dump_record((record), (index))
#define OPEN_CFW_MRAM_DB_LOG_LEVEL() \
    open_cfw_test_mram_db_log_level()
#define OPEN_CFW_MRAM_DB_LOG(...) \
    open_cfw_test_mram_db_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_DB_TRACE(...) \
    open_cfw_test_mram_db_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_app_db_update.c"

unsigned int open_cfw_test_mram_db_order[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_order_count;
unsigned int open_cfw_test_mram_db_cache_calls;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_cache_ranges[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_cache_all[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_compare_calls;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_compare_left[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
open_cfw_mram_db_uintptr open_cfw_test_mram_db_compare_right[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_compare_sizes[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_update_calls;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_update_records[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_update_indices[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_update_mode;
unsigned int open_cfw_test_mram_db_dump_calls;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_dump_records[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_dump_indices[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_levels[
    OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_db_level_count;
unsigned int open_cfw_test_mram_db_level_index;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_log_records[
    OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_COUNT
    * OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_WIDTH
];
unsigned int open_cfw_test_mram_db_log_count;
open_cfw_mram_db_uintptr open_cfw_test_mram_db_trace_records[
    OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_COUNT
    * OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_WIDTH
];
unsigned int open_cfw_test_mram_db_trace_count;

static void open_cfw_test_mram_db_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_db_order_count
        < OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_db_order[
            open_cfw_test_mram_db_order_count
        ] = event;
    }
    ++open_cfw_test_mram_db_order_count;
}

void open_cfw_test_mram_db_reset(void)
{
    memset(open_cfw_test_mram_db_nvm, 0, sizeof(open_cfw_test_mram_db_nvm));
    memset(open_cfw_test_mram_db_order, 0, sizeof(open_cfw_test_mram_db_order));
    memset(
        open_cfw_test_mram_db_cache_ranges,
        0,
        sizeof(open_cfw_test_mram_db_cache_ranges)
    );
    memset(
        open_cfw_test_mram_db_cache_all,
        0,
        sizeof(open_cfw_test_mram_db_cache_all)
    );
    memset(
        open_cfw_test_mram_db_compare_left,
        0,
        sizeof(open_cfw_test_mram_db_compare_left)
    );
    memset(
        open_cfw_test_mram_db_compare_right,
        0,
        sizeof(open_cfw_test_mram_db_compare_right)
    );
    memset(
        open_cfw_test_mram_db_compare_sizes,
        0,
        sizeof(open_cfw_test_mram_db_compare_sizes)
    );
    memset(
        open_cfw_test_mram_db_update_records,
        0,
        sizeof(open_cfw_test_mram_db_update_records)
    );
    memset(
        open_cfw_test_mram_db_update_indices,
        0,
        sizeof(open_cfw_test_mram_db_update_indices)
    );
    memset(
        open_cfw_test_mram_db_dump_records,
        0,
        sizeof(open_cfw_test_mram_db_dump_records)
    );
    memset(
        open_cfw_test_mram_db_dump_indices,
        0,
        sizeof(open_cfw_test_mram_db_dump_indices)
    );
    memset(
        open_cfw_test_mram_db_levels,
        0,
        sizeof(open_cfw_test_mram_db_levels)
    );
    memset(
        open_cfw_test_mram_db_log_records,
        0,
        sizeof(open_cfw_test_mram_db_log_records)
    );
    memset(
        open_cfw_test_mram_db_trace_records,
        0,
        sizeof(open_cfw_test_mram_db_trace_records)
    );

    open_cfw_test_mram_db_order_count = 0U;
    open_cfw_test_mram_db_cache_calls = 0U;
    open_cfw_test_mram_db_compare_calls = 0U;
    open_cfw_test_mram_db_update_calls = 0U;
    open_cfw_test_mram_db_update_mode = 0U;
    open_cfw_test_mram_db_dump_calls = 0U;
    open_cfw_test_mram_db_level_count = 0U;
    open_cfw_test_mram_db_level_index = 0U;
    open_cfw_test_mram_db_log_count = 0U;
    open_cfw_test_mram_db_trace_count = 0U;
}

unsigned int open_cfw_test_mram_db_cache_invalidate(
    const void *range,
    unsigned int all
)
{
    unsigned int call = open_cfw_test_mram_db_cache_calls;

    open_cfw_test_mram_db_order_append(1U);
    if (call < OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT) {
        open_cfw_test_mram_db_cache_ranges[call] =
            (open_cfw_mram_db_uintptr)range;
        open_cfw_test_mram_db_cache_all[call] = all;
    }
    ++open_cfw_test_mram_db_cache_calls;
    return 0U;
}

int open_cfw_memory_compare(
    const void *left,
    const void *right,
    unsigned int size
)
{
    unsigned int call = open_cfw_test_mram_db_compare_calls;

    open_cfw_test_mram_db_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT) {
        open_cfw_test_mram_db_compare_left[call] =
            (open_cfw_mram_db_uintptr)left;
        open_cfw_test_mram_db_compare_right[call] =
            (open_cfw_mram_db_uintptr)right;
        open_cfw_test_mram_db_compare_sizes[call] = size;
    }
    ++open_cfw_test_mram_db_compare_calls;
    return memcmp(left, right, size);
}

void open_cfw_test_mram_db_update_record(
    const unsigned char *record,
    unsigned char record_index
)
{
    unsigned int call = open_cfw_test_mram_db_update_calls;
    unsigned char *destination =
        open_cfw_test_mram_db_nvm
        + (unsigned int)record_index
            * OPEN_CFW_TEST_MRAM_DB_RECORD_STRIDE;

    open_cfw_test_mram_db_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT) {
        open_cfw_test_mram_db_update_records[call] =
            (open_cfw_mram_db_uintptr)record;
        open_cfw_test_mram_db_update_indices[call] = record_index;
    }
    ++open_cfw_test_mram_db_update_calls;

    if (open_cfw_test_mram_db_update_mode != 0U) {
        memcpy(
            destination,
            record,
            OPEN_CFW_TEST_MRAM_DB_RECORD_BYTES
        );
    }
    if (open_cfw_test_mram_db_update_mode == 2U) {
        destination[0] ^= 0xFFU;
    }
}

void open_cfw_test_mram_db_dump_record(
    const void *record,
    unsigned int record_index
)
{
    unsigned int call = open_cfw_test_mram_db_dump_calls;

    open_cfw_test_mram_db_order_append(4U);
    if (call < OPEN_CFW_TEST_MRAM_DB_CAPTURE_COUNT) {
        open_cfw_test_mram_db_dump_records[call] =
            (open_cfw_mram_db_uintptr)record;
        open_cfw_test_mram_db_dump_indices[call] = record_index;
    }
    ++open_cfw_test_mram_db_dump_calls;
}

unsigned int open_cfw_test_mram_db_log_level(void)
{
    unsigned int result = 0U;

    open_cfw_test_mram_db_order_append(5U);
    if (
        open_cfw_test_mram_db_level_index
        < open_cfw_test_mram_db_level_count
    ) {
        result = open_cfw_test_mram_db_levels[
            open_cfw_test_mram_db_level_index
        ];
    }
    ++open_cfw_test_mram_db_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_db_argument_count(
    open_cfw_mram_db_uintptr identity
)
{
    switch ((unsigned int)identity) {
        case 0x0071258CU:
        case 0x006F82DCU:
        case 0x00712640U:
        case 0x006F848CU:
            return 0U;
        case 0x00709124U:
        case 0x006F836CU:
        case 0x00769388U:
        case 0x00751EA8U:
        case 0x007001B0U:
        case 0x006EB4E8U:
        case 0x007693A4U:
        case 0x00747814U:
        case 0x006F1800U:
        case 0x006E2388U:
        case 0x00709164U:
        case 0x006F83B4U:
        case 0x0074783CU:
        case 0x00726D88U:
        case 0x0071BF58U:
        case 0x00700238U:
        case 0x006F1898U:
        case 0x006E2438U:
            return 1U;
        case 0x006E23E0U:
        case 0x006D9EA4U:
        case 0x007125C8U:
        case 0x007001F4U:
        case 0x007091A4U:
        case 0x006F184CU:
            return 2U;
        case 0x006F8324U:
        case 0x006E6280U:
            return 3U;
        case 0x00712604U:
        case 0x006F83FCU:
        case 0x007091E4U:
        case 0x006F18E4U:
        case 0x00709224U:
        case 0x006F8444U:
            return 6U;
        case 0x006D9F08U:
        case 0x006A6BD4U:
            return 7U;
        default:
            return 0U;
    }
}

void open_cfw_test_mram_db_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_db_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_db_order_append(6U);
    if (
        open_cfw_test_mram_db_log_count
        >= OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_COUNT
    ) {
        ++open_cfw_test_mram_db_log_count;
        return;
    }
    output = &open_cfw_test_mram_db_log_records[
        open_cfw_test_mram_db_log_count
        * OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_WIDTH
    ];
    output[0] = severity;
    output[1] = (open_cfw_mram_db_uintptr)module;
    output[2] = (open_cfw_mram_db_uintptr)file;
    output[3] = (open_cfw_mram_db_uintptr)function;
    output[4] = line;
    output[5] = (open_cfw_mram_db_uintptr)identity;
    count = open_cfw_test_mram_db_argument_count(output[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        output[6U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_mram_db_log_count;
}

void open_cfw_test_mram_db_trace(
    unsigned int event,
    const void *first_identity,
    const void *second_identity,
    ...
)
{
    open_cfw_mram_db_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_db_order_append(7U);
    if (
        open_cfw_test_mram_db_trace_count
        >= OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_COUNT
    ) {
        ++open_cfw_test_mram_db_trace_count;
        return;
    }
    output = &open_cfw_test_mram_db_trace_records[
        open_cfw_test_mram_db_trace_count
        * OPEN_CFW_TEST_MRAM_DB_DIAGNOSTIC_WIDTH
    ];
    output[0] = event;
    output[1] = (open_cfw_mram_db_uintptr)first_identity;
    output[2] = (open_cfw_mram_db_uintptr)second_identity;
    count = open_cfw_test_mram_db_argument_count(output[1]);
    va_start(arguments, second_identity);
    for (index = 0U; index < count; ++index) {
        output[3U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_mram_db_trace_count;
}
