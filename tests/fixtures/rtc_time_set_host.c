/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the Apollo510 RTC calendar/time setter.
 */

#define OPEN_CFW_TEST_RTC_TIME_EVENT_READ 1U
#define OPEN_CFW_TEST_RTC_TIME_EVENT_WRITE 2U
#define OPEN_CFW_TEST_RTC_TIME_EVENT_LEVEL 3U
#define OPEN_CFW_TEST_RTC_TIME_EVENT_STRUCTURED 4U
#define OPEN_CFW_TEST_RTC_TIME_EVENT_TRACE 5U

#define OPEN_CFW_TEST_RTC_TIME_CONTROL_ADDRESS 0x40004800U
#define OPEN_CFW_TEST_RTC_TIME_COUNTER_LOW_ADDRESS 0x40004820U
#define OPEN_CFW_TEST_RTC_TIME_COUNTER_UP_ADDRESS 0x40004824U

unsigned int open_cfw_test_rtc_time_control;
unsigned int open_cfw_test_rtc_time_counter_low;
unsigned int open_cfw_test_rtc_time_counter_up;
unsigned int open_cfw_test_rtc_time_event_count;
unsigned int open_cfw_test_rtc_time_event_kind[32];
unsigned int open_cfw_test_rtc_time_event_address[32];
unsigned int open_cfw_test_rtc_time_event_value[32];

unsigned int open_cfw_test_rtc_time_level_values[8];
unsigned int open_cfw_test_rtc_time_level_count;
unsigned int open_cfw_test_rtc_time_level_index;

unsigned int open_cfw_test_rtc_time_structured_count;
unsigned int open_cfw_test_rtc_time_structured_severity;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_structured_tag;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_structured_file;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_structured_function;
unsigned int open_cfw_test_rtc_time_structured_line;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_structured_message;

unsigned int open_cfw_test_rtc_time_trace_count;
unsigned int open_cfw_test_rtc_time_trace_mask;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_trace_format;
__UINTPTR_TYPE__ open_cfw_test_rtc_time_trace_argument;

static void open_cfw_test_rtc_time_record(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rtc_time_event_count++;

    if (index < 32U) {
        open_cfw_test_rtc_time_event_kind[index] = kind;
        open_cfw_test_rtc_time_event_address[index] = address;
        open_cfw_test_rtc_time_event_value[index] = value;
    }
}

void open_cfw_test_rtc_time_reset(void)
{
    unsigned int index;

    open_cfw_test_rtc_time_control = 0U;
    open_cfw_test_rtc_time_counter_low = 0U;
    open_cfw_test_rtc_time_counter_up = 0U;
    open_cfw_test_rtc_time_event_count = 0U;
    open_cfw_test_rtc_time_level_count = 0U;
    open_cfw_test_rtc_time_level_index = 0U;
    open_cfw_test_rtc_time_structured_count = 0U;
    open_cfw_test_rtc_time_structured_severity = 0U;
    open_cfw_test_rtc_time_structured_tag = 0U;
    open_cfw_test_rtc_time_structured_file = 0U;
    open_cfw_test_rtc_time_structured_function = 0U;
    open_cfw_test_rtc_time_structured_line = 0U;
    open_cfw_test_rtc_time_structured_message = 0U;
    open_cfw_test_rtc_time_trace_count = 0U;
    open_cfw_test_rtc_time_trace_mask = 0U;
    open_cfw_test_rtc_time_trace_format = 0U;
    open_cfw_test_rtc_time_trace_argument = 0U;

    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_rtc_time_event_kind[index] = 0U;
        open_cfw_test_rtc_time_event_address[index] = 0U;
        open_cfw_test_rtc_time_event_value[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtc_time_level_values[index] = 0U;
    }
}

static unsigned int open_cfw_test_rtc_time_read(unsigned int address)
{
    unsigned int value;

    if (address == OPEN_CFW_TEST_RTC_TIME_CONTROL_ADDRESS) {
        value = open_cfw_test_rtc_time_control;
    } else if (address == OPEN_CFW_TEST_RTC_TIME_COUNTER_LOW_ADDRESS) {
        value = open_cfw_test_rtc_time_counter_low;
    } else {
        value = open_cfw_test_rtc_time_counter_up;
    }
    open_cfw_test_rtc_time_record(
        OPEN_CFW_TEST_RTC_TIME_EVENT_READ,
        address,
        value
    );
    return value;
}

static void open_cfw_test_rtc_time_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == OPEN_CFW_TEST_RTC_TIME_CONTROL_ADDRESS) {
        open_cfw_test_rtc_time_control = value;
    } else if (address == OPEN_CFW_TEST_RTC_TIME_COUNTER_LOW_ADDRESS) {
        open_cfw_test_rtc_time_counter_low = value;
    } else {
        open_cfw_test_rtc_time_counter_up = value;
    }
    open_cfw_test_rtc_time_record(
        OPEN_CFW_TEST_RTC_TIME_EVENT_WRITE,
        address,
        value
    );
}

static unsigned int open_cfw_test_rtc_time_log_level(void)
{
    unsigned int index = open_cfw_test_rtc_time_level_index++;
    unsigned int value = 0U;

    if (index < open_cfw_test_rtc_time_level_count && index < 8U) {
        value = open_cfw_test_rtc_time_level_values[index];
    }
    open_cfw_test_rtc_time_record(
        OPEN_CFW_TEST_RTC_TIME_EVENT_LEVEL,
        0U,
        value
    );
    return value;
}

static void open_cfw_test_rtc_time_structured_log(
    unsigned int severity,
    const char *tag,
    const char *file,
    const char *function,
    unsigned int line,
    const char *message
)
{
    ++open_cfw_test_rtc_time_structured_count;
    open_cfw_test_rtc_time_structured_severity = severity;
    open_cfw_test_rtc_time_structured_tag = (__UINTPTR_TYPE__)tag;
    open_cfw_test_rtc_time_structured_file = (__UINTPTR_TYPE__)file;
    open_cfw_test_rtc_time_structured_function = (__UINTPTR_TYPE__)function;
    open_cfw_test_rtc_time_structured_line = line;
    open_cfw_test_rtc_time_structured_message = (__UINTPTR_TYPE__)message;
    open_cfw_test_rtc_time_record(
        OPEN_CFW_TEST_RTC_TIME_EVENT_STRUCTURED,
        0U,
        severity
    );
}

static void open_cfw_test_rtc_time_trace(
    unsigned int mask,
    const char *format,
    const char *argument
)
{
    ++open_cfw_test_rtc_time_trace_count;
    open_cfw_test_rtc_time_trace_mask = mask;
    open_cfw_test_rtc_time_trace_format = (__UINTPTR_TYPE__)format;
    open_cfw_test_rtc_time_trace_argument = (__UINTPTR_TYPE__)argument;
    open_cfw_test_rtc_time_record(
        OPEN_CFW_TEST_RTC_TIME_EVENT_TRACE,
        0U,
        mask
    );
}

#define OPEN_CFW_RTC_TIME_READ(address) \
    open_cfw_test_rtc_time_read(address)
#define OPEN_CFW_RTC_TIME_WRITE(address, value) \
    open_cfw_test_rtc_time_write((address), (value))
#define OPEN_CFW_RTC_TIME_LOG_LEVEL() \
    open_cfw_test_rtc_time_log_level()
#define OPEN_CFW_RTC_TIME_STRUCTURED_LOG( \
    severity, tag, file, function, line, message \
) \
    open_cfw_test_rtc_time_structured_log( \
        (severity), (tag), (file), (function), (line), (message) \
    )
#define OPEN_CFW_RTC_TIME_TRACE(mask, format, argument) \
    open_cfw_test_rtc_time_trace((mask), (format), (argument))

#include "../../components/apollo_main/core_overlay/rtc_time_set.c"
