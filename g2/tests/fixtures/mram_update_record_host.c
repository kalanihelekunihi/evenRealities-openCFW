/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record programmer.
 */

#include <stdarg.h>

#define OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT 16U
#define OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH 12U

unsigned int open_cfw_test_mram_update_cache_invalidate(
    unsigned int,
    unsigned int
);
unsigned int open_cfw_test_mram_update_program(
    unsigned int,
    const unsigned int *,
    unsigned int *,
    unsigned int
);
unsigned int open_cfw_test_mram_update_exception_number(void);
unsigned int open_cfw_test_mram_update_yield(void);
unsigned int open_cfw_test_mram_update_log_level(void);
void open_cfw_test_mram_update_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_update_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);

unsigned char open_cfw_test_mram_update_nvm[0x10000U];

#define OPEN_CFW_MRAM_UPDATE_NVM_BASE open_cfw_test_mram_update_nvm
#define OPEN_CFW_MRAM_UPDATE_CACHE_INVALIDATE(range, all) \
    open_cfw_test_mram_update_cache_invalidate((range), (all))
#define OPEN_CFW_MRAM_UPDATE_PROGRAM(key, source, destination, count) \
    open_cfw_test_mram_update_program( \
        (key), \
        (source), \
        (destination), \
        (count) \
    )
#define OPEN_CFW_MRAM_UPDATE_EXCEPTION_NUMBER() \
    open_cfw_test_mram_update_exception_number()
#define OPEN_CFW_MRAM_UPDATE_YIELD() \
    open_cfw_test_mram_update_yield()
#define OPEN_CFW_MRAM_UPDATE_LOG_LEVEL() \
    open_cfw_test_mram_update_log_level()
#define OPEN_CFW_MRAM_UPDATE_LOG(...) \
    open_cfw_test_mram_update_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_UPDATE_TRACE(...) \
    open_cfw_test_mram_update_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_update_record.c"

unsigned int open_cfw_test_mram_update_order[
    OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_update_order_count;
unsigned int open_cfw_test_mram_update_cache_calls;
unsigned int open_cfw_test_mram_update_cache_range;
unsigned int open_cfw_test_mram_update_cache_all;
unsigned int open_cfw_test_mram_update_program_calls;
unsigned int open_cfw_test_mram_update_program_results[2];
unsigned int open_cfw_test_mram_update_program_keys[2];
open_cfw_mram_update_uintptr
    open_cfw_test_mram_update_program_sources[2];
open_cfw_mram_update_uintptr
    open_cfw_test_mram_update_program_destinations[2];
unsigned int open_cfw_test_mram_update_program_counts[2];
unsigned int open_cfw_test_mram_update_exception_calls;
unsigned int open_cfw_test_mram_update_exception_value;
unsigned int open_cfw_test_mram_update_yield_calls;
unsigned int open_cfw_test_mram_update_yield_result;
unsigned int open_cfw_test_mram_update_levels[
    OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_update_level_count;
unsigned int open_cfw_test_mram_update_level_index;
open_cfw_mram_update_uintptr open_cfw_test_mram_update_log_records[
    OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_update_log_count;
open_cfw_mram_update_uintptr open_cfw_test_mram_update_trace_records[
    OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_update_trace_count;

static void open_cfw_test_mram_update_order_append(unsigned int event)
{
    if (
        open_cfw_test_mram_update_order_count
        < OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
    ) {
        open_cfw_test_mram_update_order[
            open_cfw_test_mram_update_order_count
        ] = event;
    }
    ++open_cfw_test_mram_update_order_count;
}

void open_cfw_test_mram_update_reset(void)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT;
        ++index
    ) {
        open_cfw_test_mram_update_order[index] = 0U;
        open_cfw_test_mram_update_levels[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_mram_update_program_results[index] = 0U;
        open_cfw_test_mram_update_program_keys[index] = 0U;
        open_cfw_test_mram_update_program_sources[index] = 0U;
        open_cfw_test_mram_update_program_destinations[index] = 0U;
        open_cfw_test_mram_update_program_counts[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
                * OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_update_log_records[index] = 0U;
        open_cfw_test_mram_update_trace_records[index] = 0U;
    }

    open_cfw_test_mram_update_order_count = 0U;
    open_cfw_test_mram_update_cache_calls = 0U;
    open_cfw_test_mram_update_cache_range = 0U;
    open_cfw_test_mram_update_cache_all = 0U;
    open_cfw_test_mram_update_program_calls = 0U;
    open_cfw_test_mram_update_exception_calls = 0U;
    open_cfw_test_mram_update_exception_value = 0U;
    open_cfw_test_mram_update_yield_calls = 0U;
    open_cfw_test_mram_update_yield_result = 0U;
    open_cfw_test_mram_update_level_count = 0U;
    open_cfw_test_mram_update_level_index = 0U;
    open_cfw_test_mram_update_log_count = 0U;
    open_cfw_test_mram_update_trace_count = 0U;
}

unsigned int open_cfw_test_mram_update_cache_invalidate(
    unsigned int range,
    unsigned int all
)
{
    open_cfw_test_mram_update_order_append(1U);
    ++open_cfw_test_mram_update_cache_calls;
    open_cfw_test_mram_update_cache_range = range;
    open_cfw_test_mram_update_cache_all = all;
    return 0U;
}

unsigned int open_cfw_test_mram_update_program(
    unsigned int key,
    const unsigned int *source,
    unsigned int *destination,
    unsigned int count
)
{
    unsigned int call = open_cfw_test_mram_update_program_calls;

    open_cfw_test_mram_update_order_append(call == 0U ? 2U : 5U);
    if (call < 2U) {
        open_cfw_test_mram_update_program_keys[call] = key;
        open_cfw_test_mram_update_program_sources[call] =
            (open_cfw_mram_update_uintptr)source;
        open_cfw_test_mram_update_program_destinations[call] =
            (open_cfw_mram_update_uintptr)destination;
        open_cfw_test_mram_update_program_counts[call] = count;
    }
    ++open_cfw_test_mram_update_program_calls;
    return call < 2U
        ? open_cfw_test_mram_update_program_results[call]
        : 0U;
}

unsigned int open_cfw_test_mram_update_exception_number(void)
{
    open_cfw_test_mram_update_order_append(3U);
    ++open_cfw_test_mram_update_exception_calls;
    return open_cfw_test_mram_update_exception_value;
}

unsigned int open_cfw_test_mram_update_yield(void)
{
    open_cfw_test_mram_update_order_append(4U);
    ++open_cfw_test_mram_update_yield_calls;
    return open_cfw_test_mram_update_yield_result;
}

unsigned int open_cfw_test_mram_update_log_level(void)
{
    unsigned int result = 0U;

    open_cfw_test_mram_update_order_append(6U);
    if (
        open_cfw_test_mram_update_level_index
        < open_cfw_test_mram_update_level_count
    ) {
        result = open_cfw_test_mram_update_levels[
            open_cfw_test_mram_update_level_index
        ];
    }
    ++open_cfw_test_mram_update_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_update_argument_count(
    open_cfw_mram_update_uintptr identity
)
{
    if (
        identity == 0x007090E4U
        || identity == 0x006F17B4U
    ) {
        return 2U;
    }
    if (
        identity == 0x006E622CU
        || identity == 0x006DF548U
    ) {
        return 3U;
    }
    return 0U;
}

void open_cfw_test_mram_update_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_update_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_update_order_append(7U);
    if (
        open_cfw_test_mram_update_log_count
        >= OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_update_log_count;
        return;
    }
    output = &open_cfw_test_mram_update_log_records[
        open_cfw_test_mram_update_log_count
        * OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH
    ];
    output[0] = severity;
    output[1] = (open_cfw_mram_update_uintptr)module;
    output[2] = (open_cfw_mram_update_uintptr)file;
    output[3] = (open_cfw_mram_update_uintptr)function;
    output[4] = line;
    output[5] = (open_cfw_mram_update_uintptr)identity;
    count = open_cfw_test_mram_update_argument_count(output[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        output[6U + index] =
            (open_cfw_mram_update_uintptr)va_arg(
                arguments,
                unsigned int
            );
    }
    va_end(arguments);
    ++open_cfw_test_mram_update_log_count;
}

void open_cfw_test_mram_update_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_mram_update_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    open_cfw_test_mram_update_order_append(8U);
    if (
        open_cfw_test_mram_update_trace_count
        >= OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_COUNT
    ) {
        ++open_cfw_test_mram_update_trace_count;
        return;
    }
    output = &open_cfw_test_mram_update_trace_records[
        open_cfw_test_mram_update_trace_count
        * OPEN_CFW_TEST_MRAM_UPDATE_CAPTURE_WIDTH
    ];
    output[0] = event;
    output[1] = (open_cfw_mram_update_uintptr)identity;
    output[2] =
        (open_cfw_mram_update_uintptr)duplicate_identity;
    count = open_cfw_test_mram_update_argument_count(output[1]);
    va_start(arguments, duplicate_identity);
    for (index = 0U; index < count; ++index) {
        output[3U + index] =
            (open_cfw_mram_update_uintptr)va_arg(
                arguments,
                unsigned int
            );
    }
    va_end(arguments);
    ++open_cfw_test_mram_update_trace_count;
}
