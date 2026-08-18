#ifndef OPENR1_SDK_RTC_H
#define OPENR1_SDK_RTC_H

#include <stdbool.h>
#include <stdint.h>

#include "sdk_errors.h"
#include "rtc_device/rtc_device.h"

ret_code_t openr1_rtc_initialize(void);
bool openr1_rtc_adopt_phone_time(
    uint32_t epoch_seconds, int16_t utc_offset_minutes);
bool openr1_rtc_snapshot(rtc_device_time_block *out);

#endif
