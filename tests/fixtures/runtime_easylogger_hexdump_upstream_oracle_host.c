/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle compiled directly from authenticated Armink EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24. Only formatter, copy, port, and
 * async-sink seams are substituted for deterministic observation.
 */

#include <setjmp.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int open_cfw_test_easylogger_hexdump_oracle_snprintf(
    char *buffer,
    size_t size,
    const char *format,
    ...
);
static char *open_cfw_test_easylogger_hexdump_oracle_strncpy(
    char *destination,
    const char *source,
    size_t size
);

#undef snprintf
#undef strncpy
#define snprintf open_cfw_test_easylogger_hexdump_oracle_snprintf
#define strncpy open_cfw_test_easylogger_hexdump_oracle_strncpy
#include "../../third_party/easylogger/src/elog.c"
#include "../../third_party/easylogger/src/elog_utils.c"
#undef snprintf
#undef strncpy

enum {
    OPEN_CFW_TEST_HEXDUMP_EVENT_LOCK = 3U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_HEADER = 5U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_HEX = 6U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_STRNCPY = 7U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_CHARACTER = 9U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_SINK = 10U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_UNLOCK = 11U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY = 512U,
    OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES = 16U
};

static uint32_t open_cfw_test_easylogger_hexdump_events[
    OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY
];
static uint32_t open_cfw_test_easylogger_hexdump_event_count_value;
static uint32_t open_cfw_test_easylogger_hexdump_lock_depth_value;
static uint32_t open_cfw_test_easylogger_hexdump_header_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_hex_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_character_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_strncpy_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_sink_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_sink_limit;
static uint32_t open_cfw_test_easylogger_hexdump_last_length_value;
static uint32_t open_cfw_test_easylogger_hexdump_last_level_value;
static uint32_t open_cfw_test_easylogger_hexdump_last_header_offset_value;
static uint32_t open_cfw_test_easylogger_hexdump_last_header_end_value;
static char open_cfw_test_easylogger_hexdump_last_header_name_value[64];
static char open_cfw_test_easylogger_hexdump_lines[
    OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES
][1025];
static uint32_t open_cfw_test_easylogger_hexdump_line_lengths[
    OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES
];
static char open_cfw_test_easylogger_hexdump_last_line_value[1025];
static uint32_t open_cfw_test_easylogger_hexdump_force_header;
static int32_t open_cfw_test_easylogger_hexdump_forced_header_result;
static jmp_buf open_cfw_test_easylogger_hexdump_escape;
static uint32_t open_cfw_test_easylogger_hexdump_escape_armed;

static void open_cfw_test_easylogger_hexdump_event(uint32_t event)
{
    if (
        open_cfw_test_easylogger_hexdump_event_count_value <
            OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY
    ) {
        open_cfw_test_easylogger_hexdump_events[
            open_cfw_test_easylogger_hexdump_event_count_value
        ] = event;
    }
    open_cfw_test_easylogger_hexdump_event_count_value++;
}

static int open_cfw_test_easylogger_hexdump_oracle_snprintf(
    char *buffer,
    size_t size,
    const char *format,
    ...
)
{
    int result;
    va_list arguments;

    va_start(arguments, format);
    if (strcmp(format, "D/HEX %s: %04X-%04X: ") == 0) {
        const char *name = va_arg(arguments, const char *);
        unsigned int offset = va_arg(arguments, unsigned int);
        unsigned int end = va_arg(arguments, unsigned int);
        open_cfw_test_easylogger_hexdump_event(
            OPEN_CFW_TEST_HEXDUMP_EVENT_HEADER
        );
        open_cfw_test_easylogger_hexdump_header_calls_value++;
        open_cfw_test_easylogger_hexdump_last_header_offset_value = offset;
        open_cfw_test_easylogger_hexdump_last_header_end_value = end;
        (void)snprintf(
            open_cfw_test_easylogger_hexdump_last_header_name_value,
            sizeof(open_cfw_test_easylogger_hexdump_last_header_name_value),
            "%s",
            name
        );
        if (open_cfw_test_easylogger_hexdump_force_header != 0U) {
            if (size != 0U) {
                buffer[0] = '\0';
            }
            result = (int)open_cfw_test_easylogger_hexdump_forced_header_result;
        } else {
            result = snprintf(buffer, size, format, name, offset, end);
        }
    } else if (strcmp(format, "%02X ") == 0) {
        unsigned int value = va_arg(arguments, unsigned int);
        open_cfw_test_easylogger_hexdump_event(
            OPEN_CFW_TEST_HEXDUMP_EVENT_HEX
        );
        open_cfw_test_easylogger_hexdump_hex_calls_value++;
        result = snprintf(buffer, size, format, value);
    } else {
        int value = va_arg(arguments, int);
        open_cfw_test_easylogger_hexdump_event(
            OPEN_CFW_TEST_HEXDUMP_EVENT_CHARACTER
        );
        open_cfw_test_easylogger_hexdump_character_calls_value++;
        result = snprintf(buffer, size, format, value);
    }
    va_end(arguments);
    return result;
}

static char *open_cfw_test_easylogger_hexdump_oracle_strncpy(
    char *destination,
    const char *source,
    size_t size
)
{
    size_t index;
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_STRNCPY
    );
    open_cfw_test_easylogger_hexdump_strncpy_calls_value++;
    for (index = 0U; index < size; index++) {
        if (*source != '\0') {
            destination[index] = *source++;
        } else {
            destination[index] = '\0';
        }
    }
    return destination;
}

ElogErrCode elog_port_init(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_port_deinit(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_async_init(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_async_deinit(void)
{
    return ELOG_NO_ERR;
}

void elog_async_enabled(bool enabled)
{
    (void)enabled;
}

void elog_port_output(const char *buffer, size_t length)
{
    (void)buffer;
    (void)length;
}

void elog_port_output_lock(void)
{
    open_cfw_test_easylogger_hexdump_event(OPEN_CFW_TEST_HEXDUMP_EVENT_LOCK);
    open_cfw_test_easylogger_hexdump_lock_depth_value++;
}

void elog_port_output_unlock(void)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_UNLOCK
    );
    if (open_cfw_test_easylogger_hexdump_lock_depth_value != 0U) {
        open_cfw_test_easylogger_hexdump_lock_depth_value--;
    }
}

const char *elog_port_get_time(void)
{
    return "TIME";
}

const char *elog_port_get_p_info(void)
{
    return "PROCESS";
}

const char *elog_port_get_t_info(void)
{
    return "THREAD";
}

void elog_async_output(uint8_t level, const char *buffer, size_t length)
{
    uint32_t slot = open_cfw_test_easylogger_hexdump_sink_calls_value;
    size_t copy = length > 1024U ? 1024U : length;

    open_cfw_test_easylogger_hexdump_event(OPEN_CFW_TEST_HEXDUMP_EVENT_SINK);
    open_cfw_test_easylogger_hexdump_sink_calls_value++;
    open_cfw_test_easylogger_hexdump_last_length_value = (uint32_t)length;
    open_cfw_test_easylogger_hexdump_last_level_value = level;
    memcpy(open_cfw_test_easylogger_hexdump_last_line_value, buffer, copy);
    open_cfw_test_easylogger_hexdump_last_line_value[copy] = '\0';
    if (slot < OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES) {
        memcpy(open_cfw_test_easylogger_hexdump_lines[slot], buffer, copy);
        open_cfw_test_easylogger_hexdump_lines[slot][copy] = '\0';
        open_cfw_test_easylogger_hexdump_line_lengths[slot] = (uint32_t)length;
    }
    if (
        open_cfw_test_easylogger_hexdump_escape_armed != 0U &&
        open_cfw_test_easylogger_hexdump_sink_limit != 0U &&
        open_cfw_test_easylogger_hexdump_sink_calls_value >=
            open_cfw_test_easylogger_hexdump_sink_limit
    ) {
        longjmp(open_cfw_test_easylogger_hexdump_escape, 1);
    }
}

static void open_cfw_test_easylogger_hexdump_assert_return(
    const char *expression,
    const char *function,
    size_t line
)
{
    (void)expression;
    (void)function;
    (void)line;
}

void open_cfw_test_easylogger_hexdump_reset(void)
{
    uint32_t level;
    memset(&elog, 0, sizeof(elog));
    elog.filter.level = ELOG_LVL_VERBOSE;
    for (level = 0U; level < ELOG_LVL_TOTAL_NUM; level++) {
        elog.enabled_fmt_set[level] = ELOG_FMT_ALL;
    }
    elog.init_ok = true;
    elog.output_enabled = true;
    elog.output_lock_enabled = true;
    elog_assert_hook = open_cfw_test_easylogger_hexdump_assert_return;
    memset(log_buf, 0xA5, sizeof(log_buf));
    memset(open_cfw_test_easylogger_hexdump_events, 0, sizeof(open_cfw_test_easylogger_hexdump_events));
    memset(open_cfw_test_easylogger_hexdump_lines, 0, sizeof(open_cfw_test_easylogger_hexdump_lines));
    memset(open_cfw_test_easylogger_hexdump_line_lengths, 0, sizeof(open_cfw_test_easylogger_hexdump_line_lengths));
    memset(open_cfw_test_easylogger_hexdump_last_line_value, 0, sizeof(open_cfw_test_easylogger_hexdump_last_line_value));
    memset(open_cfw_test_easylogger_hexdump_last_header_name_value, 0, sizeof(open_cfw_test_easylogger_hexdump_last_header_name_value));
    open_cfw_test_easylogger_hexdump_event_count_value = 0U;
    open_cfw_test_easylogger_hexdump_lock_depth_value = 0U;
    open_cfw_test_easylogger_hexdump_header_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_hex_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_character_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_strncpy_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_sink_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_sink_limit = 0U;
    open_cfw_test_easylogger_hexdump_last_length_value = 0U;
    open_cfw_test_easylogger_hexdump_last_level_value = 0U;
    open_cfw_test_easylogger_hexdump_last_header_offset_value = 0U;
    open_cfw_test_easylogger_hexdump_last_header_end_value = 0U;
    open_cfw_test_easylogger_hexdump_force_header = 0U;
    open_cfw_test_easylogger_hexdump_forced_header_result = 0;
    open_cfw_test_easylogger_hexdump_escape_armed = 0U;
}

void open_cfw_test_easylogger_hexdump_set_output_enabled(uint32_t enabled)
{
    elog.output_enabled = enabled != 0U;
}

void open_cfw_test_easylogger_hexdump_set_filter_level(uint32_t level)
{
    elog.filter.level = (uint8_t)level;
}

void open_cfw_test_easylogger_hexdump_set_filter_tag(const char *tag)
{
    (void)snprintf(elog.filter.tag, sizeof(elog.filter.tag), "%s", tag);
}

void open_cfw_test_easylogger_hexdump_force_header_result(
    uint32_t enabled,
    int32_t result
)
{
    open_cfw_test_easylogger_hexdump_force_header = enabled;
    open_cfw_test_easylogger_hexdump_forced_header_result = result;
}

uint32_t open_cfw_test_easylogger_hexdump_run(
    const char *name,
    uint32_t width,
    const void *buffer,
    uint32_t size,
    uint32_t sink_limit
)
{
    open_cfw_test_easylogger_hexdump_sink_limit = sink_limit;
    open_cfw_test_easylogger_hexdump_escape_armed = 1U;
    if (setjmp(open_cfw_test_easylogger_hexdump_escape) != 0) {
        open_cfw_test_easylogger_hexdump_escape_armed = 0U;
        return 1U;
    }
    elog_hexdump(name, (uint8_t)width, buffer, (uint16_t)size);
    open_cfw_test_easylogger_hexdump_escape_armed = 0U;
    return 0U;
}

#define OPEN_CFW_TEST_HEXDUMP_U32_GETTER(name, value) \
    uint32_t name(void) { return (value); }

OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_event_count, open_cfw_test_easylogger_hexdump_event_count_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_lock_depth, open_cfw_test_easylogger_hexdump_lock_depth_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_fill_calls, 0U)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_fill_count, 0U)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_fill_value, 0U)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_header_calls, open_cfw_test_easylogger_hexdump_header_calls_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_hex_calls, open_cfw_test_easylogger_hexdump_hex_calls_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_character_calls, open_cfw_test_easylogger_hexdump_character_calls_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_strncpy_calls, open_cfw_test_easylogger_hexdump_strncpy_calls_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_append_calls, 0U)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_sink_calls, open_cfw_test_easylogger_hexdump_sink_calls_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_last_length, open_cfw_test_easylogger_hexdump_last_length_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_last_buffer_matches, 1U)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_last_header_offset, open_cfw_test_easylogger_hexdump_last_header_offset_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_last_header_end, open_cfw_test_easylogger_hexdump_last_header_end_value)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(open_cfw_test_easylogger_hexdump_last_level, open_cfw_test_easylogger_hexdump_last_level_value)

uint32_t open_cfw_test_easylogger_hexdump_event_at(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_easylogger_hexdump_events[index];
}

const char *open_cfw_test_easylogger_hexdump_line_at(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES) {
        return "";
    }
    return open_cfw_test_easylogger_hexdump_lines[index];
}

uint32_t open_cfw_test_easylogger_hexdump_line_length_at(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES) {
        return 0U;
    }
    return open_cfw_test_easylogger_hexdump_line_lengths[index];
}

const char *open_cfw_test_easylogger_hexdump_last_line(void)
{
    return open_cfw_test_easylogger_hexdump_last_line_value;
}

const char *open_cfw_test_easylogger_hexdump_last_header_name(void)
{
    return open_cfw_test_easylogger_hexdump_last_header_name_value;
}
