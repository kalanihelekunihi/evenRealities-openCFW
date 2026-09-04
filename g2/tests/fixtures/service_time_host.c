/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/service_time.h"

static uint8_t host_configuration[12];
static uint32_t host_format_mode;
static uint8_t host_role;
static open_cfw_service_time_calendar host_rtc;
static open_cfw_service_time_calendar host_last_set;
static unsigned int host_get_calls;
static unsigned int host_set_calls;
static unsigned int host_send_calls;
static unsigned int host_remove_calls;
static unsigned int host_push_calls;
static uint32_t host_send_record;
static uint32_t host_send_size;
static uint32_t host_send_options;
static open_cfw_service_time_peer_message host_message;
static void (*host_removed_callback)(void);
static void (*host_pushed_callback)(void);
static void *host_pushed_argument;
static uint32_t host_pushed_delay;

static void host_rtc_get(open_cfw_service_time_calendar *calendar)
{
    ++host_get_calls;
    *calendar = host_rtc;
}

static uint32_t host_rtc_set(
    const open_cfw_service_time_calendar *calendar
)
{
    ++host_set_calls;
    host_last_set = *calendar;
    host_rtc = *calendar;
    return 0U;
}

static int host_sync_send(
    uint32_t record, const void *payload, uint32_t size, uint32_t options
)
{
    ++host_send_calls;
    host_send_record = record;
    host_send_size = size;
    host_send_options = options;
    memcpy(&host_message, payload, sizeof(host_message));
    return 0;
}

static uint8_t host_remove_delayed(void (*callback)(void))
{
    ++host_remove_calls;
    host_removed_callback = callback;
    return 1U;
}

static void host_push_delayed(
    void (*callback)(void), void *argument, uint32_t delay
)
{
    ++host_push_calls;
    host_pushed_callback = callback;
    host_pushed_argument = argument;
    host_pushed_delay = delay;
}

#define OPEN_CFW_SERVICE_TIME_CONFIGURATION host_configuration
#define OPEN_CFW_SERVICE_TIME_FORMAT_MODE() host_format_mode
#define OPEN_CFW_SERVICE_TIME_RTC_GET(calendar) host_rtc_get((calendar))
#define OPEN_CFW_SERVICE_TIME_RTC_SET(calendar) host_rtc_set((calendar))
#define OPEN_CFW_SERVICE_TIME_ROLE() host_role
#define OPEN_CFW_SERVICE_TIME_SYNC_SEND(record, payload, size, options) \
    host_sync_send((record), (payload), (size), (options))
#define OPEN_CFW_SERVICE_TIME_REMOVE_DELAYED(callback) \
    host_remove_delayed((callback))
#define OPEN_CFW_SERVICE_TIME_PUSH_DELAYED(callback, argument, delay) \
    host_push_delayed((callback), (argument), (delay))
#include "../../components/apollo_main/core_overlay/service_time.c"

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

static void require_date(
    const open_cfw_service_time_calendar *calendar,
    uint32_t year, uint32_t month, uint32_t day,
    uint32_t hour, uint32_t minute, uint32_t second
)
{
    require(calendar->year == year - 2000U);
    require(calendar->month == month);
    require(calendar->day == day);
    require(calendar->hour == hour);
    require(calendar->minute == minute);
    require(calendar->second == second);
}

static void reset_calls(void)
{
    host_get_calls = 0U;
    host_set_calls = 0U;
    host_send_calls = 0U;
    host_remove_calls = 0U;
    host_push_calls = 0U;
    host_removed_callback = NULL;
    host_pushed_callback = NULL;
    host_pushed_argument = (void *)(uintptr_t)1U;
    host_pushed_delay = 0U;
}

int main(void)
{
    open_cfw_service_time_calendar calendar;
    uint32_t leap_epoch = OPEN_CFW_SERVICE_TIME_UNIX_2000
        + 59U * OPEN_CFW_SERVICE_TIME_SECONDS_PER_DAY
        + 12U * 3600U + 34U * 60U + 56U;

    memset(&calendar, 0xA5, sizeof(calendar));
    open_cfw_service_time_epoch_to_calendar24(0U, &calendar);
    require_date(&calendar, 2000U, 1U, 1U, 0U, 0U, 0U);
    require(calendar.weekday == 6U && calendar.read_error == 0U);
    require(calendar.hundredths == 0U);

    open_cfw_service_time_epoch_to_calendar24(leap_epoch, &calendar);
    require_date(&calendar, 2000U, 2U, 29U, 12U, 34U, 56U);
    require(open_cfw_service_time_calendar_to_epoch(&calendar) == leap_epoch);
    calendar.hundredths = 50U;
    require(open_cfw_service_time_calendar_to_epoch_wrapper(&calendar)
            == leap_epoch + 1U);

    host_format_mode = 1U;
    open_cfw_service_time_epoch_to_calendar_configured(
        OPEN_CFW_SERVICE_TIME_UNIX_2000, &calendar);
    require(calendar.hour == 12U);
    open_cfw_service_time_epoch_to_calendar_configured(
        OPEN_CFW_SERVICE_TIME_UNIX_2000 + 13U * 3600U, &calendar);
    require(calendar.hour == 1U);
    host_format_mode = 0U;

    open_cfw_service_time_epoch_to_calendar(
        OPEN_CFW_SERVICE_TIME_UNIX_2000 + 86400U, &calendar);
    require_date(&calendar, 2000U, 1U, 2U, 0U, 0U, 0U);

    open_cfw_service_time_epoch_to_calendar24(
        OPEN_CFW_SERVICE_TIME_UNIX_2000, &host_rtc);
    host_configuration[8] = 4U;
    reset_calls();
    open_cfw_service_time_current_calendar_get(&calendar);
    require(host_get_calls == 1U);
    require_date(&calendar, 2000U, 1U, 1U, 1U, 0U, 0U);
    require(open_cfw_service_time_current_epoch_get()
            == OPEN_CFW_SERVICE_TIME_UNIX_2000 + 3600U);
    require(host_get_calls == 2U);
    open_cfw_service_time_rtc_refresh();
    require(host_get_calls == 3U);

    reset_calls();
    SVC_SystemTimeSync(leap_epoch, -4);
    require(host_set_calls == 1U && host_get_calls == 1U);
    require_date(&host_last_set, 2000U, 2U, 29U, 12U, 34U, 56U);

    host_role = 2U;
    reset_calls();
    RPC_SystemTimeSync();
    require(host_send_calls == 0U && host_get_calls == 0U);
    require(host_remove_calls == 0U && host_push_calls == 0U);

    host_role = 1U;
    host_configuration[8] = (uint8_t)(int8_t)-4;
    reset_calls();
    RPC_SystemTimeSync();
    require(host_get_calls == 1U && host_send_calls == 1U);
    require(host_send_record == 0x100U && host_send_size == 16U);
    require(host_send_options == 0U);
    require(host_message.record_id == 0x80U);
    require(host_message.payload_bytes == 8U);
    require(host_message.source_role == 1U);
    require(host_message.destination_role == 2U);
    require(host_message.unix_seconds == leap_epoch);
    require(host_message.timezone_quarters == -4);
    require(host_remove_calls == 1U && host_push_calls == 1U);
    require(host_removed_callback == RPC_SystemTimeSync);
    require(host_pushed_callback == RPC_SystemTimeSync);
    require(host_pushed_argument == NULL && host_pushed_delay == 30000U);

    reset_calls();
    open_cfw_service_time_sync_callback();
    require(host_get_calls == 2U && host_set_calls == 1U);
    require(host_remove_calls == 1U && host_push_calls == 1U);
    require(host_pushed_callback == RPC_SystemTimeSync);
    require(host_pushed_delay == 0U);

    host_role = 2U;
    reset_calls();
    open_cfw_service_time_sync_callback();
    require(host_get_calls == 0U && host_set_calls == 0U);
    require(host_remove_calls == 1U && host_push_calls == 1U);
    return 0;
}
