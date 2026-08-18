#ifndef OPENR1_RTC_ZEPHYR_H
#define OPENR1_RTC_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "rtc_device/rtc_device.h"

int openr1_rtc_zephyr_initialize(void);
bool openr1_rtc_zephyr_adopt_phone_time(
    uint32_t epoch_seconds, int16_t utc_offset_minutes);
bool openr1_rtc_zephyr_snapshot(rtc_device_time_block *out);

#endif
