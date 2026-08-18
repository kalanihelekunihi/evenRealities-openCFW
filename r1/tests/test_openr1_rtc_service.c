#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1_rtc_service.h"
#include "time_calendar/time_calendar.h"

static size_t init_calls;
static size_t tick_enable_calls;
static size_t enable_calls;
static const void *instance_seen;
static uint16_t prescaler_seen;
static uint8_t priority_seen;

static bool breakdown(uint32_t epoch, rtc_device_broken_down *out) {
    time_calendar_broken_down broken;
    if (time_calendar_unix_to_broken_down(epoch, &broken) != &broken) {
        return false;
    }
    *out = (rtc_device_broken_down){
        (int32_t)broken.second, (int32_t)broken.minute,
        (int32_t)broken.hour, (int32_t)broken.day,
        (int32_t)broken.month, (int32_t)broken.year,
        (int32_t)broken.weekday, (int32_t)broken.year_day,
    };
    return true;
}

static uint32_t rtc_init(void *instance, uint16_t prescaler, uint8_t priority) {
    ++init_calls;
    instance_seen = instance;
    prescaler_seen = prescaler;
    priority_seen = priority;
    return 0u;
}

static void tick_enable(void *instance, bool enable) {
    assert(instance == instance_seen);
    assert(enable);
    ++tick_enable_calls;
}

static void rtc_enable(void *instance) {
    assert(instance == instance_seen);
    ++enable_calls;
}

void test_openr1_rtc_service(void) {
    openr1_rtc_service service;
    const rtc_device_providers providers = {
        breakdown, rtc_init, tick_enable, rtc_enable, NULL,
    };
    const uintptr_t instance[2] = {UINT32_C(0x40024000), UINT32_C(0x00040424)};

    assert(openr1_rtc_service_initialize(
        NULL, &providers, instance, sizeof(instance)) ==
        RTC_DEVICE_STATUS_BAD_ARGUMENT);
    assert(openr1_rtc_service_initialize(
        &service, &providers, instance, sizeof(uintptr_t)) ==
        RTC_DEVICE_STATUS_BAD_ARGUMENT);

    init_calls = 0u;
    tick_enable_calls = 0u;
    enable_calls = 0u;
    assert(openr1_rtc_service_initialize(
        &service, &providers, instance, sizeof(instance)) ==
        RTC_DEVICE_STATUS_OK);
    assert(service.initialized);
    assert(init_calls == 1u && tick_enable_calls == 1u && enable_calls == 1u);
    assert(prescaler_seen == 4095u && priority_seen == 6u);
    assert(generic_device_registry_find(&service.registry, "sys rtc") ==
           &service.registry_record);

    assert(openr1_rtc_service_set_time(
        &service, UINT32_C(1723852800), -300) == RTC_DEVICE_STATUS_OK);
    for (size_t tick = 0u; tick < RTC_DEVICE_TICKS_PER_SECOND; ++tick) {
        openr1_rtc_service_tick(&service);
    }
    rtc_device_time_block snapshot = {0};
    assert(openr1_rtc_service_snapshot(&service, &snapshot) ==
           RTC_DEVICE_STATUS_OK);
    assert(snapshot.epoch_seconds == UINT32_C(1723852801));
    assert(snapshot.millisecond_value ==
           (uint64_t)(UINT32_C(1723852801) * UINT32_C(1000)));
    assert(service.rtc.state.utc_offset_minutes == -300);

    rtc_device_time_block via_veneer = {0};
    assert(rtc_device_ops_control(&service.rtc, &via_veneer) == 1u);
    assert(via_veneer.epoch_seconds == snapshot.epoch_seconds);
    assert(rtc_device_ops_set_time(
        &service.rtc, UINT32_C(1723852900), 60) == 1u);
    assert(service.rtc.state.epoch_seconds == UINT32_C(1723852900));
    assert(service.rtc.state.utc_offset_minutes == 60);
}
