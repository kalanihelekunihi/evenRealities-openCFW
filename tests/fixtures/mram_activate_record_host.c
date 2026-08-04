/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record activation and
 * persistence adapter.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT 32U
#define OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_WIDTH 12U

unsigned int open_cfw_test_mram_activate_update(
    const unsigned char *
);
unsigned int open_cfw_test_mram_activate_verify(
    const unsigned char *
);
unsigned int open_cfw_test_mram_activate_log_level(void);
void open_cfw_test_mram_activate_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_activate_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned int open_cfw_test_mram_activate_counter;

#define OPEN_CFW_MRAM_ACTIVATE_COUNTER \
    open_cfw_test_mram_activate_counter
#define OPEN_CFW_MRAM_ACTIVATE_UPDATE(record) \
    open_cfw_test_mram_activate_update(record)
#define OPEN_CFW_MRAM_ACTIVATE_VERIFY(record) \
    open_cfw_test_mram_activate_verify(record)
#define OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL() \
    open_cfw_test_mram_activate_log_level()
#define OPEN_CFW_MRAM_ACTIVATE_LOG(...) \
    open_cfw_test_mram_activate_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_ACTIVATE_TRACE(...) \
    open_cfw_test_mram_activate_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_activate_record.c"

unsigned int open_cfw_test_mram_activate_order[
    OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_activate_order_count;
open_cfw_mram_activate_uintptr
    open_cfw_test_mram_activate_update_record;
open_cfw_mram_activate_uintptr
    open_cfw_test_mram_activate_verify_record;
unsigned int open_cfw_test_mram_activate_update_result;
unsigned int open_cfw_test_mram_activate_verify_result;
unsigned int open_cfw_test_mram_activate_update_state[4];
unsigned int open_cfw_test_mram_activate_verify_state[4];
unsigned int open_cfw_test_mram_activate_levels[
    OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_activate_level_count;
unsigned int open_cfw_test_mram_activate_level_index;
open_cfw_mram_activate_uintptr open_cfw_test_mram_activate_logs[
    OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_activate_log_count;
open_cfw_mram_activate_uintptr open_cfw_test_mram_activate_traces[
    OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_activate_trace_count;

static unsigned int open_cfw_test_mram_activate_u32(
    const unsigned char *record
)
{
    unsigned int value;

    memcpy(&value, record + 0xC4U, sizeof(value));
    return value;
}

static void open_cfw_test_mram_activate_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_activate_order_count
        < OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_activate_order[
            open_cfw_test_mram_activate_order_count
        ] = event;
    }
    ++open_cfw_test_mram_activate_order_count;
}

void open_cfw_test_mram_activate_reset(void)
{
    memset(
        open_cfw_test_mram_activate_order,
        0,
        sizeof(open_cfw_test_mram_activate_order)
    );
    memset(
        open_cfw_test_mram_activate_update_state,
        0,
        sizeof(open_cfw_test_mram_activate_update_state)
    );
    memset(
        open_cfw_test_mram_activate_verify_state,
        0,
        sizeof(open_cfw_test_mram_activate_verify_state)
    );
    memset(
        open_cfw_test_mram_activate_levels,
        0,
        sizeof(open_cfw_test_mram_activate_levels)
    );
    memset(
        open_cfw_test_mram_activate_logs,
        0,
        sizeof(open_cfw_test_mram_activate_logs)
    );
    memset(
        open_cfw_test_mram_activate_traces,
        0,
        sizeof(open_cfw_test_mram_activate_traces)
    );
    open_cfw_test_mram_activate_counter = 0U;
    open_cfw_test_mram_activate_order_count = 0U;
    open_cfw_test_mram_activate_update_record = 0U;
    open_cfw_test_mram_activate_verify_record = 0U;
    open_cfw_test_mram_activate_update_result = 0U;
    open_cfw_test_mram_activate_verify_result = 0U;
    open_cfw_test_mram_activate_level_count = 0U;
    open_cfw_test_mram_activate_level_index = 0U;
    open_cfw_test_mram_activate_log_count = 0U;
    open_cfw_test_mram_activate_trace_count = 0U;
}

static void open_cfw_test_mram_activate_capture_state(
    unsigned int *output,
    const unsigned char *record
)
{
    output[0] = record[0x30U];
    output[1] = record[0x2FU];
    output[2] = record[0x2EU];
    output[3] = open_cfw_test_mram_activate_u32(record);
}

unsigned int open_cfw_test_mram_activate_update(
    const unsigned char *record
)
{
    open_cfw_test_mram_activate_order_append(1U);
    open_cfw_test_mram_activate_update_record =
        (open_cfw_mram_activate_uintptr)record;
    open_cfw_test_mram_activate_capture_state(
        open_cfw_test_mram_activate_update_state,
        record
    );
    return open_cfw_test_mram_activate_update_result;
}

unsigned int open_cfw_test_mram_activate_verify(
    const unsigned char *record
)
{
    open_cfw_test_mram_activate_order_append(2U);
    open_cfw_test_mram_activate_verify_record =
        (open_cfw_mram_activate_uintptr)record;
    open_cfw_test_mram_activate_capture_state(
        open_cfw_test_mram_activate_verify_state,
        record
    );
    return open_cfw_test_mram_activate_verify_result;
}

unsigned int open_cfw_test_mram_activate_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_activate_level_index
        < open_cfw_test_mram_activate_level_count
    ) {
        result = open_cfw_test_mram_activate_levels[
            open_cfw_test_mram_activate_level_index
        ];
    }
    ++open_cfw_test_mram_activate_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_activate_argument_count(
    open_cfw_mram_activate_uintptr identity
)
{
    if (
        identity == 0x0071267CU
        || identity == 0x006F84D4U
        || identity == 0x006EB538U
        || identity == 0x006DF5A4U
    ) {
        return 1U;
    }
    return 0U;
}

void open_cfw_test_mram_activate_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_activate_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (
        open_cfw_test_mram_activate_log_count
        >= OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_activate_log_count;
        return;
    }
    output = &open_cfw_test_mram_activate_logs[
        open_cfw_test_mram_activate_log_count
        * OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_WIDTH
    ];
    output[0] = severity;
    output[1] = (open_cfw_mram_activate_uintptr)module;
    output[2] = (open_cfw_mram_activate_uintptr)file;
    output[3] = (open_cfw_mram_activate_uintptr)function;
    output[4] = line;
    output[5] = (open_cfw_mram_activate_uintptr)identity;
    count = open_cfw_test_mram_activate_argument_count(output[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        output[6U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_mram_activate_log_count;
}

void open_cfw_test_mram_activate_trace(
    unsigned int event,
    const void *first_identity,
    const void *second_identity,
    ...
)
{
    open_cfw_mram_activate_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (
        open_cfw_test_mram_activate_trace_count
        >= OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_activate_trace_count;
        return;
    }
    output = &open_cfw_test_mram_activate_traces[
        open_cfw_test_mram_activate_trace_count
        * OPEN_CFW_TEST_MRAM_ACTIVATE_CAPTURE_WIDTH
    ];
    output[0] = event;
    output[1] = (open_cfw_mram_activate_uintptr)first_identity;
    output[2] = (open_cfw_mram_activate_uintptr)second_identity;
    count = open_cfw_test_mram_activate_argument_count(output[1]);
    va_start(arguments, second_identity);
    for (index = 0U; index < count; ++index) {
        output[3U + index] = va_arg(arguments, unsigned int);
    }
    va_end(arguments);
    ++open_cfw_test_mram_activate_trace_count;
}
