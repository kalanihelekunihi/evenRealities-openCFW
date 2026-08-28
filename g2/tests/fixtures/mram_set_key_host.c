/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Cordio application-database key writer.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_SET_KEY_CAPTURE_COUNT 512U
#define OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_COUNT 64U
#define OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_WIDTH 24U

unsigned int open_cfw_test_mram_set_key_update(
    const unsigned char *
);
unsigned int open_cfw_test_mram_set_key_verify(
    const unsigned char *
);
unsigned int open_cfw_test_mram_set_key_log_level(void);
void open_cfw_test_mram_set_key_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_set_key_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_SET_KEY_UPDATE(record) \
    open_cfw_test_mram_set_key_update(record)
#define OPEN_CFW_MRAM_SET_KEY_VERIFY(record) \
    open_cfw_test_mram_set_key_verify(record)
#define OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL() \
    open_cfw_test_mram_set_key_log_level()
#define OPEN_CFW_MRAM_SET_KEY_LOG(...) \
    open_cfw_test_mram_set_key_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_SET_KEY_TRACE(...) \
    open_cfw_test_mram_set_key_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_set_key.c"

unsigned int open_cfw_test_mram_set_key_order[
    OPEN_CFW_TEST_MRAM_SET_KEY_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_set_key_order_count;
unsigned int open_cfw_test_mram_set_key_levels[
    OPEN_CFW_TEST_MRAM_SET_KEY_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_set_key_level_count;
unsigned int open_cfw_test_mram_set_key_level_index;
unsigned int open_cfw_test_mram_set_key_level_default;
open_cfw_mram_set_key_uintptr open_cfw_test_mram_set_key_log_records[
    OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_COUNT
    * OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_WIDTH
];
unsigned int open_cfw_test_mram_set_key_log_count;
open_cfw_mram_set_key_uintptr open_cfw_test_mram_set_key_trace_records[
    OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_COUNT
    * OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_WIDTH
];
unsigned int open_cfw_test_mram_set_key_trace_count;
unsigned int open_cfw_test_mram_set_key_update_calls;
open_cfw_mram_set_key_uintptr open_cfw_test_mram_set_key_update_record;
unsigned int open_cfw_test_mram_set_key_update_result;
unsigned int open_cfw_test_mram_set_key_verify_calls;
open_cfw_mram_set_key_uintptr open_cfw_test_mram_set_key_verify_record;
unsigned int open_cfw_test_mram_set_key_verify_result;

static void open_cfw_test_mram_set_key_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_set_key_order_count
        < OPEN_CFW_TEST_MRAM_SET_KEY_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_set_key_order[
            open_cfw_test_mram_set_key_order_count
        ] = event;
    }
    ++open_cfw_test_mram_set_key_order_count;
}

static unsigned int open_cfw_test_mram_set_key_argument_count(
    open_cfw_mram_set_key_uintptr identity
)
{
    switch (identity) {
        case 0x007693DCU:
        case 0x00751EF0U:
            return 0U;
        case 0x007693C0U:
        case 0x00747864U:
        case 0x0074788CU:
        case 0x00726DBCU:
        case 0x007478B4U:
        case 0x00726DF0U:
        case 0x00731844U:
        case 0x00712730U:
            return 1U;
        case 0x007126F4U:
        case 0x00700348U:
        case 0x0071C070U:
        case 0x0070038CU:
            return 2U;
        case 0x0071C0A8U:
        case 0x007092E4U:
            return 6U;
        default:
            return 16U;
    }
}

void open_cfw_test_mram_set_key_reset(void)
{
    memset(
        open_cfw_test_mram_set_key_order,
        0,
        sizeof(open_cfw_test_mram_set_key_order)
    );
    memset(
        open_cfw_test_mram_set_key_levels,
        0,
        sizeof(open_cfw_test_mram_set_key_levels)
    );
    memset(
        open_cfw_test_mram_set_key_log_records,
        0,
        sizeof(open_cfw_test_mram_set_key_log_records)
    );
    memset(
        open_cfw_test_mram_set_key_trace_records,
        0,
        sizeof(open_cfw_test_mram_set_key_trace_records)
    );
    open_cfw_test_mram_set_key_order_count = 0U;
    open_cfw_test_mram_set_key_level_count = 0U;
    open_cfw_test_mram_set_key_level_index = 0U;
    open_cfw_test_mram_set_key_level_default = 0U;
    open_cfw_test_mram_set_key_log_count = 0U;
    open_cfw_test_mram_set_key_trace_count = 0U;
    open_cfw_test_mram_set_key_update_calls = 0U;
    open_cfw_test_mram_set_key_update_record = 0U;
    open_cfw_test_mram_set_key_update_result = 0U;
    open_cfw_test_mram_set_key_verify_calls = 0U;
    open_cfw_test_mram_set_key_verify_record = 0U;
    open_cfw_test_mram_set_key_verify_result = 0U;
}

unsigned int open_cfw_test_mram_set_key_log_level(void)
{
    unsigned int index = open_cfw_test_mram_set_key_level_index++;
    unsigned int result = open_cfw_test_mram_set_key_level_default;

    open_cfw_test_mram_set_key_order_append(1U);
    if (index < open_cfw_test_mram_set_key_level_count) {
        result = open_cfw_test_mram_set_key_levels[index];
    }
    return result;
}

void open_cfw_test_mram_set_key_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_set_key_log_count;
    unsigned int count = open_cfw_test_mram_set_key_argument_count(
        (open_cfw_mram_set_key_uintptr)identity
    );
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_set_key_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_COUNT) {
        open_cfw_mram_set_key_uintptr *record =
            open_cfw_test_mram_set_key_log_records
            + call * OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_WIDTH;

        record[0] = severity;
        record[1] = (open_cfw_mram_set_key_uintptr)module;
        record[2] = (open_cfw_mram_set_key_uintptr)file;
        record[3] = (open_cfw_mram_set_key_uintptr)function;
        record[4] = line;
        record[5] = (open_cfw_mram_set_key_uintptr)identity;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_set_key_log_count;
}

void open_cfw_test_mram_set_key_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_set_key_trace_count;
    unsigned int count = open_cfw_test_mram_set_key_argument_count(
        (open_cfw_mram_set_key_uintptr)identity
    );
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_set_key_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_COUNT) {
        open_cfw_mram_set_key_uintptr *record =
            open_cfw_test_mram_set_key_trace_records
            + call * OPEN_CFW_TEST_MRAM_SET_KEY_DIAGNOSTIC_WIDTH;

        record[0] = event;
        record[1] = (open_cfw_mram_set_key_uintptr)schema;
        record[2] = (open_cfw_mram_set_key_uintptr)identity;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_set_key_trace_count;
}

unsigned int open_cfw_test_mram_set_key_update(
    const unsigned char *record
)
{
    open_cfw_test_mram_set_key_order_append(4U);
    ++open_cfw_test_mram_set_key_update_calls;
    open_cfw_test_mram_set_key_update_record =
        (open_cfw_mram_set_key_uintptr)record;
    return open_cfw_test_mram_set_key_update_result;
}

unsigned int open_cfw_test_mram_set_key_verify(
    const unsigned char *record
)
{
    open_cfw_test_mram_set_key_order_append(5U);
    ++open_cfw_test_mram_set_key_verify_calls;
    open_cfw_test_mram_set_key_verify_record =
        (open_cfw_mram_set_key_uintptr)record;
    return open_cfw_test_mram_set_key_verify_result;
}
