/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record diagnostic dump.
 */

#include <stdarg.h>

unsigned int open_cfw_test_mram_dump_log_level(void);
void open_cfw_test_mram_dump_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_dump_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_dump_hex(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

const volatile unsigned char *open_cfw_test_mram_dump_base;

#define OPEN_CFW_MRAM_DUMP_BASE open_cfw_test_mram_dump_base
#define OPEN_CFW_MRAM_DUMP_LOG_LEVEL() \
    open_cfw_test_mram_dump_log_level()
#define OPEN_CFW_MRAM_DUMP_LOG(...) \
    open_cfw_test_mram_dump_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_DUMP_TRACE(...) \
    open_cfw_test_mram_dump_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_DUMP_HEX(...) \
    open_cfw_test_mram_dump_hex(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_diagnostic_dump.c"

#define OPEN_CFW_TEST_MRAM_DUMP_WIDTH 12U
#define OPEN_CFW_TEST_MRAM_DUMP_CAPACITY 40U

unsigned char open_cfw_test_mram_dump_records[2U * 0x100U];
unsigned int open_cfw_test_mram_dump_levels[96];
unsigned int open_cfw_test_mram_dump_level_count;
unsigned int open_cfw_test_mram_dump_level_index;
open_cfw_mram_dump_uintptr open_cfw_test_mram_dump_logs[
    OPEN_CFW_TEST_MRAM_DUMP_CAPACITY * OPEN_CFW_TEST_MRAM_DUMP_WIDTH
];
unsigned int open_cfw_test_mram_dump_log_count;
open_cfw_mram_dump_uintptr open_cfw_test_mram_dump_traces[
    OPEN_CFW_TEST_MRAM_DUMP_CAPACITY * OPEN_CFW_TEST_MRAM_DUMP_WIDTH
];
unsigned int open_cfw_test_mram_dump_trace_count;
open_cfw_mram_dump_uintptr open_cfw_test_mram_dump_hexes[4U * 4U];
unsigned int open_cfw_test_mram_dump_hex_count;

static unsigned int open_cfw_test_mram_dump_argument_count(
    open_cfw_mram_dump_uintptr identity
)
{
    switch ((unsigned int)identity) {
        case 0x00769238U:
        case 0x00747634U:
        case 0x00769254U:
        case 0x00747684U:
        case 0x0076928CU:
        case 0x007476FCU:
        case 0x007692C4U:
        case 0x0074774CU:
        case 0x00784F10U:
        case 0x007750D4U:
        case 0x007692E0U:
        case 0x00747774U:
        case 0x007692FCU:
        case 0x0074779CU:
        case 0x00784F40U:
        case 0x00769318U:
        case 0x0075DE30U:
        case 0x0073C0E8U:
            return 0U;
        case 0x00731814U:
        case 0x00712550U:
            return 6U;
        case 0x00775044U:
        case 0x00751DACU:
        case 0x00784F20U:
        case 0x007750ECU:
            return 2U;
        default:
            return 1U;
    }
}

void open_cfw_test_mram_dump_reset(void)
{
    unsigned int index;

    open_cfw_test_mram_dump_base = open_cfw_test_mram_dump_records;
    for (index = 0U; index < 2U * 0x100U; ++index) {
        open_cfw_test_mram_dump_records[index] = 0U;
    }
    for (index = 0U; index < 96U; ++index) {
        open_cfw_test_mram_dump_levels[index] = 0U;
    }
    for (
        index = 0U;
        index
            < OPEN_CFW_TEST_MRAM_DUMP_CAPACITY
                * OPEN_CFW_TEST_MRAM_DUMP_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_dump_logs[index] = 0U;
        open_cfw_test_mram_dump_traces[index] = 0U;
    }
    for (index = 0U; index < 4U * 4U; ++index) {
        open_cfw_test_mram_dump_hexes[index] = 0U;
    }
    open_cfw_test_mram_dump_level_count = 0U;
    open_cfw_test_mram_dump_level_index = 0U;
    open_cfw_test_mram_dump_log_count = 0U;
    open_cfw_test_mram_dump_trace_count = 0U;
    open_cfw_test_mram_dump_hex_count = 0U;
}

unsigned int open_cfw_test_mram_dump_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_dump_level_index
        < open_cfw_test_mram_dump_level_count
    ) {
        result = open_cfw_test_mram_dump_levels[
            open_cfw_test_mram_dump_level_index
        ];
    }
    ++open_cfw_test_mram_dump_level_index;
    return result;
}

void open_cfw_test_mram_dump_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_dump_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (
        open_cfw_test_mram_dump_log_count
        >= OPEN_CFW_TEST_MRAM_DUMP_CAPACITY
    ) {
        ++open_cfw_test_mram_dump_log_count;
        return;
    }
    output = &open_cfw_test_mram_dump_logs[
        open_cfw_test_mram_dump_log_count
        * OPEN_CFW_TEST_MRAM_DUMP_WIDTH
    ];
    output[0] = severity;
    output[1] = (open_cfw_mram_dump_uintptr)module;
    output[2] = (open_cfw_mram_dump_uintptr)file;
    output[3] = (open_cfw_mram_dump_uintptr)function;
    output[4] = line;
    output[5] = (open_cfw_mram_dump_uintptr)identity;
    count = open_cfw_test_mram_dump_argument_count(output[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        output[6U + index] = va_arg(
            arguments,
            open_cfw_mram_dump_uintptr
        );
    }
    va_end(arguments);
    ++open_cfw_test_mram_dump_log_count;
}

void open_cfw_test_mram_dump_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_mram_dump_uintptr *output;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (
        open_cfw_test_mram_dump_trace_count
        >= OPEN_CFW_TEST_MRAM_DUMP_CAPACITY
    ) {
        ++open_cfw_test_mram_dump_trace_count;
        return;
    }
    output = &open_cfw_test_mram_dump_traces[
        open_cfw_test_mram_dump_trace_count
        * OPEN_CFW_TEST_MRAM_DUMP_WIDTH
    ];
    output[0] = event;
    output[1] = (open_cfw_mram_dump_uintptr)identity;
    output[2] = (open_cfw_mram_dump_uintptr)duplicate_identity;
    count = open_cfw_test_mram_dump_argument_count(output[1]);
    va_start(arguments, duplicate_identity);
    for (index = 0U; index < count; ++index) {
        output[3U + index] = va_arg(
            arguments,
            open_cfw_mram_dump_uintptr
        );
    }
    va_end(arguments);
    ++open_cfw_test_mram_dump_trace_count;
}

void open_cfw_test_mram_dump_hex(
    const void *identity,
    unsigned int width,
    const void *pointer,
    unsigned int size
)
{
    open_cfw_mram_dump_uintptr *output;

    if (open_cfw_test_mram_dump_hex_count >= 4U) {
        ++open_cfw_test_mram_dump_hex_count;
        return;
    }
    output = &open_cfw_test_mram_dump_hexes[
        open_cfw_test_mram_dump_hex_count * 4U
    ];
    output[0] = (open_cfw_mram_dump_uintptr)identity;
    output[1] = width;
    output[2] = (open_cfw_mram_dump_uintptr)pointer;
    output[3] = size;
    ++open_cfw_test_mram_dump_hex_count;
}
