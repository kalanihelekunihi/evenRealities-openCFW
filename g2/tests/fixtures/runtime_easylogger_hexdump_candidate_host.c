/*
 * SPDX-License-Identifier: MIT
 *
 * Host seam recorder for the nonproduction Apollo-main elog_hexdump source
 * candidate. It records ABI and ordering without replacing candidate logic.
 */

#include <setjmp.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct open_cfw_easylogger_hexdump_logger;

static struct open_cfw_easylogger_hexdump_logger *
open_cfw_test_easylogger_hexdump_get_logger(void);
static char *open_cfw_test_easylogger_hexdump_get_buffer(void);
static void open_cfw_test_easylogger_hexdump_fill(
    void *destination,
    uint32_t count,
    uint32_t value
);
static void open_cfw_test_easylogger_hexdump_raw_sink(
    const char *buffer,
    uint32_t length
);
static int open_cfw_test_easylogger_hexdump_format_header(
    char *buffer,
    uint32_t size,
    const char *name,
    unsigned int offset,
    unsigned int end
);
static void open_cfw_test_easylogger_hexdump_format_hex(
    char *buffer,
    uint8_t value
);
static void open_cfw_test_easylogger_hexdump_format_character(
    char *buffer,
    uint8_t value
);
static void open_cfw_test_easylogger_hexdump_blank_hex(char *buffer);

#define OPEN_CFW_EASYLOGGER_HEXDUMP_GET_LOGGER() \
    open_cfw_test_easylogger_hexdump_get_logger()
#define OPEN_CFW_EASYLOGGER_HEXDUMP_GET_BUFFER() \
    open_cfw_test_easylogger_hexdump_get_buffer()
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FILL(destination, count, value) \
    open_cfw_test_easylogger_hexdump_fill((destination), (count), (value))
#define OPEN_CFW_EASYLOGGER_HEXDUMP_RAW_SINK(buffer, length) \
    open_cfw_test_easylogger_hexdump_raw_sink((buffer), (length))
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEADER( \
    buffer, size, name, offset, end \
) \
    open_cfw_test_easylogger_hexdump_format_header( \
        (buffer), (size), (name), (offset), (end) \
    )
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEX(buffer, value) \
    open_cfw_test_easylogger_hexdump_format_hex((buffer), (value))
#define OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_CHARACTER(buffer, value) \
    open_cfw_test_easylogger_hexdump_format_character((buffer), (value))
#define OPEN_CFW_EASYLOGGER_HEXDUMP_BLANK_HEX(buffer) \
    open_cfw_test_easylogger_hexdump_blank_hex((buffer))

#include "../../components/shared/easylogger/runtime_easylogger_hexdump_candidate.c"

enum {
    OPEN_CFW_TEST_HEXDUMP_EVENT_FILL = 1U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_STATE = 2U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_LOCK = 3U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_BUFFER = 4U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_HEADER = 5U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_HEX = 6U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_STRNCPY = 7U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_APPEND = 8U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_CHARACTER = 9U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_SINK = 10U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_UNLOCK = 11U,
    OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY = 512U,
    OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES = 16U
};

static struct open_cfw_easylogger_hexdump_logger
    open_cfw_test_easylogger_hexdump_logger;
static char open_cfw_test_easylogger_hexdump_buffer[1025];
static uint32_t open_cfw_test_easylogger_hexdump_events[
    OPEN_CFW_TEST_HEXDUMP_EVENT_CAPACITY
];
static uint32_t open_cfw_test_easylogger_hexdump_event_count_value;
static uint32_t open_cfw_test_easylogger_hexdump_lock_depth_value;
static uint32_t open_cfw_test_easylogger_hexdump_fill_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_fill_count_value;
static uint32_t open_cfw_test_easylogger_hexdump_fill_value_value;
static uint32_t open_cfw_test_easylogger_hexdump_header_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_hex_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_character_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_strncpy_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_append_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_sink_calls_value;
static uint32_t open_cfw_test_easylogger_hexdump_sink_limit;
static uint32_t open_cfw_test_easylogger_hexdump_last_length_value;
static uint32_t open_cfw_test_easylogger_hexdump_last_buffer_match_value;
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

static struct open_cfw_easylogger_hexdump_logger *
open_cfw_test_easylogger_hexdump_get_logger(void)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_STATE
    );
    return &open_cfw_test_easylogger_hexdump_logger;
}

static char *open_cfw_test_easylogger_hexdump_get_buffer(void)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_BUFFER
    );
    return open_cfw_test_easylogger_hexdump_buffer;
}

static void open_cfw_test_easylogger_hexdump_fill(
    void *destination,
    uint32_t count,
    uint32_t value
)
{
    open_cfw_test_easylogger_hexdump_event(OPEN_CFW_TEST_HEXDUMP_EVENT_FILL);
    open_cfw_test_easylogger_hexdump_fill_calls_value++;
    open_cfw_test_easylogger_hexdump_fill_count_value = count;
    open_cfw_test_easylogger_hexdump_fill_value_value = value;
    memset(destination, (int)(uint8_t)value, (size_t)count);
}

void open_cfw_easylogger_output_lock(void)
{
    open_cfw_test_easylogger_hexdump_event(OPEN_CFW_TEST_HEXDUMP_EVENT_LOCK);
    open_cfw_test_easylogger_hexdump_lock_depth_value++;
}

void open_cfw_easylogger_output_unlock(void)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_UNLOCK
    );
    if (open_cfw_test_easylogger_hexdump_lock_depth_value != 0U) {
        open_cfw_test_easylogger_hexdump_lock_depth_value--;
    }
}

open_cfw_easylogger_hexdump_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_hexdump_u32 current_length,
    char *destination,
    const char *source
)
{
    const char *old = source;
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_APPEND
    );
    open_cfw_test_easylogger_hexdump_append_calls_value++;
    while (*source != '\0') {
        if (current_length++ < 1024U) {
            *destination++ = *source++;
        } else {
            break;
        }
    }
    return (open_cfw_easylogger_hexdump_u32)(source - old);
}

static int open_cfw_test_easylogger_hexdump_format_header(
    char *buffer,
    uint32_t size,
    const char *name,
    unsigned int offset,
    unsigned int end
)
{
    int result;

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
        result = snprintf(
            buffer,
            (size_t)size,
            "D/HEX %s: %04X-%04X: ",
            name,
            offset,
            end
        );
    }
    return result;
}

static void open_cfw_test_easylogger_hexdump_format_hex(
    char *buffer,
    uint8_t value
)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_HEX
    );
    open_cfw_test_easylogger_hexdump_hex_calls_value++;
    (void)snprintf(buffer, 8U, "%02X ", (unsigned int)value);
}

static void open_cfw_test_easylogger_hexdump_format_character(
    char *buffer,
    uint8_t value
)
{
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_CHARACTER
    );
    open_cfw_test_easylogger_hexdump_character_calls_value++;
    (void)snprintf(buffer, 8U, "%c", (int)value);
}

static void open_cfw_test_easylogger_hexdump_blank_hex(char *buffer)
{
    uint32_t index;
    open_cfw_test_easylogger_hexdump_event(
        OPEN_CFW_TEST_HEXDUMP_EVENT_STRNCPY
    );
    open_cfw_test_easylogger_hexdump_strncpy_calls_value++;
    buffer[0] = ' ';
    buffer[1] = ' ';
    buffer[2] = ' ';
    for (index = 3U; index < 8U; index++) {
        buffer[index] = '\0';
    }
}

static void open_cfw_test_easylogger_hexdump_raw_sink(
    const char *buffer,
    uint32_t length
)
{
    uint32_t slot = open_cfw_test_easylogger_hexdump_sink_calls_value;
    uint32_t copy = length > 1024U ? 1024U : length;

    open_cfw_test_easylogger_hexdump_event(OPEN_CFW_TEST_HEXDUMP_EVENT_SINK);
    open_cfw_test_easylogger_hexdump_sink_calls_value++;
    open_cfw_test_easylogger_hexdump_last_length_value = length;
    open_cfw_test_easylogger_hexdump_last_buffer_match_value =
        (uint32_t)(buffer == open_cfw_test_easylogger_hexdump_buffer);
    memcpy(open_cfw_test_easylogger_hexdump_last_line_value, buffer, copy);
    open_cfw_test_easylogger_hexdump_last_line_value[copy] = '\0';
    if (slot < OPEN_CFW_TEST_HEXDUMP_CAPTURED_LINES) {
        memcpy(open_cfw_test_easylogger_hexdump_lines[slot], buffer, copy);
        open_cfw_test_easylogger_hexdump_lines[slot][copy] = '\0';
        open_cfw_test_easylogger_hexdump_line_lengths[slot] = length;
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

void open_cfw_test_easylogger_hexdump_reset(void)
{
    memset(
        &open_cfw_test_easylogger_hexdump_logger,
        0,
        sizeof(open_cfw_test_easylogger_hexdump_logger)
    );
    open_cfw_test_easylogger_hexdump_logger.filter.level =
        OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_VERBOSE;
    open_cfw_test_easylogger_hexdump_logger.output_enabled = 1U;
    open_cfw_test_easylogger_hexdump_logger.output_lock_enabled = 1U;
    memset(open_cfw_test_easylogger_hexdump_buffer, 0xA5, 1024U);
    open_cfw_test_easylogger_hexdump_buffer[1024] = '\0';
    memset(open_cfw_test_easylogger_hexdump_events, 0, sizeof(open_cfw_test_easylogger_hexdump_events));
    memset(open_cfw_test_easylogger_hexdump_lines, 0, sizeof(open_cfw_test_easylogger_hexdump_lines));
    memset(open_cfw_test_easylogger_hexdump_line_lengths, 0, sizeof(open_cfw_test_easylogger_hexdump_line_lengths));
    memset(open_cfw_test_easylogger_hexdump_last_line_value, 0, sizeof(open_cfw_test_easylogger_hexdump_last_line_value));
    memset(open_cfw_test_easylogger_hexdump_last_header_name_value, 0, sizeof(open_cfw_test_easylogger_hexdump_last_header_name_value));
    open_cfw_test_easylogger_hexdump_event_count_value = 0U;
    open_cfw_test_easylogger_hexdump_lock_depth_value = 0U;
    open_cfw_test_easylogger_hexdump_fill_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_fill_count_value = 0U;
    open_cfw_test_easylogger_hexdump_fill_value_value = 0U;
    open_cfw_test_easylogger_hexdump_header_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_hex_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_character_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_strncpy_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_append_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_sink_calls_value = 0U;
    open_cfw_test_easylogger_hexdump_sink_limit = 0U;
    open_cfw_test_easylogger_hexdump_last_length_value = 0U;
    open_cfw_test_easylogger_hexdump_last_buffer_match_value = 0U;
    open_cfw_test_easylogger_hexdump_last_header_offset_value = 0U;
    open_cfw_test_easylogger_hexdump_last_header_end_value = 0U;
    open_cfw_test_easylogger_hexdump_force_header = 0U;
    open_cfw_test_easylogger_hexdump_forced_header_result = 0;
    open_cfw_test_easylogger_hexdump_escape_armed = 0U;
}

void open_cfw_test_easylogger_hexdump_set_output_enabled(uint32_t enabled)
{
    open_cfw_test_easylogger_hexdump_logger.output_enabled = (uint8_t)enabled;
}

void open_cfw_test_easylogger_hexdump_set_filter_level(uint32_t level)
{
    open_cfw_test_easylogger_hexdump_logger.filter.level = (uint8_t)level;
}

void open_cfw_test_easylogger_hexdump_set_filter_tag(const char *tag)
{
    (void)snprintf(
        open_cfw_test_easylogger_hexdump_logger.filter.tag,
        sizeof(open_cfw_test_easylogger_hexdump_logger.filter.tag),
        "%s",
        tag
    );
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
    open_cfw_easylogger_hexdump_candidate(
        name,
        (open_cfw_easylogger_hexdump_u8)width,
        buffer,
        (open_cfw_easylogger_hexdump_u16)size
    );
    open_cfw_test_easylogger_hexdump_escape_armed = 0U;
    return 0U;
}

#define OPEN_CFW_TEST_HEXDUMP_U32_GETTER(name, value) \
    uint32_t name(void) { return (value); }

OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_event_count,
    open_cfw_test_easylogger_hexdump_event_count_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_lock_depth,
    open_cfw_test_easylogger_hexdump_lock_depth_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_fill_calls,
    open_cfw_test_easylogger_hexdump_fill_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_fill_count,
    open_cfw_test_easylogger_hexdump_fill_count_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_fill_value,
    open_cfw_test_easylogger_hexdump_fill_value_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_header_calls,
    open_cfw_test_easylogger_hexdump_header_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_hex_calls,
    open_cfw_test_easylogger_hexdump_hex_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_character_calls,
    open_cfw_test_easylogger_hexdump_character_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_strncpy_calls,
    open_cfw_test_easylogger_hexdump_strncpy_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_append_calls,
    open_cfw_test_easylogger_hexdump_append_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_sink_calls,
    open_cfw_test_easylogger_hexdump_sink_calls_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_last_length,
    open_cfw_test_easylogger_hexdump_last_length_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_last_buffer_matches,
    open_cfw_test_easylogger_hexdump_last_buffer_match_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_last_header_offset,
    open_cfw_test_easylogger_hexdump_last_header_offset_value
)
OPEN_CFW_TEST_HEXDUMP_U32_GETTER(
    open_cfw_test_easylogger_hexdump_last_header_end,
    open_cfw_test_easylogger_hexdump_last_header_end_value
)

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
