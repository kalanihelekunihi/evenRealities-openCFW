/*
 * SPDX-License-Identifier: MIT
 *
 * Host seam oracle for the nonproduction Apollo-main EasyLogger output
 * candidate. It records observable ordering without replacing candidate logic.
 */

#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct open_cfw_easylogger_output_logger;

static uint32_t open_cfw_test_easylogger_output_read_ipsr(void);
static struct open_cfw_easylogger_output_logger *
open_cfw_test_easylogger_output_get_logger(void);
static char *open_cfw_test_easylogger_output_get_buffer(void);
static void open_cfw_test_easylogger_output_assert_wait(void);
static const char *open_cfw_test_easylogger_output_get_time(void);
static const char *open_cfw_test_easylogger_output_get_process(void);
static const char *open_cfw_test_easylogger_output_get_thread(void);
static int open_cfw_test_easylogger_output_snprintf(
    char *buffer,
    uint32_t size,
    const char *format,
    ...
);
static int open_cfw_test_easylogger_output_vsnprintf(
    char *buffer,
    uint32_t size,
    const char *format,
    va_list arguments
);

static char open_cfw_test_easylogger_output_buffer[1025];
static void (*open_cfw_test_easylogger_output_assert_hook)(
    const char *,
    const char *,
    uint32_t
);

#define OPEN_CFW_EASYLOGGER_OUTPUT_READ_IPSR() \
    open_cfw_test_easylogger_output_read_ipsr()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_LOGGER() \
    open_cfw_test_easylogger_output_get_logger()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_BUFFER() \
    open_cfw_test_easylogger_output_get_buffer()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_ASSERT_HOOK() \
    open_cfw_test_easylogger_output_assert_hook
#define OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_SOURCE_PATH \
    "G2/third_party/EasyLogger-master/easylogger/src/elog.c"
#define OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT() \
    open_cfw_test_easylogger_output_assert_wait()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_TIME() \
    open_cfw_test_easylogger_output_get_time()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_PROCESS() \
    open_cfw_test_easylogger_output_get_process()
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_THREAD() \
    open_cfw_test_easylogger_output_get_thread()
#define OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF(buffer, size, format, value) \
    open_cfw_test_easylogger_output_snprintf( \
        (buffer), (size), (format), (value) \
    )
#define OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF( \
    buffer, size, format, arguments \
) \
    open_cfw_test_easylogger_output_vsnprintf( \
        (buffer), (size), (format), (arguments) \
    )

#include "../../components/shared/easylogger/runtime_easylogger_output_candidate.c"

enum {
    OPEN_CFW_TEST_ELOG_EVENT_IPSR = 1U,
    OPEN_CFW_TEST_ELOG_EVENT_STATE = 2U,
    OPEN_CFW_TEST_ELOG_EVENT_TAG_LEVEL = 3U,
    OPEN_CFW_TEST_ELOG_EVENT_LOCK = 4U,
    OPEN_CFW_TEST_ELOG_EVENT_BUFFER = 5U,
    OPEN_CFW_TEST_ELOG_EVENT_APPEND = 6U,
    OPEN_CFW_TEST_ELOG_EVENT_TIME = 7U,
    OPEN_CFW_TEST_ELOG_EVENT_PROCESS = 8U,
    OPEN_CFW_TEST_ELOG_EVENT_THREAD = 9U,
    OPEN_CFW_TEST_ELOG_EVENT_LINE_FORMAT = 10U,
    OPEN_CFW_TEST_ELOG_EVENT_MESSAGE_FORMAT = 11U,
    OPEN_CFW_TEST_ELOG_EVENT_SINK = 12U,
    OPEN_CFW_TEST_ELOG_EVENT_UNLOCK = 13U,
    OPEN_CFW_TEST_ELOG_EVENT_ASSERT = 14U,
    OPEN_CFW_TEST_ELOG_EVENT_WAIT = 15U,
    OPEN_CFW_TEST_ELOG_EVENT_CAPACITY = 256U
};

static struct open_cfw_easylogger_output_logger
    open_cfw_test_easylogger_output_logger;
static uint32_t open_cfw_test_easylogger_output_ipsr;
static const char *open_cfw_test_easylogger_output_time = "TIME";
static const char *open_cfw_test_easylogger_output_process = "PROCESS";
static const char *open_cfw_test_easylogger_output_thread = "THREAD";
static uint32_t open_cfw_test_easylogger_output_events[
    OPEN_CFW_TEST_ELOG_EVENT_CAPACITY
];
static uint32_t open_cfw_test_easylogger_output_event_count_value;
static uint32_t open_cfw_test_easylogger_output_lock_depth;
static uint32_t open_cfw_test_easylogger_output_force_format;
static int32_t open_cfw_test_easylogger_output_forced_result;
static uint32_t open_cfw_test_easylogger_output_forced_write;
static uint8_t open_cfw_test_easylogger_output_forced_byte;
static char open_cfw_test_easylogger_output_sink[1025];
static uint32_t open_cfw_test_easylogger_output_sink_length_value;
static uint32_t open_cfw_test_easylogger_output_sink_level_value;
static uint32_t open_cfw_test_easylogger_output_sink_calls_value;
static uint32_t open_cfw_test_easylogger_output_assert_calls_value;
static uint32_t open_cfw_test_easylogger_output_assert_line_value;
static char open_cfw_test_easylogger_output_assert_expression[64];
static char open_cfw_test_easylogger_output_assert_function[32];

static void open_cfw_test_easylogger_output_record_event(uint32_t event)
{
    if (
        open_cfw_test_easylogger_output_event_count_value <
            OPEN_CFW_TEST_ELOG_EVENT_CAPACITY
    ) {
        open_cfw_test_easylogger_output_events[
            open_cfw_test_easylogger_output_event_count_value
        ] = event;
    }
    open_cfw_test_easylogger_output_event_count_value++;
}

static uint32_t open_cfw_test_easylogger_output_read_ipsr(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_IPSR);
    return open_cfw_test_easylogger_output_ipsr;
}

static struct open_cfw_easylogger_output_logger *
open_cfw_test_easylogger_output_get_logger(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_STATE);
    return &open_cfw_test_easylogger_output_logger;
}

static char *open_cfw_test_easylogger_output_get_buffer(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_BUFFER);
    return open_cfw_test_easylogger_output_buffer;
}

static void open_cfw_test_easylogger_output_returning_assert_hook(
    const char *expression,
    const char *function,
    uint32_t line
)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_ASSERT);
    open_cfw_test_easylogger_output_assert_calls_value++;
    open_cfw_test_easylogger_output_assert_line_value = line;
    (void)snprintf(
        open_cfw_test_easylogger_output_assert_expression,
        sizeof(open_cfw_test_easylogger_output_assert_expression),
        "%s",
        expression
    );
    (void)snprintf(
        open_cfw_test_easylogger_output_assert_function,
        sizeof(open_cfw_test_easylogger_output_assert_function),
        "%s",
        function
    );
}

static void open_cfw_test_easylogger_output_assert_wait(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_WAIT);
}

static const char *open_cfw_test_easylogger_output_get_time(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_TIME);
    return open_cfw_test_easylogger_output_time;
}

static const char *open_cfw_test_easylogger_output_get_process(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_PROCESS);
    return open_cfw_test_easylogger_output_process;
}

static const char *open_cfw_test_easylogger_output_get_thread(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_THREAD);
    return open_cfw_test_easylogger_output_thread;
}

static int open_cfw_test_easylogger_output_snprintf(
    char *buffer,
    uint32_t size,
    const char *format,
    ...
)
{
    int result;
    va_list arguments;

    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_LINE_FORMAT
    );
    va_start(arguments, format);
    result = vsnprintf(buffer, (size_t)size, format, arguments);
    va_end(arguments);
    return result;
}

static int open_cfw_test_easylogger_output_vsnprintf(
    char *buffer,
    uint32_t size,
    const char *format,
    va_list arguments
)
{
    uint32_t write;

    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_MESSAGE_FORMAT
    );
    if (open_cfw_test_easylogger_output_force_format == 0U) {
        return vsnprintf(buffer, (size_t)size, format, arguments);
    }

    write = open_cfw_test_easylogger_output_forced_write;
    if (size == 0U) {
        write = 0U;
    } else if (write >= size) {
        write = size - 1U;
    }
    if (write != 0U) {
        memset(
            buffer,
            (int)open_cfw_test_easylogger_output_forced_byte,
            write
        );
    }
    if (size != 0U) {
        buffer[write] = '\0';
    }
    return (int)open_cfw_test_easylogger_output_forced_result;
}

void open_cfw_easylogger_output_lock(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_LOCK);
    open_cfw_test_easylogger_output_lock_depth++;
    open_cfw_test_easylogger_output_logger
        .output_is_locked_before_disable = 1U;
}

void open_cfw_easylogger_output_unlock(void)
{
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_UNLOCK);
    if (open_cfw_test_easylogger_output_lock_depth != 0U) {
        open_cfw_test_easylogger_output_lock_depth--;
    }
    open_cfw_test_easylogger_output_logger
        .output_is_locked_before_disable = 0U;
}

static uint8_t open_cfw_test_easylogger_output_tags_equal(
    const char *left,
    const char *right
)
{
    uint32_t index;
    for (index = 0U; index < 30U; index++) {
        uint8_t left_byte = (uint8_t)left[index];
        uint8_t right_byte = (uint8_t)right[index];
        if (left_byte != right_byte) {
            return 0U;
        }
        if (left_byte == 0U) {
            return 1U;
        }
    }
    return 1U;
}

open_cfw_easylogger_output_u8 open_cfw_easylogger_get_filter_tag_level(
    const char *tag
)
{
    uint8_t level = OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_VERBOSE;
    uint32_t index;

    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_TAG_LEVEL
    );
    if (open_cfw_test_easylogger_output_logger.init_ok == 0U) {
        return level;
    }
    open_cfw_easylogger_output_lock();
    for (index = 0U; index < 5U; index++) {
        struct open_cfw_easylogger_output_tag_level *entry =
            &open_cfw_test_easylogger_output_logger
                .filter.tag_level[index];
        if (
            entry->tag_use_flag != 0U &&
            open_cfw_test_easylogger_output_tags_equal(tag, entry->tag) != 0U
        ) {
            level = entry->level;
            break;
        }
    }
    open_cfw_easylogger_output_unlock();
    return level;
}

open_cfw_easylogger_output_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_output_u32 current_length,
    char *destination,
    const char *source
)
{
    const char *source_old = source;

    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_APPEND);
    while (*source != '\0') {
        if (current_length++ < 1024U) {
            *destination++ = *source++;
        } else {
            break;
        }
    }
    return (uint32_t)(source - source_old);
}

open_cfw_easylogger_output_u8 open_cfw_easylogger_get_fmt_enabled(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set
)
{
    return (uint8_t)(
        (open_cfw_test_easylogger_output_logger
            .enabled_format_set[level] & format_set) != 0U
    );
}

open_cfw_easylogger_output_u8
open_cfw_easylogger_get_fmt_used_and_enabled_u32(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set,
    open_cfw_easylogger_output_u32 argument
)
{
    return (uint8_t)(
        argument != 0U &&
        open_cfw_easylogger_get_fmt_enabled(level, format_set) != 0U
    );
}

open_cfw_easylogger_output_u8
open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set,
    const char *argument
)
{
    return (uint8_t)(
        argument != NULL &&
        open_cfw_easylogger_get_fmt_enabled(level, format_set) != 0U
    );
}

void open_cfw_g2_easylogger_async_submit(
    const char *buffer,
    open_cfw_easylogger_output_u32 length,
    open_cfw_easylogger_output_u32 level
)
{
    uint32_t copy = length > 1024U ? 1024U : length;
    open_cfw_test_easylogger_output_record_event(OPEN_CFW_TEST_ELOG_EVENT_SINK);
    open_cfw_test_easylogger_output_sink_calls_value++;
    open_cfw_test_easylogger_output_sink_length_value = length;
    open_cfw_test_easylogger_output_sink_level_value = level;
    memcpy(open_cfw_test_easylogger_output_sink, buffer, copy);
    open_cfw_test_easylogger_output_sink[copy] = '\0';
}

void open_cfw_test_easylogger_output_reset(uint32_t ipsr)
{
    uint32_t level;

    memset(
        &open_cfw_test_easylogger_output_logger,
        0,
        sizeof(open_cfw_test_easylogger_output_logger)
    );
    open_cfw_test_easylogger_output_logger.filter.level = 5U;
    for (level = 0U; level < 6U; level++) {
        open_cfw_test_easylogger_output_logger.enabled_format_set[level] =
            0xFFU;
    }
    open_cfw_test_easylogger_output_logger.init_ok = 1U;
    open_cfw_test_easylogger_output_logger.output_enabled = 1U;
    open_cfw_test_easylogger_output_logger.output_lock_enabled = 1U;
    open_cfw_test_easylogger_output_logger.text_color_enabled = 1U;
    open_cfw_test_easylogger_output_ipsr = ipsr;
    open_cfw_test_easylogger_output_time = "TIME";
    open_cfw_test_easylogger_output_process = "PROCESS";
    open_cfw_test_easylogger_output_thread = "THREAD";
    open_cfw_test_easylogger_output_assert_hook =
        open_cfw_test_easylogger_output_returning_assert_hook;
    open_cfw_test_easylogger_output_event_count_value = 0U;
    open_cfw_test_easylogger_output_lock_depth = 0U;
    open_cfw_test_easylogger_output_force_format = 0U;
    open_cfw_test_easylogger_output_forced_result = 0;
    open_cfw_test_easylogger_output_forced_write = 0U;
    open_cfw_test_easylogger_output_forced_byte = (uint8_t)'X';
    open_cfw_test_easylogger_output_sink_length_value = 0U;
    open_cfw_test_easylogger_output_sink_level_value = 0U;
    open_cfw_test_easylogger_output_sink_calls_value = 0U;
    open_cfw_test_easylogger_output_assert_calls_value = 0U;
    open_cfw_test_easylogger_output_assert_line_value = 0U;
    open_cfw_test_easylogger_output_assert_expression[0] = '\0';
    open_cfw_test_easylogger_output_assert_function[0] = '\0';
    memset(open_cfw_test_easylogger_output_events, 0, sizeof(open_cfw_test_easylogger_output_events));
    memset(open_cfw_test_easylogger_output_buffer, 0xA5, sizeof(open_cfw_test_easylogger_output_buffer));
    memset(open_cfw_test_easylogger_output_sink, 0, sizeof(open_cfw_test_easylogger_output_sink));
}

void open_cfw_test_easylogger_output_set_output_enabled(uint32_t enabled)
{
    open_cfw_test_easylogger_output_logger.output_enabled = (uint8_t)enabled;
}

void open_cfw_test_easylogger_output_set_global_level(uint32_t level)
{
    open_cfw_test_easylogger_output_logger.filter.level = (uint8_t)level;
}

void open_cfw_test_easylogger_output_set_color(uint32_t enabled)
{
    open_cfw_test_easylogger_output_logger.text_color_enabled =
        (uint8_t)enabled;
}

void open_cfw_test_easylogger_output_set_mask(uint32_t level, uint32_t mask)
{
    if (level < 6U) {
        open_cfw_test_easylogger_output_logger.enabled_format_set[level] =
            mask;
    }
}

void open_cfw_test_easylogger_output_set_filter(
    const char *tag,
    const char *keyword
)
{
    (void)snprintf(
        open_cfw_test_easylogger_output_logger.filter.tag,
        sizeof(open_cfw_test_easylogger_output_logger.filter.tag),
        "%s",
        tag
    );
    (void)snprintf(
        open_cfw_test_easylogger_output_logger.filter.keyword,
        sizeof(open_cfw_test_easylogger_output_logger.filter.keyword),
        "%s",
        keyword
    );
}

void open_cfw_test_easylogger_output_set_tag_level(
    uint32_t index,
    const char *tag,
    uint32_t level,
    uint32_t used
)
{
    struct open_cfw_easylogger_output_tag_level *entry;
    if (index >= 5U) {
        return;
    }
    entry = &open_cfw_test_easylogger_output_logger.filter.tag_level[index];
    memset(entry, 0, sizeof(*entry));
    entry->level = (uint8_t)level;
    entry->tag_use_flag = (uint8_t)used;
    (void)snprintf(entry->tag, sizeof(entry->tag), "%s", tag);
}

void open_cfw_test_easylogger_output_set_port_text(
    const char *time,
    const char *process,
    const char *thread
)
{
    open_cfw_test_easylogger_output_time = time;
    open_cfw_test_easylogger_output_process = process;
    open_cfw_test_easylogger_output_thread = thread;
}

void open_cfw_test_easylogger_output_force_formatter(
    uint32_t enabled,
    int32_t result,
    uint32_t write,
    uint32_t byte
)
{
    open_cfw_test_easylogger_output_force_format = enabled;
    open_cfw_test_easylogger_output_forced_result = result;
    open_cfw_test_easylogger_output_forced_write = write;
    open_cfw_test_easylogger_output_forced_byte = (uint8_t)byte;
}

void open_cfw_test_easylogger_output_emit_text(
    uint32_t level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *message
)
{
    open_cfw_easylogger_output(
        (uint8_t)level,
        tag,
        file,
        function,
        line,
        "%s",
        message
    );
}

void open_cfw_test_easylogger_output_emit_integer(
    uint32_t level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    int32_t value
)
{
    open_cfw_easylogger_output(
        (uint8_t)level,
        tag,
        file,
        function,
        line,
        format,
        value
    );
}

void open_cfw_test_easylogger_output_emit_invalid_interrupt(void)
{
    open_cfw_easylogger_output(
        0xFFU,
        (const char *)(uintptr_t)1U,
        (const char *)(uintptr_t)3U,
        (const char *)(uintptr_t)5U,
        7L,
        (const char *)(uintptr_t)9U
    );
}

uint32_t open_cfw_test_easylogger_output_event_count(void)
{
    return open_cfw_test_easylogger_output_event_count_value;
}

uint32_t open_cfw_test_easylogger_output_event(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_ELOG_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_easylogger_output_events[index];
}

const char *open_cfw_test_easylogger_output_sink_data(void)
{
    return open_cfw_test_easylogger_output_sink;
}

uint32_t open_cfw_test_easylogger_output_sink_length(void)
{
    return open_cfw_test_easylogger_output_sink_length_value;
}

uint32_t open_cfw_test_easylogger_output_sink_level(void)
{
    return open_cfw_test_easylogger_output_sink_level_value;
}

uint32_t open_cfw_test_easylogger_output_sink_calls(void)
{
    return open_cfw_test_easylogger_output_sink_calls_value;
}

uint32_t open_cfw_test_easylogger_output_lock_depth_value(void)
{
    return open_cfw_test_easylogger_output_lock_depth;
}

uint32_t open_cfw_test_easylogger_output_assert_calls(void)
{
    return open_cfw_test_easylogger_output_assert_calls_value;
}

uint32_t open_cfw_test_easylogger_output_assert_line(void)
{
    return open_cfw_test_easylogger_output_assert_line_value;
}

const char *open_cfw_test_easylogger_output_assert_expression_value(void)
{
    return open_cfw_test_easylogger_output_assert_expression;
}

const char *open_cfw_test_easylogger_output_assert_function_value(void)
{
    return open_cfw_test_easylogger_output_assert_function;
}
