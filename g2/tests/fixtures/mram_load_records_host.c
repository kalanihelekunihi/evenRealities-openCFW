/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Apollo protected-MRAM record loader.
 */

#include <stdarg.h>

#define OPEN_CFW_TEST_MRAM_LOAD_RECORD_COUNT 10U
#define OPEN_CFW_TEST_MRAM_LOAD_NVM_STRIDE 0x100U
#define OPEN_CFW_TEST_MRAM_LOAD_RAM_STRIDE 0xC8U
#define OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT 96U
#define OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH 16U

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);
unsigned int open_cfw_test_mram_load_cache_invalidate(
    unsigned int,
    unsigned int
);
void open_cfw_test_mram_load_persist(unsigned char *);
unsigned int open_cfw_test_mram_load_log_level(void);
void open_cfw_test_mram_load_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_load_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_load_hex(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

unsigned char open_cfw_test_mram_load_nvm[
    OPEN_CFW_TEST_MRAM_LOAD_RECORD_COUNT
    * OPEN_CFW_TEST_MRAM_LOAD_NVM_STRIDE
];
unsigned char open_cfw_test_mram_load_zero_key[16];

#define OPEN_CFW_MRAM_LOAD_NVM_BASE open_cfw_test_mram_load_nvm
#define OPEN_CFW_MRAM_LOAD_ZERO_KEY open_cfw_test_mram_load_zero_key
#define OPEN_CFW_MRAM_LOAD_CACHE_INVALIDATE(range, all) \
    open_cfw_test_mram_load_cache_invalidate((range), (all))
#define OPEN_CFW_MRAM_LOAD_PERSIST(record) \
    open_cfw_test_mram_load_persist(record)
#define OPEN_CFW_MRAM_LOAD_LOG_LEVEL() \
    open_cfw_test_mram_load_log_level()
#define OPEN_CFW_MRAM_LOAD_LOG(...) \
    open_cfw_test_mram_load_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_LOAD_TRACE(...) \
    open_cfw_test_mram_load_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_LOAD_HEX(...) \
    open_cfw_test_mram_load_hex(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_load_records.c"

unsigned int open_cfw_test_mram_load_cache_calls;
unsigned int open_cfw_test_mram_load_cache_range;
unsigned int open_cfw_test_mram_load_cache_all;
unsigned int open_cfw_test_mram_load_compare_calls;
unsigned char open_cfw_test_mram_load_compare_values[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT * 16U
];
open_cfw_mram_load_uintptr open_cfw_test_mram_load_compare_keys[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_load_compare_sizes[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_load_persist_calls;
open_cfw_mram_load_uintptr open_cfw_test_mram_load_persist_pointers[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
];
unsigned char open_cfw_test_mram_load_persist_records[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_LOAD_RAM_STRIDE
];
unsigned int open_cfw_test_mram_load_persist_mutate;
unsigned int open_cfw_test_mram_load_persist_mutate_mask;
unsigned int open_cfw_test_mram_load_levels[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
];
unsigned int open_cfw_test_mram_load_level_count;
unsigned int open_cfw_test_mram_load_level_index;
open_cfw_mram_load_uintptr open_cfw_test_mram_load_log_records[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_load_log_count;
open_cfw_mram_load_uintptr open_cfw_test_mram_load_trace_records[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
    * OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH
];
unsigned int open_cfw_test_mram_load_trace_count;
open_cfw_mram_load_uintptr open_cfw_test_mram_load_hex_records[
    OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT * 4U
];
unsigned int open_cfw_test_mram_load_hex_count;

void open_cfw_test_mram_load_reset(void)
{
    unsigned int index;

    for (
        index = 0U;
        index < sizeof(open_cfw_test_mram_load_nvm);
        ++index
    ) {
        open_cfw_test_mram_load_nvm[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_mram_load_zero_key[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT * 16U;
        ++index
    ) {
        open_cfw_test_mram_load_compare_values[index] = 0U;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT;
        ++index
    ) {
        open_cfw_test_mram_load_compare_keys[index] = 0U;
        open_cfw_test_mram_load_compare_sizes[index] = 0U;
        open_cfw_test_mram_load_persist_pointers[index] = 0U;
        open_cfw_test_mram_load_levels[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
                * OPEN_CFW_TEST_MRAM_LOAD_RAM_STRIDE;
        ++index
    ) {
        open_cfw_test_mram_load_persist_records[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT
                * OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_load_log_records[index] = 0U;
        open_cfw_test_mram_load_trace_records[index] = 0U;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT * 4U;
        ++index
    ) {
        open_cfw_test_mram_load_hex_records[index] = 0U;
    }

    open_cfw_test_mram_load_cache_calls = 0U;
    open_cfw_test_mram_load_cache_range = 0U;
    open_cfw_test_mram_load_cache_all = 0U;
    open_cfw_test_mram_load_compare_calls = 0U;
    open_cfw_test_mram_load_persist_calls = 0U;
    open_cfw_test_mram_load_persist_mutate = 0U;
    open_cfw_test_mram_load_persist_mutate_mask = 0U;
    open_cfw_test_mram_load_level_count = 0U;
    open_cfw_test_mram_load_level_index = 0U;
    open_cfw_test_mram_load_log_count = 0U;
    open_cfw_test_mram_load_trace_count = 0U;
    open_cfw_test_mram_load_hex_count = 0U;
}

unsigned int open_cfw_test_mram_load_cache_invalidate(
    unsigned int range,
    unsigned int all
)
{
    ++open_cfw_test_mram_load_cache_calls;
    open_cfw_test_mram_load_cache_range = range;
    open_cfw_test_mram_load_cache_all = all;
    return 0U;
}

int open_cfw_memory_compare(
    const void *left_value,
    const void *right_value,
    unsigned int size
)
{
    const unsigned char *left =
        (const unsigned char *)left_value;
    const unsigned char *right =
        (const unsigned char *)right_value;
    unsigned int call = open_cfw_test_mram_load_compare_calls;
    unsigned int index;

    if (call < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT) {
        for (index = 0U; index < 16U; ++index) {
            open_cfw_test_mram_load_compare_values[
                call * 16U + index
            ] = index < size ? left[index] : 0U;
        }
        open_cfw_test_mram_load_compare_keys[call] =
            (open_cfw_mram_load_uintptr)right;
        open_cfw_test_mram_load_compare_sizes[call] = size;
    }
    ++open_cfw_test_mram_load_compare_calls;
    for (index = 0U; index < size; ++index) {
        if (left[index] != right[index]) {
            return (int)left[index] - (int)right[index];
        }
    }
    return 0;
}

void open_cfw_test_mram_load_persist(unsigned char *record)
{
    unsigned int call = open_cfw_test_mram_load_persist_calls;
    unsigned int index;

    if (call < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT) {
        open_cfw_test_mram_load_persist_pointers[call] =
            (open_cfw_mram_load_uintptr)record;
        for (
            index = 0U;
            index < OPEN_CFW_TEST_MRAM_LOAD_RAM_STRIDE;
            ++index
        ) {
            open_cfw_test_mram_load_persist_records[
                call * OPEN_CFW_TEST_MRAM_LOAD_RAM_STRIDE + index
            ] = record[index];
        }
    }
    ++open_cfw_test_mram_load_persist_calls;
    if (open_cfw_test_mram_load_persist_mutate != 0U) {
        record[0x2EU] =
            (unsigned char)open_cfw_test_mram_load_persist_mutate_mask;
    }
}

unsigned int open_cfw_test_mram_load_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_load_level_index
        < open_cfw_test_mram_load_level_count
    ) {
        result = open_cfw_test_mram_load_levels[
            open_cfw_test_mram_load_level_index
        ];
    }
    ++open_cfw_test_mram_load_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_load_argument_count(
    open_cfw_mram_load_uintptr identity
)
{
    if (
        identity == 0x00708FE4U
        || identity == 0x006F16D0U
    ) {
        return 0U;
    }
    if (
        identity == 0x00709064U
        || identity == 0x006F1768U
        || identity == 0x007090A4U
        || identity == 0x006F8294U
    ) {
        return 1U;
    }
    if (
        identity == 0x006D9E40U
        || identity == 0x006A65B4U
        || identity == 0x00709024U
        || identity == 0x006F171CU
    ) {
        return 2U;
    }
    if (
        identity == 0x006E61D8U
        || identity == 0x006DF4ECU
    ) {
        return 3U;
    }
    if (
        identity == 0x006A68C4U
        || identity == 0x006D5E58U
    ) {
        return 9U;
    }
    return 0U;
}

void open_cfw_test_mram_load_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_load_log_count;

    if (call < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT) {
        open_cfw_mram_load_uintptr *capture =
            &open_cfw_test_mram_load_log_records[
                call * OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH
            ];
        unsigned int count =
            open_cfw_test_mram_load_argument_count(
                (open_cfw_mram_load_uintptr)identity
            );
        unsigned int index;
        va_list arguments;

        capture[0] = severity;
        capture[1] = (open_cfw_mram_load_uintptr)module;
        capture[2] = (open_cfw_mram_load_uintptr)file;
        capture[3] = (open_cfw_mram_load_uintptr)function;
        capture[4] = line;
        capture[5] = (open_cfw_mram_load_uintptr)identity;
        va_start(arguments, identity);
        for (index = 0U; index < count; ++index) {
            capture[6U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_load_log_count;
}

void open_cfw_test_mram_load_trace(
    unsigned int event,
    const void *first_identity,
    const void *second_identity,
    ...
)
{
    unsigned int call = open_cfw_test_mram_load_trace_count;

    if (call < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT) {
        open_cfw_mram_load_uintptr *capture =
            &open_cfw_test_mram_load_trace_records[
                call * OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_WIDTH
            ];
        unsigned int count =
            open_cfw_test_mram_load_argument_count(
                (open_cfw_mram_load_uintptr)first_identity
            );
        unsigned int index;
        va_list arguments;

        capture[0] = event;
        capture[1] = (open_cfw_mram_load_uintptr)first_identity;
        capture[2] = (open_cfw_mram_load_uintptr)second_identity;
        va_start(arguments, second_identity);
        for (index = 0U; index < count; ++index) {
            capture[3U + index] = va_arg(arguments, unsigned int);
        }
        va_end(arguments);
    }
    ++open_cfw_test_mram_load_trace_count;
}

void open_cfw_test_mram_load_hex(
    const void *identity,
    unsigned int width,
    const void *pointer,
    unsigned int size
)
{
    unsigned int call = open_cfw_test_mram_load_hex_count;

    if (call < OPEN_CFW_TEST_MRAM_LOAD_CAPTURE_COUNT) {
        open_cfw_mram_load_uintptr *capture =
            &open_cfw_test_mram_load_hex_records[call * 4U];

        capture[0] = (open_cfw_mram_load_uintptr)identity;
        capture[1] = width;
        capture[2] = (open_cfw_mram_load_uintptr)pointer;
        capture[3] = size;
    }
    ++open_cfw_test_mram_load_hex_count;
}
