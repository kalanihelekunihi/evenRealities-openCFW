#include "openr1_rtc_zephyr.h"

#include <errno.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/counter.h>
#include <zephyr/kernel.h>

#include "openr1_rtc_service.h"
#include "time_calendar/time_calendar.h"

#define OPENR1_RTC_CHANNEL 0u
#define OPENR1_RTC_PRESCALER 4095u
#define OPENR1_RTC_IRQ_PRIORITY 6u

typedef struct {
    const struct device *device;
    uint32_t peripheral_number;
} openr1_rtc_instance;

static openr1_rtc_service rtc_service;
static const openr1_rtc_instance rtc2_instance = {
    DEVICE_DT_GET(DT_NODELABEL(rtc2)),
    2u,
};
static int backend_error;
static bool tick_requested;

static bool breakdown(uint32_t epoch_seconds, rtc_device_broken_down *out) {
    if (out == NULL) {
        return false;
    }
    time_calendar_broken_down value;
    if (time_calendar_unix_to_broken_down(epoch_seconds, &value) != &value) {
        return false;
    }
    *out = (rtc_device_broken_down){
        (int32_t)value.second, (int32_t)value.minute,
        (int32_t)value.hour, (int32_t)value.day,
        (int32_t)value.month, (int32_t)value.year,
        (int32_t)value.weekday, (int32_t)value.year_day,
    };
    return true;
}

static void rtc2_alarm(
    const struct device *device, uint8_t channel,
    uint32_t ticks, void *context);

static void arm_tick(const struct device *device) {
    const struct counter_alarm_cfg alarm = {
        .callback = rtc2_alarm,
        .ticks = 1u,
        .user_data = &rtc_service,
        .flags = 0u,
    };
    const int error = counter_set_channel_alarm(
        device, OPENR1_RTC_CHANNEL, &alarm);
    if (error != 0 && backend_error == 0) {
        backend_error = error;
    }
}

static void rtc2_alarm(
    const struct device *device, uint8_t channel,
    uint32_t ticks, void *context) {
    (void)channel;
    (void)ticks;
    openr1_rtc_service_tick((openr1_rtc_service *)context);
    arm_tick(device);
}

static uint32_t rtc2_initialize(
    void *instance, uint16_t prescaler, uint8_t irq_priority) {
    const openr1_rtc_instance *rtc = (const openr1_rtc_instance *)instance;
    if (rtc == NULL || rtc->device == NULL ||
            !device_is_ready(rtc->device) || rtc->peripheral_number != 2u ||
            prescaler != OPENR1_RTC_PRESCALER ||
            irq_priority != OPENR1_RTC_IRQ_PRIORITY) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    return RTC_DEVICE_STATUS_OK;
}

static void rtc2_tick_enable(void *instance, bool enable) {
    (void)instance;
    tick_requested = enable;
}

static void rtc2_enable(void *instance) {
    const openr1_rtc_instance *rtc = (const openr1_rtc_instance *)instance;
    if (rtc == NULL || !tick_requested) {
        backend_error = -EINVAL;
        return;
    }
    backend_error = counter_start(rtc->device);
    if (backend_error == 0) {
        arm_tick(rtc->device);
    }
}

static void rtc2_fault(void) {
    k_panic();
}

int openr1_rtc_zephyr_initialize(void) {
    const rtc_device_providers providers = {
        breakdown,
        rtc2_initialize,
        rtc2_tick_enable,
        rtc2_enable,
        rtc2_fault,
    };
    backend_error = 0;
    tick_requested = false;
    const uint32_t status = openr1_rtc_service_initialize(
        &rtc_service, &providers, &rtc2_instance, sizeof(rtc2_instance));
    if (status != RTC_DEVICE_STATUS_OK) {
        return -EIO;
    }
    return backend_error;
}

bool openr1_rtc_zephyr_adopt_phone_time(
    uint32_t epoch_seconds, int16_t utc_offset_minutes) {
    return openr1_rtc_service_set_time(
        &rtc_service, epoch_seconds, utc_offset_minutes) ==
        RTC_DEVICE_STATUS_OK;
}

bool openr1_rtc_zephyr_snapshot(rtc_device_time_block *out) {
    return openr1_rtc_service_snapshot(&rtc_service, out) ==
        RTC_DEVICE_STATUS_OK;
}

typedef struct {
    bool (*adopt_phone_time)(uint32_t, int16_t);
    bool (*snapshot)(rtc_device_time_block *);
} openr1_rtc_zephyr_api;

__attribute__((used, section(".openr1_platform_api")))
static const openr1_rtc_zephyr_api rtc_zephyr_api = {
    openr1_rtc_zephyr_adopt_phone_time,
    openr1_rtc_zephyr_snapshot,
};
