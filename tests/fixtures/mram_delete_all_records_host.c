/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for Cordio AppDbDeleteAllRecords.
 */

#include <stdarg.h>

unsigned int open_cfw_test_mram_delete_log_level(void);
void open_cfw_test_mram_delete_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_delete_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_delete_clear_prefix_byte(
    volatile unsigned char *,
    unsigned int
);
void open_cfw_test_mram_delete_program_zero_region(void);

unsigned char open_cfw_test_mram_delete_records[10U * 200U];

#define OPEN_CFW_MRAM_DELETE_RECORDS open_cfw_test_mram_delete_records
#define OPEN_CFW_MRAM_DELETE_LOG_LEVEL() \
    open_cfw_test_mram_delete_log_level()
#define OPEN_CFW_MRAM_DELETE_LOG(...) \
    open_cfw_test_mram_delete_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_DELETE_TRACE(...) \
    open_cfw_test_mram_delete_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_DELETE_CLEAR_PREFIX_BYTE(record, index) \
    open_cfw_test_mram_delete_clear_prefix_byte((record), (index))
#define OPEN_CFW_MRAM_DELETE_PROGRAM_ZERO_REGION() \
    open_cfw_test_mram_delete_program_zero_region()

#include "../../components/apollo_main/core_overlay/mram_delete_all_records.c"

#define OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT 80U
#define OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH 6U

unsigned int open_cfw_test_mram_delete_levels[
    OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_delete_level_count;
unsigned int open_cfw_test_mram_delete_level_index;
open_cfw_mram_delete_uintptr open_cfw_test_mram_delete_logs[
    OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_delete_log_count;
open_cfw_mram_delete_uintptr open_cfw_test_mram_delete_traces[
    OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_delete_trace_count;
unsigned int open_cfw_test_mram_delete_order[
    OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_delete_order_count;
unsigned int open_cfw_test_mram_delete_clear_count;
unsigned int open_cfw_test_mram_delete_flags_were_clear;
unsigned int open_cfw_test_mram_delete_program_calls;

void open_cfw_test_mram_delete_reset(void)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT;
        ++index
    ) {
        open_cfw_test_mram_delete_levels[index] = 0U;
        open_cfw_test_mram_delete_order[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
                * OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_delete_logs[index] = 0U;
        open_cfw_test_mram_delete_traces[index] = 0U;
    }
    open_cfw_test_mram_delete_level_count = 0U;
    open_cfw_test_mram_delete_level_index = 0U;
    open_cfw_test_mram_delete_log_count = 0U;
    open_cfw_test_mram_delete_trace_count = 0U;
    open_cfw_test_mram_delete_order_count = 0U;
    open_cfw_test_mram_delete_clear_count = 0U;
    open_cfw_test_mram_delete_flags_were_clear = 1U;
    open_cfw_test_mram_delete_program_calls = 0U;
}

unsigned int open_cfw_test_mram_delete_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_delete_level_index
        < open_cfw_test_mram_delete_level_count
    ) {
        result = open_cfw_test_mram_delete_levels[
            open_cfw_test_mram_delete_level_index
        ];
    }
    ++open_cfw_test_mram_delete_level_index;
    return result;
}

void open_cfw_test_mram_delete_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_delete_uintptr *record;

    if (
        open_cfw_test_mram_delete_log_count
        >= OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_delete_log_count;
        return;
    }
    record = &open_cfw_test_mram_delete_logs[
        open_cfw_test_mram_delete_log_count
        * OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH
    ];
    record[0] = severity;
    record[1] = (open_cfw_mram_delete_uintptr)module;
    record[2] = (open_cfw_mram_delete_uintptr)file;
    record[3] = (open_cfw_mram_delete_uintptr)function;
    record[4] = line;
    record[5] = (open_cfw_mram_delete_uintptr)identity;
    ++open_cfw_test_mram_delete_log_count;
}

void open_cfw_test_mram_delete_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_mram_delete_uintptr *record;

    if (
        open_cfw_test_mram_delete_trace_count
        >= OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_delete_trace_count;
        return;
    }
    record = &open_cfw_test_mram_delete_traces[
        open_cfw_test_mram_delete_trace_count
        * OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_WIDTH
    ];
    record[0] = event;
    record[1] = (open_cfw_mram_delete_uintptr)identity;
    record[2] = (open_cfw_mram_delete_uintptr)duplicate_identity;
    ++open_cfw_test_mram_delete_trace_count;
}

void open_cfw_test_mram_delete_clear_prefix_byte(
    volatile unsigned char *record,
    unsigned int index
)
{
    unsigned int record_index =
        (unsigned int)(
            record - open_cfw_test_mram_delete_records
        ) / 200U;

    if (
        index == 0U
        && (record[0x2FU] != 0U || record[0x30U] != 0U)
    ) {
        open_cfw_test_mram_delete_flags_were_clear = 0U;
    }
    if (
        open_cfw_test_mram_delete_order_count
        < OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_delete_order[
            open_cfw_test_mram_delete_order_count
        ] = record_index * 10U + index + 1U;
    }
    ++open_cfw_test_mram_delete_order_count;
    ++open_cfw_test_mram_delete_clear_count;
    record[index] = 0U;
}

void open_cfw_test_mram_delete_program_zero_region(void)
{
    if (
        open_cfw_test_mram_delete_order_count
        < OPEN_CFW_TEST_MRAM_DELETE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_delete_order[
            open_cfw_test_mram_delete_order_count
        ] = 1000U;
    }
    ++open_cfw_test_mram_delete_order_count;
    ++open_cfw_test_mram_delete_program_calls;
}
