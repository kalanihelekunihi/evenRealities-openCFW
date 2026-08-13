/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Cordio protected-MRAM write verifier.
 */

#include <stdarg.h>
#include <string.h>

#define OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT 256U

unsigned int open_cfw_test_mram_verify_cache(
    const void *,
    unsigned int
);
int open_cfw_test_mram_verify_compare(
    const void *,
    const void *,
    unsigned int
);
unsigned int open_cfw_test_mram_verify_log_level(void);
void open_cfw_test_mram_verify_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_verify_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_verify_hex(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

unsigned char open_cfw_test_mram_verify_nvm[10U * 0x100U];

#define OPEN_CFW_MRAM_VERIFY_NVM_BASE \
    open_cfw_test_mram_verify_nvm
#define OPEN_CFW_MRAM_VERIFY_CACHE_INVALIDATE(range, clean) \
    open_cfw_test_mram_verify_cache((range), (clean))
#define OPEN_CFW_MRAM_VERIFY_COMPARE(left, right, size) \
    open_cfw_test_mram_verify_compare((left), (right), (size))
#define OPEN_CFW_MRAM_VERIFY_LOG_LEVEL() \
    open_cfw_test_mram_verify_log_level()
#define OPEN_CFW_MRAM_VERIFY_LOG(...) \
    open_cfw_test_mram_verify_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_VERIFY_TRACE(...) \
    open_cfw_test_mram_verify_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_VERIFY_HEX(...) \
    open_cfw_test_mram_verify_hex(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_verify_write.c"

unsigned int open_cfw_test_mram_verify_order[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_verify_order_count;
unsigned int open_cfw_test_mram_verify_levels[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_verify_level_count;
unsigned int open_cfw_test_mram_verify_level_index;
unsigned int open_cfw_test_mram_verify_level_default;
open_cfw_mram_verify_uintptr open_cfw_test_mram_verify_logs[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT * 9U
];
unsigned int open_cfw_test_mram_verify_log_count;
open_cfw_mram_verify_uintptr open_cfw_test_mram_verify_traces[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT * 6U
];
unsigned int open_cfw_test_mram_verify_trace_count;
open_cfw_mram_verify_uintptr open_cfw_test_mram_verify_compares[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT * 3U
];
unsigned int open_cfw_test_mram_verify_compare_count;
open_cfw_mram_verify_uintptr open_cfw_test_mram_verify_hexes[
    OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT * 4U
];
unsigned int open_cfw_test_mram_verify_hex_count;
unsigned int open_cfw_test_mram_verify_cache_count;
open_cfw_mram_verify_uintptr open_cfw_test_mram_verify_cache_range;
unsigned int open_cfw_test_mram_verify_cache_clean;

static void open_cfw_test_mram_verify_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_verify_order_count
        < OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_verify_order[
            open_cfw_test_mram_verify_order_count
        ] = event;
    }
    ++open_cfw_test_mram_verify_order_count;
}

void open_cfw_test_mram_verify_reset(void)
{
    memset(
        open_cfw_test_mram_verify_nvm,
        0,
        sizeof(open_cfw_test_mram_verify_nvm)
    );
    memset(
        open_cfw_test_mram_verify_order,
        0,
        sizeof(open_cfw_test_mram_verify_order)
    );
    memset(
        open_cfw_test_mram_verify_levels,
        0,
        sizeof(open_cfw_test_mram_verify_levels)
    );
    memset(
        open_cfw_test_mram_verify_logs,
        0,
        sizeof(open_cfw_test_mram_verify_logs)
    );
    memset(
        open_cfw_test_mram_verify_traces,
        0,
        sizeof(open_cfw_test_mram_verify_traces)
    );
    memset(
        open_cfw_test_mram_verify_compares,
        0,
        sizeof(open_cfw_test_mram_verify_compares)
    );
    memset(
        open_cfw_test_mram_verify_hexes,
        0,
        sizeof(open_cfw_test_mram_verify_hexes)
    );
    open_cfw_test_mram_verify_order_count = 0U;
    open_cfw_test_mram_verify_level_count = 0U;
    open_cfw_test_mram_verify_level_index = 0U;
    open_cfw_test_mram_verify_level_default = 0U;
    open_cfw_test_mram_verify_log_count = 0U;
    open_cfw_test_mram_verify_trace_count = 0U;
    open_cfw_test_mram_verify_compare_count = 0U;
    open_cfw_test_mram_verify_hex_count = 0U;
    open_cfw_test_mram_verify_cache_count = 0U;
    open_cfw_test_mram_verify_cache_range = 0U;
    open_cfw_test_mram_verify_cache_clean = 0U;
}

unsigned int open_cfw_test_mram_verify_log_level(void)
{
    unsigned int index = open_cfw_test_mram_verify_level_index++;
    unsigned int result = open_cfw_test_mram_verify_level_default;

    open_cfw_test_mram_verify_order_append(1U);
    if (index < open_cfw_test_mram_verify_level_count) {
        result = open_cfw_test_mram_verify_levels[index];
    }
    return result;
}

static unsigned int open_cfw_test_mram_verify_line_arguments(
    unsigned int line
)
{
    if (line == 0x782U) {
        return 1U;
    }
    if (line == 0x787U || line == 0x78DU || line == 0x793U) {
        return 2U;
    }
    return 0U;
}

void open_cfw_test_mram_verify_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_verify_log_count;
    unsigned int count =
        open_cfw_test_mram_verify_line_arguments(line);
    va_list arguments;

    open_cfw_test_mram_verify_order_append(2U);
    if (call < OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT) {
        open_cfw_mram_verify_uintptr *record =
            open_cfw_test_mram_verify_logs + call * 9U;

        record[0] = severity;
        record[1] = (open_cfw_mram_verify_uintptr)module;
        record[2] = (open_cfw_mram_verify_uintptr)file;
        record[3] = (open_cfw_mram_verify_uintptr)function;
        record[4] = line;
        record[5] = (open_cfw_mram_verify_uintptr)identity;
        record[6] = count;
        va_start(arguments, identity);
        if (count != 0U) {
            record[7] = va_arg(arguments, unsigned int);
        }
        if (count == 2U) {
            record[8] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_verify_log_count;
}

static unsigned int open_cfw_test_mram_verify_trace_arguments(
    unsigned int event
)
{
    if (event == 0x10400000U) {
        return 1U;
    }
    if (event == 0x04800000U) {
        return 2U;
    }
    return 0U;
}

void open_cfw_test_mram_verify_trace(
    unsigned int event,
    const void *schema,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_verify_trace_count;
    unsigned int count =
        open_cfw_test_mram_verify_trace_arguments(event);
    va_list arguments;

    open_cfw_test_mram_verify_order_append(3U);
    if (call < OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT) {
        open_cfw_mram_verify_uintptr *record =
            open_cfw_test_mram_verify_traces + call * 6U;

        record[0] = event;
        record[1] = (open_cfw_mram_verify_uintptr)schema;
        record[2] = (open_cfw_mram_verify_uintptr)identity;
        record[3] = count;
        va_start(arguments, identity);
        if (count != 0U) {
            record[4] = va_arg(arguments, unsigned int);
        }
        if (count == 2U) {
            record[5] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_verify_trace_count;
}

unsigned int open_cfw_test_mram_verify_cache(
    const void *range,
    unsigned int clean
)
{
    open_cfw_test_mram_verify_order_append(4U);
    ++open_cfw_test_mram_verify_cache_count;
    open_cfw_test_mram_verify_cache_range =
        (open_cfw_mram_verify_uintptr)range;
    open_cfw_test_mram_verify_cache_clean = clean;
    return 0U;
}

int open_cfw_test_mram_verify_compare(
    const void *left,
    const void *right,
    unsigned int size
)
{
    unsigned int call = open_cfw_test_mram_verify_compare_count;

    open_cfw_test_mram_verify_order_append(5U);
    if (call < OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT) {
        open_cfw_mram_verify_uintptr *record =
            open_cfw_test_mram_verify_compares + call * 3U;

        record[0] = (open_cfw_mram_verify_uintptr)left;
        record[1] = (open_cfw_mram_verify_uintptr)right;
        record[2] = size;
    }
    ++open_cfw_test_mram_verify_compare_count;
    return memcmp(left, right, size);
}

void open_cfw_test_mram_verify_hex(
    const void *label,
    unsigned int width,
    const void *data,
    unsigned int size
)
{
    unsigned int call = open_cfw_test_mram_verify_hex_count;

    open_cfw_test_mram_verify_order_append(6U);
    if (call < OPEN_CFW_TEST_MRAM_VERIFY_CAPTURE_COUNT) {
        open_cfw_mram_verify_uintptr *record =
            open_cfw_test_mram_verify_hexes + call * 4U;

        record[0] = (open_cfw_mram_verify_uintptr)label;
        record[1] = width;
        record[2] = (open_cfw_mram_verify_uintptr)data;
        record[3] = size;
    }
    ++open_cfw_test_mram_verify_hex_count;
}
