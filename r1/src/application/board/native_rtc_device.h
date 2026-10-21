#ifndef R1_NATIVE_RTC_DEVICE_H
#define R1_NATIVE_RTC_DEVICE_H

#include "rtc_device/rtc_device.h"
#include "../registry/stock_registry.h"
typedef struct {uintptr_t registers;int8_t irq;uint8_t instance_id,channels,padding;} r1_rtc_instance;
typedef struct {const char *name;uint8_t opened,padding[3];rtc_device_calendar calendar;r1_rtc_instance rtc;rtc_device_alarm_callback callback;generic_device_registry_device registry;} r1_rtc_native_record;
typedef struct {int16_t offset;uint16_t divider;uint32_t epoch;} r1_rtc_counter_state;
extern r1_rtc_counter_state r1_rtc_counter;
extern r1_rtc_native_record r1_rtc_record;
extern const char r1_rtc_device_name[];
#endif
