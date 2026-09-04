/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_SERVICE_TIME_H
#define OPEN_CFW_SERVICE_TIME_H

#include <stdint.h>

#define OPEN_CFW_SERVICE_TIME_UNIX_2000 946684800U
#define OPEN_CFW_SERVICE_TIME_SECONDS_PER_DAY 86400U
#define OPEN_CFW_SERVICE_TIME_TIMEZONE_UNIT 900

typedef struct {
    uint32_t read_error;
    uint32_t weekday;
    uint32_t century_bit;
    uint32_t year;
    uint32_t month;
    uint32_t day;
    uint32_t hour;
    uint32_t minute;
    uint32_t second;
    uint32_t hundredths;
} open_cfw_service_time_calendar;

typedef struct {
    uint16_t record_id;
    uint16_t payload_bytes;
    uint8_t source_role;
    uint8_t destination_role;
    uint16_t reserved;
    uint32_t unix_seconds;
    int32_t timezone_quarters;
} open_cfw_service_time_peer_message;

void open_cfw_service_time_epoch_to_calendar24(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
);
void open_cfw_service_time_epoch_to_calendar_configured(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
);
void open_cfw_service_time_epoch_to_calendar(
    uint32_t unix_seconds, open_cfw_service_time_calendar *calendar
);
uint32_t open_cfw_service_time_calendar_to_epoch(
    const open_cfw_service_time_calendar *calendar
);
uint32_t open_cfw_service_time_calendar_to_epoch_wrapper(
    const open_cfw_service_time_calendar *calendar
);
void open_cfw_service_time_current_calendar_get(
    open_cfw_service_time_calendar *calendar
);
uint32_t open_cfw_service_time_current_epoch_get(void);
void open_cfw_service_time_rtc_refresh(void);
void SVC_SystemTimeSync(uint32_t unix_seconds, int32_t timezone_quarters);
void RPC_SystemTimeSync(void);
void open_cfw_service_time_sync_callback(void);

#endif
