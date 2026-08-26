/*
 * OpenCFW clean-room G2 ambient-light policy driver.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Recreated from authenticated linked-object behavior and the public TI
 * OPT3007 SBOS864 register specification.  This file contains no historical
 * Even Realities or TI software source.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_ALS_SELECTOR
#define OPEN_CFW_ALS_SELECTOR 0
#endif

struct open_cfw_als_sync_record {
    uint8_t brightness;
    uint8_t notify_application;
};

struct open_cfw_als_curve_point {
    uint32_t lux_limit;
    uint32_t brightness;
};

static const struct open_cfw_als_curve_point open_cfw_als_curve[6]
    __attribute__((unused)) = {
    {10u, 35u}, {200u, 50u}, {400u, 70u},
    {1000u, 70u}, {1300u, 100u}, {UINT32_MAX, 100u},
};

enum {
    OPEN_CFW_ALS_SCALE_ONE = 1024u,
    OPEN_CFW_ALS_SCALE_MIN = 614u,
    OPEN_CFW_ALS_SCALE_MAX = 1434u,
    OPEN_CFW_ALS_PROCESS_STOPPED = 0u,
    OPEN_CFW_ALS_PROCESS_START = 1u,
    OPEN_CFW_ALS_PROCESS_ADJUST = 2u,
    OPEN_CFW_ALS_PROCESS_POLL = 3u,
    OPEN_CFW_ALS_SYNC_EVENT = 0x10eu,
};

#ifndef OPEN_CFW_ALS_OPENED
#define OPEN_CFW_ALS_OPENED (*(volatile uint32_t *)(uintptr_t)0x200741c0u)
#endif
#ifndef OPEN_CFW_ALS_PROCESS_STATUS
#define OPEN_CFW_ALS_PROCESS_STATUS \
    (*(volatile uint32_t *)(uintptr_t)0x200741c4u)
#endif
#ifndef OPEN_CFW_ALS_RAW_INDEX
#define OPEN_CFW_ALS_RAW_INDEX (*(volatile uint32_t *)(uintptr_t)0x200741c8u)
#endif
#ifndef OPEN_CFW_ALS_RAW_COUNT
#define OPEN_CFW_ALS_RAW_COUNT (*(volatile uint32_t *)(uintptr_t)0x200741ccu)
#endif
#ifndef OPEN_CFW_ALS_DARK_INDEX
#define OPEN_CFW_ALS_DARK_INDEX (*(volatile uint32_t *)(uintptr_t)0x200741d0u)
#endif
#ifndef OPEN_CFW_ALS_DARK_COUNT
#define OPEN_CFW_ALS_DARK_COUNT (*(volatile uint32_t *)(uintptr_t)0x200741d4u)
#endif
#ifndef OPEN_CFW_ALS_EXTREME_DARK
#define OPEN_CFW_ALS_EXTREME_DARK \
    (*(volatile uint32_t *)(uintptr_t)0x200741d8u)
#endif
#ifndef OPEN_CFW_ALS_RAW_VALUE
#define OPEN_CFW_ALS_RAW_VALUE (*(volatile uint32_t *)(uintptr_t)0x200741dcu)
#endif
#ifndef OPEN_CFW_ALS_PEAK_VALUE
#define OPEN_CFW_ALS_PEAK_VALUE (*(volatile uint32_t *)(uintptr_t)0x200741e0u)
#endif
#ifndef OPEN_CFW_ALS_BUCKET
#define OPEN_CFW_ALS_BUCKET (*(volatile uint32_t *)(uintptr_t)0x200741e4u)
#endif
#ifndef OPEN_CFW_ALS_CURVE_BRIGHTNESS
#define OPEN_CFW_ALS_CURVE_BRIGHTNESS \
    (*(volatile uint32_t *)(uintptr_t)0x200741e8u)
#endif
#ifndef OPEN_CFW_ALS_TARGET_BRIGHTNESS
#define OPEN_CFW_ALS_TARGET_BRIGHTNESS \
    (*(volatile uint32_t *)(uintptr_t)0x200741ecu)
#endif
#ifndef OPEN_CFW_ALS_LAST_BRIGHTNESS
#define OPEN_CFW_ALS_LAST_BRIGHTNESS \
    (*(volatile uint32_t *)(uintptr_t)0x200741f0u)
#endif
#ifndef OPEN_CFW_ALS_PREVIOUS_BRIGHTNESS
#define OPEN_CFW_ALS_PREVIOUS_BRIGHTNESS \
    (*(volatile uint32_t *)(uintptr_t)0x200741f4u)
#endif
#ifndef OPEN_CFW_ALS_NOTIFY_APPLICATION
#define OPEN_CFW_ALS_NOTIFY_APPLICATION \
    (*(volatile uint32_t *)(uintptr_t)0x200741f8u)
#endif
#ifndef OPEN_CFW_ALS_LEARN_COUNT
#define OPEN_CFW_ALS_LEARN_COUNT (*(volatile uint32_t *)(uintptr_t)0x200741fcu)
#endif
#ifndef OPEN_CFW_ALS_LEARN_COMPLETE
#define OPEN_CFW_ALS_LEARN_COMPLETE \
    (*(volatile uint32_t *)(uintptr_t)0x20074200u)
#endif
#ifndef OPEN_CFW_ALS_PERSISTED_SCALE
#define OPEN_CFW_ALS_PERSISTED_SCALE \
    (*(volatile uint32_t *)(uintptr_t)0x20000060u)
#endif
#ifndef OPEN_CFW_ALS_SCALE
#define OPEN_CFW_ALS_SCALE (*(volatile uint32_t *)(uintptr_t)0x20000064u)
#endif
#ifndef OPEN_CFW_ALS_PREVIOUS_SCALE
#define OPEN_CFW_ALS_PREVIOUS_SCALE \
    (*(volatile uint32_t *)(uintptr_t)0x20000068u)
#endif
#ifndef OPEN_CFW_ALS_LUX_BASE
#define OPEN_CFW_ALS_LUX_BASE (*(volatile uint32_t *)(uintptr_t)0x200039bcu)
#endif
#ifndef OPEN_CFW_ALS_RAW_SAMPLES
#define OPEN_CFW_ALS_RAW_SAMPLES \
    ((volatile uint32_t *)(uintptr_t)0x20073c98u)
#endif
#ifndef OPEN_CFW_ALS_DARK_SAMPLES
#define OPEN_CFW_ALS_DARK_SAMPLES \
    ((volatile uint32_t *)(uintptr_t)0x20072948u)
#endif
#ifndef OPEN_CFW_ALS_MANUAL_LOCK_TICK
#define OPEN_CFW_ALS_MANUAL_LOCK_TICK \
    (*(volatile uint32_t *)(uintptr_t)0x20003998u)
#endif

void open_cfw_retained_zero(void *destination, uint32_t size);
int32_t open_cfw_retained_sync_send(
    uint32_t event, const void *data, uint32_t size, uint32_t timeout);
float open_cfw_retained_imu_pitch(void);
void open_cfw_retained_sensor_power(uint32_t sensor, uint32_t enabled);
void open_cfw_retained_delay(uint32_t ticks);
void open_cfw_retained_opt3007_assign_register_map(void *device);
int32_t open_cfw_retained_opt3007_field_read(const void *field);
void open_cfw_retained_opt3007_field_write(void *field, uint32_t value);
uint32_t open_cfw_retained_opt3007_register_read(uint32_t reg);
uint32_t open_cfw_retained_brightness_get(void);
uint32_t open_cfw_retained_tick_get(uint32_t source);
int32_t open_cfw_retained_sensor_hub_timer_start(uint32_t ticks);
int32_t open_cfw_retained_sensor_hub_timer_stop(void);
void open_cfw_retained_brightness_apply(uint8_t brightness);
const uint32_t *open_cfw_retained_display_interface(void);
void open_cfw_retained_brightness_notify(void);

#ifndef OPEN_CFW_ALS_ZERO
#define OPEN_CFW_ALS_ZERO(d, n) open_cfw_retained_zero((d), (n))
#endif
#ifndef OPEN_CFW_ALS_SYNC_SEND
#define OPEN_CFW_ALS_SYNC_SEND(e, d, n, t) \
    open_cfw_retained_sync_send((e), (d), (n), (t))
#endif
#ifndef OPEN_CFW_ALS_PITCH
#define OPEN_CFW_ALS_PITCH() open_cfw_retained_imu_pitch()
#endif
#ifndef OPEN_CFW_ALS_SENSOR_POWER
#define OPEN_CFW_ALS_SENSOR_POWER(s, e) open_cfw_retained_sensor_power((s), (e))
#endif
#ifndef OPEN_CFW_ALS_DELAY
#define OPEN_CFW_ALS_DELAY(t) open_cfw_retained_delay((t))
#endif
#ifndef OPEN_CFW_ALS_OPT_DEVICE
#define OPEN_CFW_ALS_OPT_DEVICE ((void *)(uintptr_t)0x20073134u)
#endif
#ifndef OPEN_CFW_ALS_OPT_ASSIGN
#define OPEN_CFW_ALS_OPT_ASSIGN(d) open_cfw_retained_opt3007_assign_register_map((d))
#endif
#ifndef OPEN_CFW_ALS_OPT_MANUFACTURER_FIELD
#define OPEN_CFW_ALS_OPT_MANUFACTURER_FIELD \
    ((const void *)((uintptr_t)OPEN_CFW_ALS_OPT_DEVICE + 0x33u))
#endif
#ifndef OPEN_CFW_ALS_OPT_DEVICE_FIELD
#define OPEN_CFW_ALS_OPT_DEVICE_FIELD \
    ((const void *)((uintptr_t)OPEN_CFW_ALS_OPT_DEVICE + 0x36u))
#endif
#ifndef OPEN_CFW_ALS_OPT_CONFIG_FIELD
#define OPEN_CFW_ALS_OPT_CONFIG_FIELD \
    ((void *)((uintptr_t)OPEN_CFW_ALS_OPT_DEVICE + 0x0cu))
#endif
#ifndef OPEN_CFW_ALS_OPT_RANGE_FIELD
#define OPEN_CFW_ALS_OPT_RANGE_FIELD \
    ((void *)((uintptr_t)OPEN_CFW_ALS_OPT_DEVICE + 0x09u))
#endif
#ifndef OPEN_CFW_ALS_OPT_FIELD_READ
#define OPEN_CFW_ALS_OPT_FIELD_READ(f) open_cfw_retained_opt3007_field_read((f))
#endif
#ifndef OPEN_CFW_ALS_OPT_FIELD_WRITE
#define OPEN_CFW_ALS_OPT_FIELD_WRITE(f, v) \
    open_cfw_retained_opt3007_field_write((f), (v))
#endif
#ifndef OPEN_CFW_ALS_OPT_REGISTER_READ
#define OPEN_CFW_ALS_OPT_REGISTER_READ(r) \
    open_cfw_retained_opt3007_register_read((r))
#endif
#ifndef OPEN_CFW_ALS_BRIGHTNESS_GET
#define OPEN_CFW_ALS_BRIGHTNESS_GET() open_cfw_retained_brightness_get()
#endif
#ifndef OPEN_CFW_ALS_TICK_GET
#define OPEN_CFW_ALS_TICK_GET() open_cfw_retained_tick_get(0u)
#endif
#ifndef OPEN_CFW_ALS_TIMER_START
#define OPEN_CFW_ALS_TIMER_START(t) open_cfw_retained_sensor_hub_timer_start((t))
#endif
#ifndef OPEN_CFW_ALS_TIMER_STOP
#define OPEN_CFW_ALS_TIMER_STOP() open_cfw_retained_sensor_hub_timer_stop()
#endif
#ifndef OPEN_CFW_ALS_BRIGHTNESS_APPLY
#define OPEN_CFW_ALS_BRIGHTNESS_APPLY(v) open_cfw_retained_brightness_apply((v))
#endif
#ifndef OPEN_CFW_ALS_DISPLAY_BRIGHTNESS
static __attribute__((unused)) void open_cfw_als_retained_display_brightness(
    uint8_t brightness)
{
    const uint32_t *interface = open_cfw_retained_display_interface();
    if (interface != NULL && interface[5] != 0u) {
        ((void (*)(uint8_t))(uintptr_t)interface[5])(brightness);
    }
}
#define OPEN_CFW_ALS_DISPLAY_BRIGHTNESS(v) \
    open_cfw_als_retained_display_brightness((v))
#endif
#ifndef OPEN_CFW_ALS_BRIGHTNESS_NOTIFY
#define OPEN_CFW_ALS_BRIGHTNESS_NOTIFY() open_cfw_retained_brightness_notify()
#endif

int32_t open_cfw_als_sync_brightness(uint8_t brightness, uint8_t notify);
uint32_t open_cfw_als_minimum_brightness(void);
uint32_t open_cfw_als_clamp_brightness(uint32_t brightness);
void open_cfw_als_raw_push(uint32_t lux);
void open_cfw_als_dark_push(uint32_t lux);
void open_cfw_als_dark_reset(void);
uint32_t open_cfw_als_extreme_dark_ready(void);
uint32_t open_cfw_als_filter_value_by_pitch(uint32_t lux);
uint32_t open_cfw_als_raw_latest(void);
uint32_t open_cfw_als_raw_peak(void);
void open_cfw_als_update_target_with_extreme_dark_mode(uint32_t lux);
uint32_t open_cfw_als_samples_vary(void);
void open_cfw_als_raw_reset(void);
uint32_t open_cfw_als_bucket_index(uint32_t lux);
uint32_t open_cfw_als_bucket_brightness(uint32_t bucket);
uint32_t open_cfw_als_brightness_for_lux(uint32_t lux);
uint32_t open_cfw_als_apply_scale(uint32_t brightness, uint32_t scale_q10);
uint32_t open_cfw_als_target_for_bucket(uint32_t bucket);
void open_cfw_als_update_target(uint32_t lux);
uint32_t open_cfw_als_calculate_scale(uint32_t target, uint32_t brightness);
void open_cfw_als_learn_scale(uint32_t brightness);
void open_cfw_als_reset_scale_state(void);
int32_t open_cfw_als_publish_brightness(uint32_t brightness, uint8_t notify);
uint32_t open_cfw_als_can_fast_dim(void);
int32_t open_cfw_als_initialize(void);
void open_cfw_als_power_off(void);
uint32_t open_cfw_als_read_data(void);
int32_t open_cfw_als_open(void);
int32_t open_cfw_als_close(void);
uint32_t open_cfw_als_move_toward(
    uint32_t target, uint32_t current, uint32_t step);
void open_cfw_als_timer_start(void);
void open_cfw_als_timer_adjust(void);
void open_cfw_als_timer_polling(void);
void open_cfw_als_timer_handler(void);
int32_t open_cfw_als_sync_handler(
    uint32_t event, const uint8_t *data, uint32_t length);
int32_t open_cfw_als_manual_set_brightness(uint32_t brightness);
void open_cfw_als_set_scale(uint32_t scale_q10);
uint32_t open_cfw_als_get_scale(void);

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 1
__attribute__((noinline)) int32_t open_cfw_als_sync_brightness(
    uint8_t brightness, uint8_t notify)
{
    const struct open_cfw_als_sync_record record = {brightness, notify};
    return OPEN_CFW_ALS_SYNC_SEND(
        OPEN_CFW_ALS_SYNC_EVENT, &record, sizeof(record), 0u);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 2
__attribute__((noinline)) uint32_t open_cfw_als_minimum_brightness(void)
{
    return open_cfw_als_curve[0].brightness;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 3
__attribute__((noinline)) uint32_t open_cfw_als_clamp_brightness(
    uint32_t brightness)
{
    uint32_t minimum = open_cfw_als_minimum_brightness();
    if (brightness < minimum) {
        return minimum;
    }
    return brightness > 100u ? 100u : brightness;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 4
__attribute__((noinline)) void open_cfw_als_raw_push(uint32_t lux)
{
    OPEN_CFW_ALS_RAW_INDEX = (OPEN_CFW_ALS_RAW_INDEX + 1u) % 5u;
    OPEN_CFW_ALS_RAW_SAMPLES[OPEN_CFW_ALS_RAW_INDEX] = lux;
    ++OPEN_CFW_ALS_RAW_COUNT;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 5
__attribute__((noinline)) void open_cfw_als_dark_push(uint32_t lux)
{
    OPEN_CFW_ALS_DARK_INDEX = (OPEN_CFW_ALS_DARK_INDEX + 1u) % 20u;
    OPEN_CFW_ALS_DARK_SAMPLES[OPEN_CFW_ALS_DARK_INDEX] = lux;
    ++OPEN_CFW_ALS_DARK_COUNT;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 6
__attribute__((noinline)) void open_cfw_als_dark_reset(void)
{
    OPEN_CFW_ALS_DARK_COUNT = 0u;
    OPEN_CFW_ALS_DARK_INDEX = 0u;
    OPEN_CFW_ALS_ZERO((void *)OPEN_CFW_ALS_DARK_SAMPLES, 20u * sizeof(uint32_t));
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 7
__attribute__((noinline)) uint32_t open_cfw_als_extreme_dark_ready(void)
{
    uint32_t dark = 0u;
    uint32_t index;
    if (OPEN_CFW_ALS_DARK_COUNT < 20u) {
        return 0u;
    }
    for (index = 0u; index < 20u; ++index) {
        if (OPEN_CFW_ALS_DARK_SAMPLES[index] < 3u) {
            ++dark;
        }
    }
    return dark > 18u;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 8
__attribute__((noinline)) uint32_t open_cfw_als_filter_value_by_pitch(
    uint32_t lux)
{
    return OPEN_CFW_ALS_PITCH() < -30.0f ? OPEN_CFW_ALS_RAW_VALUE : lux;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 9
__attribute__((noinline)) uint32_t open_cfw_als_raw_latest(void)
{
    return OPEN_CFW_ALS_RAW_SAMPLES[OPEN_CFW_ALS_RAW_INDEX];
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 10
__attribute__((noinline)) uint32_t open_cfw_als_raw_peak(void)
{
    uint32_t peak;
    uint32_t index;
    if (OPEN_CFW_ALS_RAW_COUNT < 5u) {
        return open_cfw_als_raw_latest();
    }
    peak = 0u;
    for (index = 0u; index < 5u; ++index) {
        if (peak <= OPEN_CFW_ALS_RAW_SAMPLES[index]) {
            peak = OPEN_CFW_ALS_RAW_SAMPLES[index];
        }
    }
    return peak;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 11
__attribute__((noinline)) void open_cfw_als_update_target_with_extreme_dark_mode(
    uint32_t lux)
{
    if (lux < 11u) {
        if (OPEN_CFW_ALS_EXTREME_DARK == 0u &&
            open_cfw_als_extreme_dark_ready() != 0u) {
            OPEN_CFW_ALS_EXTREME_DARK = 1u;
        }
        if (OPEN_CFW_ALS_EXTREME_DARK != 0u) {
            OPEN_CFW_ALS_BUCKET = 0u;
            OPEN_CFW_ALS_CURVE_BRIGHTNESS = 15u;
            OPEN_CFW_ALS_TARGET_BRIGHTNESS = 15u;
            return;
        }
    } else {
        OPEN_CFW_ALS_EXTREME_DARK = 0u;
    }
    open_cfw_als_update_target(lux);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 12
__attribute__((noinline)) uint32_t open_cfw_als_samples_vary(void)
{
    uint32_t minimum;
    uint32_t maximum;
    uint32_t index;
    if (OPEN_CFW_ALS_RAW_COUNT < 5u) {
        return 0u;
    }
    minimum = OPEN_CFW_ALS_RAW_SAMPLES[0];
    maximum = minimum;
    for (index = 1u; index < 5u; ++index) {
        uint32_t value = OPEN_CFW_ALS_RAW_SAMPLES[index];
        if (maximum <= value) {
            maximum = value;
        }
        if (value <= minimum) {
            minimum = value;
        }
    }
    return (maximum - minimum) > 300u;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 13
__attribute__((noinline)) void open_cfw_als_raw_reset(void)
{
    OPEN_CFW_ALS_RAW_COUNT = 0u;
    OPEN_CFW_ALS_RAW_INDEX = 0u;
    OPEN_CFW_ALS_PEAK_VALUE = 0u;
    OPEN_CFW_ALS_ZERO((void *)OPEN_CFW_ALS_RAW_SAMPLES, 5u * sizeof(uint32_t));
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 14
__attribute__((noinline)) uint32_t open_cfw_als_bucket_index(uint32_t lux)
{
    uint32_t index;
    for (index = 0u; index < 6u; ++index) {
        if (lux <= open_cfw_als_curve[index].lux_limit) {
            return index;
        }
    }
    return 5u;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 15
__attribute__((noinline)) uint32_t open_cfw_als_bucket_brightness(
    uint32_t bucket)
{
    return open_cfw_als_curve[bucket < 6u ? bucket : 5u].brightness;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 16
__attribute__((noinline)) uint32_t open_cfw_als_brightness_for_lux(uint32_t lux)
{
    return open_cfw_als_bucket_brightness(open_cfw_als_bucket_index(lux));
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 17
__attribute__((noinline)) uint32_t open_cfw_als_apply_scale(
    uint32_t brightness, uint32_t scale_q10)
{
    uint32_t minimum = open_cfw_als_minimum_brightness();
    uint64_t adjusted;
    if (brightness <= minimum) {
        return minimum;
    }
    adjusted = (uint64_t)scale_q10 * (brightness - minimum) + 512u;
    return open_cfw_als_clamp_brightness(
        minimum + (uint32_t)(adjusted >> 10u));
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 18
__attribute__((noinline)) uint32_t open_cfw_als_target_for_bucket(
    uint32_t bucket)
{
    uint32_t brightness = open_cfw_als_bucket_brightness(bucket);
    if (bucket + 1u >= 6u) {
        return 100u;
    }
    return open_cfw_als_apply_scale(brightness, OPEN_CFW_ALS_SCALE);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 19
__attribute__((noinline)) void open_cfw_als_update_target(uint32_t lux)
{
    OPEN_CFW_ALS_BUCKET = open_cfw_als_bucket_index(lux);
    OPEN_CFW_ALS_CURVE_BRIGHTNESS =
        open_cfw_als_brightness_for_lux(lux);
    OPEN_CFW_ALS_TARGET_BRIGHTNESS =
        open_cfw_als_target_for_bucket(OPEN_CFW_ALS_BUCKET);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 20
__attribute__((noinline)) uint32_t open_cfw_als_calculate_scale(
    uint32_t target, uint32_t brightness)
{
    uint32_t minimum = open_cfw_als_minimum_brightness();
    uint32_t bounded = open_cfw_als_clamp_brightness(brightness);
    uint32_t numerator;
    uint32_t denominator;
    uint32_t scale;
    if (target <= minimum) {
        return OPEN_CFW_ALS_SCALE_ONE;
    }
    numerator = bounded > minimum ? bounded - minimum : 0u;
    denominator = target - minimum;
    scale = (uint32_t)(((uint64_t)numerator * 1024u + denominator / 2u) /
                       denominator);
    if (scale < OPEN_CFW_ALS_SCALE_MIN) {
        return OPEN_CFW_ALS_SCALE_MIN;
    }
    return scale > OPEN_CFW_ALS_SCALE_MAX ? OPEN_CFW_ALS_SCALE_MAX : scale;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 21
__attribute__((noinline)) void open_cfw_als_learn_scale(uint32_t brightness)
{
    uint32_t minimum = open_cfw_als_minimum_brightness();
    uint32_t learned;
    uint32_t blended;
    if (minimum >= OPEN_CFW_ALS_CURVE_BRIGHTNESS) {
        OPEN_CFW_ALS_LEARN_COMPLETE = 1u;
        OPEN_CFW_ALS_PREVIOUS_SCALE = OPEN_CFW_ALS_SCALE_ONE;
        return;
    }
    learned = open_cfw_als_calculate_scale(
        OPEN_CFW_ALS_CURVE_BRIGHTNESS, brightness);
    blended = (30u * OPEN_CFW_ALS_SCALE + 70u * learned) / 100u;
    if (blended < OPEN_CFW_ALS_SCALE_MIN) {
        blended = OPEN_CFW_ALS_SCALE_MIN;
    } else if (blended > OPEN_CFW_ALS_SCALE_MAX) {
        blended = OPEN_CFW_ALS_SCALE_MAX;
    }
    OPEN_CFW_ALS_SCALE = blended;
    ++OPEN_CFW_ALS_LEARN_COUNT;
    OPEN_CFW_ALS_PREVIOUS_SCALE = learned;
    OPEN_CFW_ALS_LEARN_COMPLETE = 0u;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 22
__attribute__((noinline)) void open_cfw_als_reset_scale_state(void)
{
    uint32_t lux = OPEN_CFW_ALS_PEAK_VALUE != 0u
        ? OPEN_CFW_ALS_PEAK_VALUE : OPEN_CFW_ALS_RAW_VALUE;
    OPEN_CFW_ALS_SCALE = OPEN_CFW_ALS_PERSISTED_SCALE;
    OPEN_CFW_ALS_LEARN_COUNT = 0u;
    OPEN_CFW_ALS_PREVIOUS_SCALE = OPEN_CFW_ALS_SCALE;
    OPEN_CFW_ALS_LEARN_COMPLETE = 0u;
    open_cfw_als_update_target(lux);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 23
__attribute__((noinline)) int32_t open_cfw_als_publish_brightness(
    uint32_t brightness, uint8_t notify)
{
    OPEN_CFW_ALS_LAST_BRIGHTNESS = brightness;
    OPEN_CFW_ALS_PREVIOUS_BRIGHTNESS = brightness;
    OPEN_CFW_ALS_NOTIFY_APPLICATION = notify != 0u;
    return open_cfw_als_sync_brightness((uint8_t)brightness, notify != 0u);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 24
__attribute__((noinline)) uint32_t open_cfw_als_can_fast_dim(void)
{
    uint32_t threshold;
    if (OPEN_CFW_ALS_BUCKET >= 2u) {
        return 0u;
    }
    threshold = open_cfw_als_apply_scale(
        open_cfw_als_bucket_brightness(1u), OPEN_CFW_ALS_SCALE);
    return threshold >= OPEN_CFW_ALS_TARGET_BRIGHTNESS &&
           threshold >= OPEN_CFW_ALS_LAST_BRIGHTNESS;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 25
__attribute__((noinline)) int32_t open_cfw_als_initialize(void)
{
    int32_t manufacturer;
    int32_t device;
    OPEN_CFW_ALS_SENSOR_POWER(9u, 1u);
    OPEN_CFW_ALS_DELAY(5u);
    OPEN_CFW_ALS_OPT_ASSIGN(OPEN_CFW_ALS_OPT_DEVICE);
    manufacturer = OPEN_CFW_ALS_OPT_FIELD_READ(
        OPEN_CFW_ALS_OPT_MANUFACTURER_FIELD);
    device = OPEN_CFW_ALS_OPT_FIELD_READ(OPEN_CFW_ALS_OPT_DEVICE_FIELD);
    if (manufacturer != 0x5449 || device != 0x3001) {
        return -1;
    }
    OPEN_CFW_ALS_OPT_FIELD_WRITE(OPEN_CFW_ALS_OPT_CONFIG_FIELD, 3u);
    OPEN_CFW_ALS_OPT_FIELD_WRITE(OPEN_CFW_ALS_OPT_RANGE_FIELD, 0u);
    return 0;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 26
__attribute__((noinline)) void open_cfw_als_power_off(void)
{
    OPEN_CFW_ALS_SENSOR_POWER(9u, 0u);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 27
__attribute__((noinline)) uint32_t open_cfw_als_read_data(void)
{
    uint32_t encoded = OPEN_CFW_ALS_OPT_REGISTER_READ(0u);
    uint32_t raw = (encoded & 0xfffu) << ((encoded >> 12u) & 0x0fu);
    uint32_t lux;
    if (OPEN_CFW_ALS_LUX_BASE == 0u) {
        lux = raw / 10u;
    } else {
        lux = (uint32_t)(((uint64_t)OPEN_CFW_ALS_LUX_BASE * raw) / 1000000u);
    }
    return open_cfw_als_filter_value_by_pitch(lux);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 28
__attribute__((noinline)) int32_t open_cfw_als_open(void)
{
    if (OPEN_CFW_ALS_OPENED != 0u) {
        return -1;
    }
    if (open_cfw_als_initialize() != 0) {
        return -1;
    }
    OPEN_CFW_ALS_OPENED = 1u;
    OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_START;
    OPEN_CFW_ALS_RAW_VALUE = 0u;
    OPEN_CFW_ALS_PEAK_VALUE = 0u;
    OPEN_CFW_ALS_BUCKET = 0u;
    OPEN_CFW_ALS_CURVE_BRIGHTNESS = OPEN_CFW_ALS_BRIGHTNESS_GET();
    OPEN_CFW_ALS_TARGET_BRIGHTNESS = 0u;
    OPEN_CFW_ALS_LAST_BRIGHTNESS = OPEN_CFW_ALS_BRIGHTNESS_GET();
    OPEN_CFW_ALS_PREVIOUS_BRIGHTNESS = OPEN_CFW_ALS_LAST_BRIGHTNESS;
    OPEN_CFW_ALS_NOTIFY_APPLICATION = 0u;
    open_cfw_als_reset_scale_state();
    open_cfw_als_raw_reset();
    open_cfw_als_dark_reset();
    (void)OPEN_CFW_ALS_TIMER_START(110u);
    return 0;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 29
__attribute__((noinline)) int32_t open_cfw_als_close(void)
{
    if (OPEN_CFW_ALS_OPENED == 0u) {
        return -1;
    }
    OPEN_CFW_ALS_OPENED = 0u;
    OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_STOPPED;
    open_cfw_als_power_off();
    (void)OPEN_CFW_ALS_TIMER_STOP();
    return 0;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 30
__attribute__((noinline)) uint32_t open_cfw_als_move_toward(
    uint32_t target, uint32_t current, uint32_t step)
{
    if (current < target) {
        return step <= 100u - current && current + step <= target
            ? current + step : target;
    }
    if (current > target && step <= current && target <= current - step) {
        return current - step;
    }
    return target;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 31
__attribute__((noinline)) void open_cfw_als_timer_start(void)
{
    uint32_t lux;
    OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_POLL;
    (void)OPEN_CFW_ALS_TIMER_START(1000u);
    lux = open_cfw_als_read_data();
    OPEN_CFW_ALS_RAW_VALUE = lux;
    if (lux == 0u) {
        return;
    }
    open_cfw_als_raw_push(lux);
    open_cfw_als_dark_push(lux);
    OPEN_CFW_ALS_PEAK_VALUE = lux;
    open_cfw_als_update_target_with_extreme_dark_mode(lux);
    if (OPEN_CFW_ALS_MANUAL_LOCK_TICK == 0u) {
        (void)open_cfw_als_publish_brightness(
            OPEN_CFW_ALS_TARGET_BRIGHTNESS, 1u);
    }
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 32
__attribute__((noinline)) void open_cfw_als_timer_adjust(void)
{
    uint32_t current;
    uint32_t next;
    uint32_t step = 2u;
    if (OPEN_CFW_ALS_MANUAL_LOCK_TICK != 0u) {
        OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_POLL;
        (void)OPEN_CFW_ALS_TIMER_START(1000u);
        return;
    }
    current = OPEN_CFW_ALS_BRIGHTNESS_GET();
    OPEN_CFW_ALS_LAST_BRIGHTNESS = current;
    if (OPEN_CFW_ALS_TARGET_BRIGHTNESS == current) {
        OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_POLL;
        (void)OPEN_CFW_ALS_TIMER_START(1000u);
        (void)open_cfw_als_publish_brightness(current, 1u);
        return;
    }
    if (OPEN_CFW_ALS_TARGET_BRIGHTNESS < current &&
        open_cfw_als_can_fast_dim() != 0u) {
        step = 5u;
    }
    next = open_cfw_als_move_toward(
        OPEN_CFW_ALS_TARGET_BRIGHTNESS, current, step);
    (void)open_cfw_als_publish_brightness(next, 0u);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 33
__attribute__((noinline)) void open_cfw_als_timer_polling(void)
{
    uint32_t lux = open_cfw_als_read_data();
    uint32_t current;
    OPEN_CFW_ALS_RAW_VALUE = lux;
    open_cfw_als_raw_push(lux);
    open_cfw_als_dark_push(lux);
    OPEN_CFW_ALS_PEAK_VALUE = open_cfw_als_raw_peak();
    open_cfw_als_update_target_with_extreme_dark_mode(
        OPEN_CFW_ALS_PEAK_VALUE);
    current = OPEN_CFW_ALS_BRIGHTNESS_GET();
    OPEN_CFW_ALS_LAST_BRIGHTNESS = current;
    if (OPEN_CFW_ALS_MANUAL_LOCK_TICK != 0u) {
        uint32_t elapsed = OPEN_CFW_ALS_TICK_GET() - OPEN_CFW_ALS_MANUAL_LOCK_TICK;
        if (open_cfw_als_samples_vary() == 0u && elapsed < 0xa8c1u) {
            return;
        }
        OPEN_CFW_ALS_MANUAL_LOCK_TICK = 0u;
    }
    if (OPEN_CFW_ALS_TARGET_BRIGHTNESS != current) {
        OPEN_CFW_ALS_PROCESS_STATUS = OPEN_CFW_ALS_PROCESS_ADJUST;
        (void)OPEN_CFW_ALS_TIMER_START(200u);
    }
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 34
__attribute__((noinline)) void open_cfw_als_timer_handler(void)
{
    if (OPEN_CFW_ALS_PROCESS_STATUS == OPEN_CFW_ALS_PROCESS_START) {
        open_cfw_als_timer_start();
    } else if (OPEN_CFW_ALS_PROCESS_STATUS == OPEN_CFW_ALS_PROCESS_ADJUST) {
        open_cfw_als_timer_adjust();
    } else if (OPEN_CFW_ALS_PROCESS_STATUS == OPEN_CFW_ALS_PROCESS_POLL) {
        open_cfw_als_timer_polling();
    }
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 35
__attribute__((noinline)) int32_t open_cfw_als_sync_handler(
    uint32_t event, const uint8_t *data, uint32_t length)
{
    uint8_t brightness;
    uint8_t notify;
    (void)event;
    if (data == NULL || length != sizeof(struct open_cfw_als_sync_record)) {
        return -1;
    }
    brightness = data[0];
    notify = data[1] != 0u;
    OPEN_CFW_ALS_BRIGHTNESS_APPLY(brightness);
    OPEN_CFW_ALS_DISPLAY_BRIGHTNESS(brightness);
    if (notify != 0u) {
        OPEN_CFW_ALS_BRIGHTNESS_NOTIFY();
    }
    return 0;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 36
__attribute__((noinline)) int32_t open_cfw_als_manual_set_brightness(
    uint32_t brightness)
{
    uint32_t lux;
    if (OPEN_CFW_ALS_OPENED == 0u) {
        return 1;
    }
    if (brightness > 100u) {
        brightness = 100u;
    } else if (brightness < 2u) {
        brightness = 2u;
    }
    brightness &= ~1u;
    lux = OPEN_CFW_ALS_PEAK_VALUE != 0u
        ? OPEN_CFW_ALS_PEAK_VALUE : OPEN_CFW_ALS_RAW_VALUE;
    open_cfw_als_update_target(lux);
    open_cfw_als_learn_scale(brightness);
    open_cfw_als_update_target(lux);
    open_cfw_als_raw_reset();
    OPEN_CFW_ALS_LAST_BRIGHTNESS = brightness;
    OPEN_CFW_ALS_PREVIOUS_BRIGHTNESS = brightness;
    OPEN_CFW_ALS_NOTIFY_APPLICATION = 1u;
    return 0;
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 37
__attribute__((noinline)) void open_cfw_als_set_scale(uint32_t scale_q10)
{
    uint32_t lux = OPEN_CFW_ALS_PEAK_VALUE != 0u
        ? OPEN_CFW_ALS_PEAK_VALUE : OPEN_CFW_ALS_RAW_VALUE;
    if (scale_q10 < OPEN_CFW_ALS_SCALE_MIN) {
        scale_q10 = OPEN_CFW_ALS_SCALE_MIN;
    } else if (scale_q10 > OPEN_CFW_ALS_SCALE_MAX) {
        scale_q10 = OPEN_CFW_ALS_SCALE_MAX;
    }
    OPEN_CFW_ALS_PERSISTED_SCALE = scale_q10;
    OPEN_CFW_ALS_SCALE = scale_q10;
    OPEN_CFW_ALS_PREVIOUS_SCALE = scale_q10;
    OPEN_CFW_ALS_LEARN_COMPLETE = 0u;
    open_cfw_als_update_target(lux);
}
#endif

#if OPEN_CFW_ALS_SELECTOR == 0 || OPEN_CFW_ALS_SELECTOR == 38
__attribute__((noinline)) uint32_t open_cfw_als_get_scale(void)
{
    return OPEN_CFW_ALS_SCALE;
}
#endif
