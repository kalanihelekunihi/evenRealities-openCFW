#include "openr1_rtc.h"

#include <time.h>

#include "app_error.h"
#include "nrf_error.h"
#include "nrfx_rtc.h"

#include "openr1_rtc_service.h"

static openr1_rtc_service rtc_service;
static const nrfx_rtc_t rtc2_instance = NRFX_RTC_INSTANCE(2);

static bool breakdown(uint32_t epoch_seconds, rtc_device_broken_down *out) {
    if (out == NULL) {
        return false;
    }
    const time_t moment = (time_t)epoch_seconds;
    struct tm value;
    if (gmtime_r(&moment, &value) == NULL) {
        return false;
    }
    *out = (rtc_device_broken_down){
        value.tm_sec, value.tm_min, value.tm_hour, value.tm_mday,
        value.tm_mon, value.tm_year, value.tm_wday, value.tm_yday,
    };
    return true;
}

static void rtc2_event(nrfx_rtc_int_type_t event) {
    if (event == NRFX_RTC_INT_TICK) {
        openr1_rtc_service_tick(&rtc_service);
    }
}

static uint32_t rtc2_initialize(
    void *instance, uint16_t prescaler, uint8_t irq_priority) {
    const nrfx_rtc_config_t configuration = {
        .prescaler = prescaler,
        .interrupt_priority = irq_priority,
        .tick_latency = 0u,
        .reliable = false,
    };
    return nrfx_rtc_init(
        (const nrfx_rtc_t *)instance, &configuration, rtc2_event);
}

static void rtc2_tick_enable(void *instance, bool enable) {
    nrfx_rtc_tick_enable((const nrfx_rtc_t *)instance, enable);
}

static void rtc2_enable(void *instance) {
    nrfx_rtc_enable((const nrfx_rtc_t *)instance);
}

static void rtc2_fault(void) {
    APP_ERROR_HANDLER(NRF_ERROR_INTERNAL);
}

ret_code_t openr1_rtc_initialize(void) {
    const rtc_device_providers providers = {
        breakdown,
        rtc2_initialize,
        rtc2_tick_enable,
        rtc2_enable,
        rtc2_fault,
    };
    return openr1_rtc_service_initialize(
        &rtc_service, &providers, &rtc2_instance, sizeof(rtc2_instance));
}

bool openr1_rtc_adopt_phone_time(
    uint32_t epoch_seconds, int16_t utc_offset_minutes) {
    return openr1_rtc_service_set_time(
        &rtc_service, epoch_seconds, utc_offset_minutes) ==
        RTC_DEVICE_STATUS_OK;
}

bool openr1_rtc_snapshot(rtc_device_time_block *out) {
    return openr1_rtc_service_snapshot(&rtc_service, out) ==
        RTC_DEVICE_STATUS_OK;
}

typedef struct {
    bool (*adopt_phone_time)(uint32_t, int16_t);
    bool (*snapshot)(rtc_device_time_block *);
} openr1_rtc_api;

__attribute__((used, section(".openr1_rtc_api")))
static const openr1_rtc_api retained_rtc_api = {
    openr1_rtc_adopt_phone_time,
    openr1_rtc_snapshot,
};
