/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 calendar and peer time service.  The
 * RTC, role, transport, configuration, and delayed-event operations remain
 * explicit provider seams so host tests never touch device hardware.
 */
#include "service_time.h"

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_STATIC_ASSERT(name, condition) \
    typedef char open_cfw_static_assert_##name[(condition) ? 1 : -1]

OPEN_CFW_STATIC_ASSERT(
    service_time_calendar_bytes,
    sizeof(open_cfw_service_time_calendar) == 40U
);
OPEN_CFW_STATIC_ASSERT(
    service_time_peer_message_bytes,
    sizeof(open_cfw_service_time_peer_message) == 16U
);

#ifndef OPEN_CFW_SERVICE_TIME_CONFIGURATION
#define OPEN_CFW_SERVICE_TIME_CONFIGURATION \
    (*(const volatile uint8_t * volatile *)(uintptr_t)0x200036FCU)
#endif

#ifndef OPEN_CFW_SERVICE_TIME_FORMAT_MODE
uint32_t open_cfw_service_time_format_mode(void);
#define OPEN_CFW_SERVICE_TIME_FORMAT_MODE() \
    open_cfw_service_time_format_mode()
#endif

#ifndef OPEN_CFW_SERVICE_TIME_RTC_GET
void open_cfw_rtc_time_get(open_cfw_service_time_calendar *calendar);
#define OPEN_CFW_SERVICE_TIME_RTC_GET(calendar) \
    open_cfw_rtc_time_get((calendar))
#endif

#ifndef OPEN_CFW_SERVICE_TIME_RTC_SET
uint32_t open_cfw_rtc_time_set(
    const open_cfw_service_time_calendar *calendar
);
#define OPEN_CFW_SERVICE_TIME_RTC_SET(calendar) \
    open_cfw_rtc_time_set((calendar))
#endif

#ifndef OPEN_CFW_SERVICE_TIME_ROLE
uint8_t open_cfw_service_time_role(void);
#define OPEN_CFW_SERVICE_TIME_ROLE() open_cfw_service_time_role()
#endif

#ifndef OPEN_CFW_SERVICE_TIME_SYNC_SEND
int open_cfw_service_time_sync_send(
    uint32_t record_id, const void *payload, uint32_t payload_bytes,
    uint32_t options
);
#define OPEN_CFW_SERVICE_TIME_SYNC_SEND( \
    record_id, payload, payload_bytes, options \
) \
    open_cfw_service_time_sync_send( \
        (record_id), (payload), (payload_bytes), (options))
#endif

typedef void (*open_cfw_service_time_callback)(void);

#ifndef OPEN_CFW_SERVICE_TIME_REMOVE_DELAYED
uint8_t open_cfw_service_time_remove_delayed(
    open_cfw_service_time_callback callback
);
#define OPEN_CFW_SERVICE_TIME_REMOVE_DELAYED(callback) \
    open_cfw_service_time_remove_delayed((callback))
#endif

#ifndef OPEN_CFW_SERVICE_TIME_PUSH_DELAYED
void open_cfw_service_time_push_delayed(
    open_cfw_service_time_callback callback, void *argument, uint32_t delay
);
#define OPEN_CFW_SERVICE_TIME_PUSH_DELAYED(callback, argument, delay) \
    open_cfw_service_time_push_delayed((callback), (argument), (delay))
#endif

#if !defined(OPEN_CFW_SERVICE_TIME_EPOCH24_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_EPOCH_CONFIGURED_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_EPOCH_WRAPPER_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_CALENDAR_TO_EPOCH_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_CALENDAR_WRAPPER_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_CURRENT_CALENDAR_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_CURRENT_EPOCH_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_RTC_REFRESH_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_SVC_SYNC_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_RPC_SYNC_ONLY) && \
    !defined(OPEN_CFW_SERVICE_TIME_SYNC_CALLBACK_ONLY)
#define OPEN_CFW_SERVICE_TIME_BUILD_ALL 1
#endif

static __attribute__((always_inline, unused)) inline int
open_cfw_service_time_is_leap(uint32_t year)
{
    return (year % 4U) == 0U &&
        ((year % 100U) != 0U || (year % 400U) == 0U);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_service_time_clear_calendar(
    open_cfw_service_time_calendar *calendar
)
{
    calendar->read_error = 0U;
    calendar->weekday = 0U;
    calendar->century_bit = 0U;
    calendar->year = 0U;
    calendar->month = 0U;
    calendar->day = 0U;
    calendar->hour = 0U;
    calendar->minute = 0U;
    calendar->second = 0U;
    calendar->hundredths = 0U;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_service_time_convert(
    uint32_t unix_seconds,
    open_cfw_service_time_calendar *calendar,
    int configured_hour
)
{
    uint32_t elapsed;
    uint32_t days;
    uint32_t day_in_cycle;
    uint32_t year;
    uint32_t month;
    uint32_t hour;

    if (calendar == NULL) {
        return;
    }
    open_cfw_service_time_clear_calendar(calendar);
    if (unix_seconds < OPEN_CFW_SERVICE_TIME_UNIX_2000) {
        elapsed = 0U;
        days = 0U;
    } else {
        elapsed = unix_seconds - OPEN_CFW_SERVICE_TIME_UNIX_2000;
        days = elapsed / OPEN_CFW_SERVICE_TIME_SECONDS_PER_DAY;
        elapsed %= OPEN_CFW_SERVICE_TIME_SECONDS_PER_DAY;
    }

    calendar->second = elapsed % 60U;
    calendar->minute = (elapsed / 60U) % 60U;
    hour = elapsed / 3600U;
    if (configured_hour != 0 && OPEN_CFW_SERVICE_TIME_FORMAT_MODE() == 1U) {
        hour %= 12U;
        if (hour == 0U) {
            hour = 12U;
        }
    }
    calendar->hour = hour;
    calendar->weekday = (days + 6U) % 7U;

    year = 2000U + (days / 1461U) * 4U;
    day_in_cycle = days % 1461U;
    if (day_in_cycle < 366U) {
    } else {
        year += (day_in_cycle - 1U) / 365U;
        day_in_cycle = (day_in_cycle - 1U) % 365U;
    }
    month = 1U;
    while (month <= 12U) {
        uint32_t month_days;
        if (month == 2U) {
            month_days = open_cfw_service_time_is_leap(year) ? 29U : 28U;
        } else if (month == 4U || month == 6U ||
                   month == 9U || month == 11U) {
            month_days = 30U;
        } else {
            month_days = 31U;
        }
        if (day_in_cycle < month_days) {
            break;
        }
        day_in_cycle -= month_days;
        ++month;
    }
    calendar->year = year - 2000U;
    calendar->century_bit = year >= 2100U ? 0U : 1U;
    calendar->month = month;
    calendar->day = day_in_cycle + 1U;
}

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_EPOCH24_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_epoch_to_calendar24(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
)
{
    open_cfw_service_time_convert(unix_seconds, calendar, 0);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_EPOCH_CONFIGURED_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_epoch_to_calendar_configured(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
)
{
    open_cfw_service_time_convert(unix_seconds, calendar, 1);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_EPOCH_WRAPPER_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_epoch_to_calendar(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
)
{
    open_cfw_service_time_epoch_to_calendar24(unix_seconds, calendar);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_CALENDAR_TO_EPOCH_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_service_time_calendar_to_epoch(
    const open_cfw_service_time_calendar *calendar
)
{
    uint32_t year;
    uint32_t year_in_century;
    uint32_t leap_adjust;
    uint32_t days;
    uint32_t seconds;

    if (calendar == NULL) {
        return 0U;
    }
    year = calendar->year + 2000U;
    year_in_century = year % 100U;
    if (calendar->month < 3U) {
        leap_adjust = 0U;
    } else if (open_cfw_service_time_is_leap(year)) {
        leap_adjust = 1U;
    } else {
        leap_adjust = 2U;
    }
    days = calendar->day
        + (calendar->month * 367U - 362U) / 12U
        + year_in_century * 365U
        + (year_in_century + 3U) / 4U
        - leap_adjust
        + 10956U;
    seconds = calendar->second
        + calendar->minute * 60U
        + calendar->hour * 3600U
        + days * OPEN_CFW_SERVICE_TIME_SECONDS_PER_DAY;
    if (calendar->hundredths > 49U) {
        ++seconds;
    }
    return seconds;
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_CALENDAR_WRAPPER_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_service_time_calendar_to_epoch_wrapper(
    const open_cfw_service_time_calendar *calendar
)
{
    return open_cfw_service_time_calendar_to_epoch(calendar);
}
#endif

static __attribute__((always_inline, unused)) inline int32_t
open_cfw_service_time_timezone_quarters(void)
{
    const volatile uint8_t *configuration =
        OPEN_CFW_SERVICE_TIME_CONFIGURATION;
    return configuration == NULL ? 0 : (int32_t)(int8_t)configuration[8];
}

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_CURRENT_CALENDAR_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_current_calendar_get(
    open_cfw_service_time_calendar *calendar
)
{
    open_cfw_service_time_calendar rtc;
    uint32_t seconds;
    OPEN_CFW_SERVICE_TIME_RTC_GET(&rtc);
    seconds = open_cfw_service_time_calendar_to_epoch(&rtc);
    seconds += (uint32_t)(open_cfw_service_time_timezone_quarters() *
                          OPEN_CFW_SERVICE_TIME_TIMEZONE_UNIT);
    open_cfw_service_time_epoch_to_calendar_configured(seconds, calendar);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_CURRENT_EPOCH_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_service_time_current_epoch_get(void)
{
    open_cfw_service_time_calendar rtc;
    uint32_t seconds;
    OPEN_CFW_SERVICE_TIME_RTC_GET(&rtc);
    seconds = open_cfw_service_time_calendar_to_epoch(&rtc);
    return seconds + (uint32_t)(open_cfw_service_time_timezone_quarters() *
                                OPEN_CFW_SERVICE_TIME_TIMEZONE_UNIT);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_RTC_REFRESH_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_rtc_refresh(void)
{
    open_cfw_service_time_calendar rtc;
    OPEN_CFW_SERVICE_TIME_RTC_GET(&rtc);
    (void)open_cfw_service_time_calendar_to_epoch(&rtc);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_SVC_SYNC_ONLY)
__attribute__((used, noinline))
void SVC_SystemTimeSync(uint32_t unix_seconds, int32_t timezone_quarters)
{
    open_cfw_service_time_calendar calendar;
    (void)timezone_quarters;
    open_cfw_service_time_epoch_to_calendar24(unix_seconds, &calendar);
    (void)OPEN_CFW_SERVICE_TIME_RTC_SET(&calendar);
    open_cfw_service_time_clear_calendar(&calendar);
    open_cfw_service_time_current_calendar_get(&calendar);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_RPC_SYNC_ONLY)
__attribute__((used, noinline))
void RPC_SystemTimeSync(void)
{
    open_cfw_service_time_calendar rtc;
    open_cfw_service_time_peer_message message;
    uint8_t role = OPEN_CFW_SERVICE_TIME_ROLE();
    if (role != 1U) {
        return;
    }
    OPEN_CFW_SERVICE_TIME_RTC_GET(&rtc);
    message.record_id = 0x0080U;
    message.payload_bytes = 8U;
    message.source_role = role;
    message.destination_role = role == 1U ? 2U : 1U;
    message.reserved = 0U;
    message.unix_seconds = open_cfw_service_time_calendar_to_epoch(&rtc);
    message.timezone_quarters = open_cfw_service_time_timezone_quarters();
    (void)OPEN_CFW_SERVICE_TIME_SYNC_SEND(
        0x0100U, &message, sizeof(message), 0U);
    (void)OPEN_CFW_SERVICE_TIME_REMOVE_DELAYED(RPC_SystemTimeSync);
    OPEN_CFW_SERVICE_TIME_PUSH_DELAYED(
        RPC_SystemTimeSync, NULL, 30000U);
}
#endif

#if defined(OPEN_CFW_SERVICE_TIME_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_TIME_SYNC_CALLBACK_ONLY)
__attribute__((used, noinline))
void open_cfw_service_time_sync_callback(void)
{
    if (OPEN_CFW_SERVICE_TIME_ROLE() == 1U) {
        open_cfw_service_time_calendar rtc;
        uint32_t seconds;
        OPEN_CFW_SERVICE_TIME_RTC_GET(&rtc);
        seconds = open_cfw_service_time_calendar_to_epoch(&rtc);
        SVC_SystemTimeSync(seconds, open_cfw_service_time_timezone_quarters());
    }
    (void)OPEN_CFW_SERVICE_TIME_REMOVE_DELAYED(RPC_SystemTimeSync);
    OPEN_CFW_SERVICE_TIME_PUSH_DELAYED(RPC_SystemTimeSync, NULL, 0U);
}
#endif
