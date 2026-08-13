/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo MRAM persistence helpers.
 */

#include <stdarg.h>

unsigned int open_cfw_test_mram_cache_invalidate(void);
unsigned int open_cfw_test_mram_irq_disable(void);
void open_cfw_test_mram_primask_restore(unsigned int);
unsigned int open_cfw_test_mram_program(
    unsigned int,
    const unsigned int *,
    unsigned int *,
    unsigned int
);
unsigned int open_cfw_test_mram_log_level(void);
void open_cfw_test_mram_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_mram_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
void open_cfw_test_mram_hex_dump(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

unsigned short open_cfw_test_mram_zero_size;
unsigned char open_cfw_test_mram_zero_buffer[64];
unsigned int open_cfw_test_mram_flag_record[4];
unsigned int open_cfw_test_mram_flag_template[4];

#define OPEN_CFW_MRAM_ZERO_SIZE open_cfw_test_mram_zero_size
#define OPEN_CFW_MRAM_ZERO_BUFFER open_cfw_test_mram_zero_buffer
#define OPEN_CFW_MRAM_ZERO_DESTINATION \
    ((unsigned int *)0x007FF000U)
#define OPEN_CFW_MRAM_FLAG_RECORD open_cfw_test_mram_flag_record
#define OPEN_CFW_MRAM_FLAG_TEMPLATE open_cfw_test_mram_flag_template
#define OPEN_CFW_MRAM_CACHE_INVALIDATE() \
    open_cfw_test_mram_cache_invalidate()
#define OPEN_CFW_MRAM_IRQ_DISABLE() open_cfw_test_mram_irq_disable()
#define OPEN_CFW_MRAM_PRIMASK_RESTORE(value) \
    open_cfw_test_mram_primask_restore(value)
#define OPEN_CFW_MRAM_PROGRAM(key, source, destination, count) \
    open_cfw_test_mram_program((key), (source), (destination), (count))
#define OPEN_CFW_MRAM_LOG_LEVEL() open_cfw_test_mram_log_level()
#define OPEN_CFW_MRAM_LOG(...) open_cfw_test_mram_log(__VA_ARGS__)
#define OPEN_CFW_MRAM_TRACE(...) open_cfw_test_mram_trace(__VA_ARGS__)
#define OPEN_CFW_MRAM_HEX_DUMP(...) \
    open_cfw_test_mram_hex_dump(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/mram_persistence.c"

#define OPEN_CFW_TEST_MRAM_RECORD_WIDTH 12U

unsigned int open_cfw_test_mram_cache_calls;
unsigned int open_cfw_test_mram_disable_calls;
unsigned int open_cfw_test_mram_disable_result;
unsigned int open_cfw_test_mram_restore_calls;
unsigned int open_cfw_test_mram_restore_value;
unsigned int open_cfw_test_mram_program_calls;
unsigned int open_cfw_test_mram_program_result;
unsigned int open_cfw_test_mram_program_key;
open_cfw_mram_uintptr open_cfw_test_mram_program_source;
open_cfw_mram_uintptr open_cfw_test_mram_program_destination;
unsigned int open_cfw_test_mram_program_count;
unsigned int open_cfw_test_mram_program_words[4];
unsigned int open_cfw_test_mram_hex_calls;
open_cfw_mram_uintptr open_cfw_test_mram_hex_identity;
unsigned int open_cfw_test_mram_hex_width;
open_cfw_mram_uintptr open_cfw_test_mram_hex_pointer;
unsigned int open_cfw_test_mram_hex_size;
unsigned int open_cfw_test_mram_levels[64];
unsigned int open_cfw_test_mram_level_count;
unsigned int open_cfw_test_mram_level_index;
open_cfw_mram_uintptr open_cfw_test_mram_log_records[
    16U * OPEN_CFW_TEST_MRAM_RECORD_WIDTH
];
unsigned int open_cfw_test_mram_log_count;
open_cfw_mram_uintptr open_cfw_test_mram_trace_records[
    16U * OPEN_CFW_TEST_MRAM_RECORD_WIDTH
];
unsigned int open_cfw_test_mram_trace_count;

void open_cfw_test_mram_reset(void)
{
    unsigned int index;

    open_cfw_test_mram_zero_size = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_mram_zero_buffer[index] = 0U;
        open_cfw_test_mram_levels[index] = 0U;
    }
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_mram_flag_record[index] = 0U;
        open_cfw_test_mram_flag_template[index] = 0U;
        open_cfw_test_mram_program_words[index] = 0U;
    }
    for (
        index = 0U;
        index < 16U * OPEN_CFW_TEST_MRAM_RECORD_WIDTH;
        ++index
    ) {
        open_cfw_test_mram_log_records[index] = 0U;
        open_cfw_test_mram_trace_records[index] = 0U;
    }

    open_cfw_test_mram_cache_calls = 0U;
    open_cfw_test_mram_disable_calls = 0U;
    open_cfw_test_mram_disable_result = 0U;
    open_cfw_test_mram_restore_calls = 0U;
    open_cfw_test_mram_restore_value = 0U;
    open_cfw_test_mram_program_calls = 0U;
    open_cfw_test_mram_program_result = 0U;
    open_cfw_test_mram_program_key = 0U;
    open_cfw_test_mram_program_source = 0U;
    open_cfw_test_mram_program_destination = 0U;
    open_cfw_test_mram_program_count = 0U;
    open_cfw_test_mram_hex_calls = 0U;
    open_cfw_test_mram_hex_identity = 0U;
    open_cfw_test_mram_hex_width = 0U;
    open_cfw_test_mram_hex_pointer = 0U;
    open_cfw_test_mram_hex_size = 0U;
    open_cfw_test_mram_level_count = 0U;
    open_cfw_test_mram_level_index = 0U;
    open_cfw_test_mram_log_count = 0U;
    open_cfw_test_mram_trace_count = 0U;
}

unsigned int open_cfw_test_mram_cache_invalidate(void)
{
    ++open_cfw_test_mram_cache_calls;
    return 0U;
}

unsigned int open_cfw_test_mram_irq_disable(void)
{
    ++open_cfw_test_mram_disable_calls;
    return open_cfw_test_mram_disable_result;
}

void open_cfw_test_mram_primask_restore(unsigned int value)
{
    ++open_cfw_test_mram_restore_calls;
    open_cfw_test_mram_restore_value = value;
}

unsigned int open_cfw_test_mram_program(
    unsigned int key,
    const unsigned int *source,
    unsigned int *destination,
    unsigned int count
)
{
    unsigned int index;

    ++open_cfw_test_mram_program_calls;
    open_cfw_test_mram_program_key = key;
    open_cfw_test_mram_program_source =
        (open_cfw_mram_uintptr)source;
    open_cfw_test_mram_program_destination =
        (open_cfw_mram_uintptr)destination;
    open_cfw_test_mram_program_count = count;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_mram_program_words[index] =
            index < count ? source[index] : 0U;
    }
    return open_cfw_test_mram_program_result;
}

unsigned int open_cfw_test_mram_log_level(void)
{
    unsigned int result = 0U;

    if (
        open_cfw_test_mram_level_index
        < open_cfw_test_mram_level_count
    ) {
        result =
            open_cfw_test_mram_levels[open_cfw_test_mram_level_index];
    }
    ++open_cfw_test_mram_level_index;
    return result;
}

static unsigned int open_cfw_test_mram_argument_count(
    open_cfw_mram_uintptr identity
)
{
    if (
        identity == 0x0073C038U
        || identity == 0x0073C064U
        || identity == 0x00726CB8U
        || identity == 0x0071BEE8U
    ) {
        return 1U;
    }
    if (
        identity == 0x0073C090U
        || identity == 0x00751D88U
        || identity == 0x0071BF20U
        || identity == 0x007317E4U
    ) {
        return 2U;
    }
    return 0U;
}

static int open_cfw_test_mram_first_argument_is_pointer(
    open_cfw_mram_uintptr identity
)
{
    return (
        identity == 0x00751D88U
        || identity == 0x007317E4U
    );
}

void open_cfw_test_mram_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_mram_uintptr *record;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (open_cfw_test_mram_log_count >= 16U) {
        ++open_cfw_test_mram_log_count;
        return;
    }
    record = &open_cfw_test_mram_log_records[
        open_cfw_test_mram_log_count * OPEN_CFW_TEST_MRAM_RECORD_WIDTH
    ];
    record[0] = severity;
    record[1] = (open_cfw_mram_uintptr)module;
    record[2] = (open_cfw_mram_uintptr)file;
    record[3] = (open_cfw_mram_uintptr)function;
    record[4] = line;
    record[5] = (open_cfw_mram_uintptr)identity;
    count = open_cfw_test_mram_argument_count(record[5]);
    va_start(arguments, identity);
    for (index = 0U; index < count; ++index) {
        if (
            index == 0U
            && open_cfw_test_mram_first_argument_is_pointer(record[5])
        ) {
            record[6U + index] = (open_cfw_mram_uintptr)va_arg(
                arguments,
                unsigned int *
            );
        }
        else {
            record[6U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
    ++open_cfw_test_mram_log_count;
}

void open_cfw_test_mram_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    open_cfw_mram_uintptr *record;
    unsigned int count;
    unsigned int index;
    va_list arguments;

    if (open_cfw_test_mram_trace_count >= 16U) {
        ++open_cfw_test_mram_trace_count;
        return;
    }
    record = &open_cfw_test_mram_trace_records[
        open_cfw_test_mram_trace_count
        * OPEN_CFW_TEST_MRAM_RECORD_WIDTH
    ];
    record[0] = event;
    record[1] = (open_cfw_mram_uintptr)identity;
    record[2] = (open_cfw_mram_uintptr)duplicate_identity;
    count = open_cfw_test_mram_argument_count(record[1]);
    va_start(arguments, duplicate_identity);
    for (index = 0U; index < count; ++index) {
        if (
            index == 0U
            && open_cfw_test_mram_first_argument_is_pointer(record[1])
        ) {
            record[3U + index] = (open_cfw_mram_uintptr)va_arg(
                arguments,
                unsigned int *
            );
        }
        else {
            record[3U + index] = va_arg(arguments, unsigned int);
        }
    }
    va_end(arguments);
    ++open_cfw_test_mram_trace_count;
}

void open_cfw_test_mram_hex_dump(
    const void *identity,
    unsigned int width,
    const void *pointer,
    unsigned int size
)
{
    ++open_cfw_test_mram_hex_calls;
    open_cfw_test_mram_hex_identity = (open_cfw_mram_uintptr)identity;
    open_cfw_test_mram_hex_width = width;
    open_cfw_test_mram_hex_pointer = (open_cfw_mram_uintptr)pointer;
    open_cfw_test_mram_hex_size = size;
}
