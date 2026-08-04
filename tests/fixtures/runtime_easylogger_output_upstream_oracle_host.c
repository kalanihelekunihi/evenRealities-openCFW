/*
 * SPDX-License-Identifier: MIT
 *
 * Host oracle compiled directly from authenticated Armink EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24. Only the port and formatter
 * seams are substituted so candidate and pristine thread-mode bytes can be
 * compared deterministically.
 */

#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int open_cfw_test_easylogger_oracle_snprintf(
    char *buffer,
    size_t size,
    const char *format,
    ...
);
static int open_cfw_test_easylogger_oracle_vsnprintf(
    char *buffer,
    size_t size,
    const char *format,
    va_list arguments
);

#undef snprintf
#undef vsnprintf
#define snprintf open_cfw_test_easylogger_oracle_snprintf
#define vsnprintf open_cfw_test_easylogger_oracle_vsnprintf
#include "../../third_party/easylogger/src/elog.c"
#include "../../third_party/easylogger/src/elog_utils.c"
#undef snprintf
#undef vsnprintf

enum {
    OPEN_CFW_TEST_ELOG_EVENT_LOCK = 4U,
    OPEN_CFW_TEST_ELOG_EVENT_TIME = 7U,
    OPEN_CFW_TEST_ELOG_EVENT_PROCESS = 8U,
    OPEN_CFW_TEST_ELOG_EVENT_THREAD = 9U,
    OPEN_CFW_TEST_ELOG_EVENT_LINE_FORMAT = 10U,
    OPEN_CFW_TEST_ELOG_EVENT_MESSAGE_FORMAT = 11U,
    OPEN_CFW_TEST_ELOG_EVENT_SINK = 12U,
    OPEN_CFW_TEST_ELOG_EVENT_UNLOCK = 13U,
    OPEN_CFW_TEST_ELOG_EVENT_CAPACITY = 256U
};

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

static int open_cfw_test_easylogger_oracle_snprintf(
    char *buffer,
    size_t size,
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
    result = vsnprintf(buffer, size, format, arguments);
    va_end(arguments);
    return result;
}

static int open_cfw_test_easylogger_oracle_vsnprintf(
    char *buffer,
    size_t size,
    const char *format,
    va_list arguments
)
{
    size_t write;

    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_MESSAGE_FORMAT
    );
    if (open_cfw_test_easylogger_output_force_format == 0U) {
        return vsnprintf(buffer, size, format, arguments);
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

void elog_port_output(const char *log, size_t size)
{
    (void)log;
    (void)size;
}

void elog_port_output_lock(void)
{
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_LOCK
    );
    open_cfw_test_easylogger_output_lock_depth++;
}

void elog_port_output_unlock(void)
{
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_UNLOCK
    );
    if (open_cfw_test_easylogger_output_lock_depth != 0U) {
        open_cfw_test_easylogger_output_lock_depth--;
    }
}

const char *elog_port_get_time(void)
{
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_TIME
    );
    return open_cfw_test_easylogger_output_time;
}

const char *elog_port_get_p_info(void)
{
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_PROCESS
    );
    return open_cfw_test_easylogger_output_process;
}

const char *elog_port_get_t_info(void)
{
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_THREAD
    );
    return open_cfw_test_easylogger_output_thread;
}

void elog_async_output(uint8_t level, const char *buffer, size_t length)
{
    size_t copy = length > 1024U ? 1024U : length;
    open_cfw_test_easylogger_output_record_event(
        OPEN_CFW_TEST_ELOG_EVENT_SINK
    );
    open_cfw_test_easylogger_output_sink_calls_value++;
    open_cfw_test_easylogger_output_sink_length_value = (uint32_t)length;
    open_cfw_test_easylogger_output_sink_level_value = level;
    memcpy(open_cfw_test_easylogger_output_sink, buffer, copy);
    open_cfw_test_easylogger_output_sink[copy] = '\0';
}

static void open_cfw_test_easylogger_output_assert_return(
    const char *expression,
    const char *function,
    size_t line
)
{
    (void)expression;
    (void)function;
    (void)line;
}

void open_cfw_test_easylogger_output_reset(uint32_t ipsr)
{
    uint32_t level;

    (void)ipsr;
    memset(&elog, 0, sizeof(elog));
    elog.filter.level = ELOG_LVL_VERBOSE;
    for (level = 0U; level < ELOG_LVL_TOTAL_NUM; level++) {
        elog.enabled_fmt_set[level] = ELOG_FMT_ALL;
    }
    elog.init_ok = true;
    elog.output_enabled = true;
    elog.output_lock_enabled = true;
    elog.text_color_enabled = true;
    elog_assert_hook = open_cfw_test_easylogger_output_assert_return;
    open_cfw_test_easylogger_output_time = "TIME";
    open_cfw_test_easylogger_output_process = "PROCESS";
    open_cfw_test_easylogger_output_thread = "THREAD";
    open_cfw_test_easylogger_output_event_count_value = 0U;
    open_cfw_test_easylogger_output_lock_depth = 0U;
    open_cfw_test_easylogger_output_force_format = 0U;
    open_cfw_test_easylogger_output_forced_result = 0;
    open_cfw_test_easylogger_output_forced_write = 0U;
    open_cfw_test_easylogger_output_forced_byte = (uint8_t)'X';
    open_cfw_test_easylogger_output_sink_length_value = 0U;
    open_cfw_test_easylogger_output_sink_level_value = 0U;
    open_cfw_test_easylogger_output_sink_calls_value = 0U;
    memset(open_cfw_test_easylogger_output_events, 0, sizeof(open_cfw_test_easylogger_output_events));
    memset(open_cfw_test_easylogger_output_sink, 0, sizeof(open_cfw_test_easylogger_output_sink));
    memset(log_buf, 0xA5, sizeof(log_buf));
}

void open_cfw_test_easylogger_output_set_output_enabled(uint32_t enabled)
{
    elog.output_enabled = enabled != 0U;
}

void open_cfw_test_easylogger_output_set_global_level(uint32_t level)
{
    elog.filter.level = (uint8_t)level;
}

void open_cfw_test_easylogger_output_set_color(uint32_t enabled)
{
    elog.text_color_enabled = enabled != 0U;
}

void open_cfw_test_easylogger_output_set_mask(uint32_t level, uint32_t mask)
{
    if (level < ELOG_LVL_TOTAL_NUM) {
        elog.enabled_fmt_set[level] = mask;
    }
}

void open_cfw_test_easylogger_output_set_filter(
    const char *tag,
    const char *keyword
)
{
    (void)snprintf(elog.filter.tag, sizeof(elog.filter.tag), "%s", tag);
    (void)snprintf(
        elog.filter.keyword,
        sizeof(elog.filter.keyword),
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
    ElogTagLvlFilter *entry;
    if (index >= ELOG_FILTER_TAG_LVL_MAX_NUM) {
        return;
    }
    entry = &elog.filter.tag_lvl[index];
    memset(entry, 0, sizeof(*entry));
    entry->level = (uint8_t)level;
    entry->tag_use_flag = used != 0U;
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
    elog_output(
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
    elog_output(
        (uint8_t)level,
        tag,
        file,
        function,
        line,
        format,
        value
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
