/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 RTC calendar and time-set adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock wrapper, HAL dependencies, register effects,
 * diagnostics, and host behavioral evidence are recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_rtc_time_uintptr;

typedef unsigned int (*open_cfw_rtc_time_log_level_function)(void);
typedef void (*open_cfw_rtc_time_structured_log_function)(
    unsigned int,
    const char *,
    const char *,
    const char *,
    unsigned int,
    const char *
);
typedef void (*open_cfw_rtc_time_trace_function)(
    unsigned int,
    const char *,
    const char *
);

typedef struct open_cfw_rtc_application_time {
    unsigned int prefix[3];
    unsigned int year;
    unsigned int month;
    unsigned int day;
    unsigned int hour;
    unsigned int minute;
    unsigned int second;
    unsigned int subseconds;
} open_cfw_rtc_application_time;

typedef struct open_cfw_rtc_hal_time {
    unsigned int read_error;
    unsigned int weekday;
    unsigned int century_bit;
    unsigned int year;
    unsigned int month;
    unsigned int day;
    unsigned int hour;
    unsigned int minute;
    unsigned int second;
    unsigned int hundredths;
} open_cfw_rtc_hal_time;

#define OPEN_CFW_RTC_TIME_CONTROL_ADDRESS 0x40004800U
#define OPEN_CFW_RTC_TIME_COUNTER_LOW_ADDRESS 0x40004820U
#define OPEN_CFW_RTC_TIME_COUNTER_UP_ADDRESS 0x40004824U
#define OPEN_CFW_RTC_TIME_WRITE_ENABLE_MASK 0x00000001U

#define OPEN_CFW_RTC_TIME_TAG_ADDRESS 0x0078D4A4U
#define OPEN_CFW_RTC_TIME_FILE_ADDRESS 0x007149A4U
#define OPEN_CFW_RTC_TIME_FUNCTION_ADDRESS 0x00785D30U
#define OPEN_CFW_RTC_TIME_MESSAGE_ADDRESS 0x0077F180U
#define OPEN_CFW_RTC_TIME_TRACE_ADDRESS 0x0075FA90U

#ifndef OPEN_CFW_RTC_TIME_READ
#define OPEN_CFW_RTC_TIME_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_RTC_TIME_WRITE
#define OPEN_CFW_RTC_TIME_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_RTC_TIME_LOG_LEVEL
#define OPEN_CFW_RTC_TIME_LOG_LEVEL() \
    (((open_cfw_rtc_time_log_level_function) \
        (open_cfw_rtc_time_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_RTC_TIME_STRUCTURED_LOG
#define OPEN_CFW_RTC_TIME_STRUCTURED_LOG( \
    severity, tag, file, function, line, message \
) \
    (((open_cfw_rtc_time_structured_log_function) \
        (open_cfw_rtc_time_uintptr)0x0043D575U)( \
            (severity), \
            (tag), \
            (file), \
            (function), \
            (line), \
            (message) \
        ))
#endif

#ifndef OPEN_CFW_RTC_TIME_TRACE
#define OPEN_CFW_RTC_TIME_TRACE(mask, format, argument) \
    (((open_cfw_rtc_time_trace_function) \
        (open_cfw_rtc_time_uintptr)0x0043CE9FU)( \
            (mask), \
            (format), \
            (argument) \
        ))
#endif

static const unsigned int open_cfw_rtc_days_per_month[12] = {
    31U, 28U, 31U, 30U, 31U, 30U,
    31U, 31U, 30U, 31U, 30U, 31U
};

static const int open_cfw_rtc_month_offsets[12] = {
    4, 0, 0, 3, 5, 1, 3, 6, 2, 4, 0, 2
};

/*
 * This is the exact AmbiqSuite 5.1.0 predicate, including its shipped
 * "% 400 != 0" century behavior. Compatibility requires retaining it.
 */
static __attribute__((always_inline)) inline int
open_cfw_rtc_is_leap_year(int year)
{
    return year % 4 == 0
        && (year % 100 != 0 || year % 400 != 0);
}

static int open_cfw_rtc_compute_weekday(int year, int month, int day)
{
    int leap_offset = 0;
    int weekday;

    if (month < 1 || month > 12 || year < 0 || day < 1) {
        return 7;
    }

    if ((unsigned int)day
        > open_cfw_rtc_days_per_month[(unsigned int)month - 1U]) {
        if (!(month == 2
            && open_cfw_rtc_is_leap_year(year)
            && day == 29)) {
            return 7;
        }
    }

    if (open_cfw_rtc_is_leap_year(year) && month < 3) {
        leap_offset = -1;
    }

    weekday = day
        + 2
        + year
        + year / 4
        - year / 100
        + year / 400
        + open_cfw_rtc_month_offsets[(unsigned int)month - 1U]
        + leap_offset;
    return weekday % 7;
}

static __attribute__((always_inline)) inline int
open_cfw_rtc_hal_time_valid(const open_cfw_rtc_hal_time *time)
{
    if (time->hundredths >= 100U) {
        return 0;
    }
    if (time->second >= 60U) {
        return 0;
    }
    if (time->minute >= 60U) {
        return 0;
    }
    if (time->hour >= 24U) {
        return 0;
    }
    if (time->day < 1U || time->day > 31U) {
        return 0;
    }
    if (time->month < 1U || time->month > 12U) {
        return 0;
    }
    if (time->year > 100U) {
        return 0;
    }
    if (time->weekday > 6U) {
        return 0;
    }
    return 1;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_rtc_decimal_to_bcd(unsigned int value)
{
    unsigned int byte = value & 0xFFU;

    return (byte % 10U) | (((byte / 10U) & 0xFU) << 4U);
}

static unsigned int open_cfw_rtc_hal_time_set(
    const open_cfw_rtc_hal_time *time
)
{
    unsigned int control;
    unsigned int counter_low;
    unsigned int counter_up;

    if (!open_cfw_rtc_hal_time_valid(time)) {
        return 1U;
    }

    control = OPEN_CFW_RTC_TIME_READ(OPEN_CFW_RTC_TIME_CONTROL_ADDRESS);
    OPEN_CFW_RTC_TIME_WRITE(
        OPEN_CFW_RTC_TIME_CONTROL_ADDRESS,
        control | OPEN_CFW_RTC_TIME_WRITE_ENABLE_MASK
    );

    counter_low =
        ((open_cfw_rtc_decimal_to_bcd(time->hour) & 0x3FU) << 24U)
        | ((open_cfw_rtc_decimal_to_bcd(time->minute) & 0x7FU) << 16U)
        | ((open_cfw_rtc_decimal_to_bcd(time->second) & 0x7FU) << 8U)
        | open_cfw_rtc_decimal_to_bcd(time->hundredths);
    OPEN_CFW_RTC_TIME_WRITE(
        OPEN_CFW_RTC_TIME_COUNTER_LOW_ADDRESS,
        counter_low
    );

    counter_up =
        ((time->century_bit & 1U) << 28U)
        | ((time->weekday & 7U) << 24U)
        | ((open_cfw_rtc_decimal_to_bcd(time->year) & 0xFFU) << 16U)
        | ((open_cfw_rtc_decimal_to_bcd(time->month) & 0x1FU) << 8U)
        | (open_cfw_rtc_decimal_to_bcd(time->day) & 0x3FU);
    OPEN_CFW_RTC_TIME_WRITE(
        OPEN_CFW_RTC_TIME_COUNTER_UP_ADDRESS,
        counter_up
    );

    control = OPEN_CFW_RTC_TIME_READ(OPEN_CFW_RTC_TIME_CONTROL_ADDRESS);
    OPEN_CFW_RTC_TIME_WRITE(
        OPEN_CFW_RTC_TIME_CONTROL_ADDRESS,
        control & ~OPEN_CFW_RTC_TIME_WRITE_ENABLE_MASK
    );
    return 0U;
}

/*
 * ABI-compatible source replacement for stock
 * 0x0047EE78...0x0047EEF9.
 */
__attribute__((used, noinline))
unsigned int open_cfw_rtc_time_set(
    const open_cfw_rtc_application_time *input
)
{
    open_cfw_rtc_hal_time time;
    unsigned int level;

    time.weekday = (unsigned int)open_cfw_rtc_compute_weekday(
        (int)(input->year + 2000U),
        (int)input->month,
        (int)input->day
    );
    time.century_bit = 1U;
    time.year = input->year;
    time.month = input->month;
    time.day = input->day;
    time.hour = input->hour;
    time.minute = input->minute;
    time.second = input->second;
    time.hundredths = 0U;

    if (open_cfw_rtc_hal_time_set(&time) == 0U) {
        return 0U;
    }

    level = OPEN_CFW_RTC_TIME_LOG_LEVEL();
    if ((level & 2U) != 0U) {
        OPEN_CFW_RTC_TIME_STRUCTURED_LOG(
            1U,
            (const char *)(open_cfw_rtc_time_uintptr)
                OPEN_CFW_RTC_TIME_TAG_ADDRESS,
            (const char *)(open_cfw_rtc_time_uintptr)
                OPEN_CFW_RTC_TIME_FILE_ADDRESS,
            (const char *)(open_cfw_rtc_time_uintptr)
                OPEN_CFW_RTC_TIME_FUNCTION_ADDRESS,
            221U,
            (const char *)(open_cfw_rtc_time_uintptr)
                OPEN_CFW_RTC_TIME_MESSAGE_ADDRESS
        );
    }

    level = OPEN_CFW_RTC_TIME_LOG_LEVEL();
    if ((level & 1U) != 0U
        || (OPEN_CFW_RTC_TIME_LOG_LEVEL() & 4U) != 0U) {
        const char *trace =
            (const char *)(open_cfw_rtc_time_uintptr)
                OPEN_CFW_RTC_TIME_TRACE_ADDRESS;

        OPEN_CFW_RTC_TIME_TRACE(0x04000000U, trace, trace);
    }

    return 1U;
}

#undef OPEN_CFW_RTC_TIME_TRACE
#undef OPEN_CFW_RTC_TIME_STRUCTURED_LOG
#undef OPEN_CFW_RTC_TIME_LOG_LEVEL
#undef OPEN_CFW_RTC_TIME_WRITE
#undef OPEN_CFW_RTC_TIME_READ
#undef OPEN_CFW_RTC_TIME_TRACE_ADDRESS
#undef OPEN_CFW_RTC_TIME_MESSAGE_ADDRESS
#undef OPEN_CFW_RTC_TIME_FUNCTION_ADDRESS
#undef OPEN_CFW_RTC_TIME_FILE_ADDRESS
#undef OPEN_CFW_RTC_TIME_TAG_ADDRESS
#undef OPEN_CFW_RTC_TIME_WRITE_ENABLE_MASK
#undef OPEN_CFW_RTC_TIME_COUNTER_UP_ADDRESS
#undef OPEN_CFW_RTC_TIME_COUNTER_LOW_ADDRESS
#undef OPEN_CFW_RTC_TIME_CONTROL_ADDRESS
