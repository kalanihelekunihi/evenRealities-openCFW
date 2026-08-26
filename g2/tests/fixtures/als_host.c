#include "als_host.h"

#include <string.h>

uint32_t host_als_opened;
uint32_t host_als_process_status;
uint32_t host_als_raw_index;
uint32_t host_als_raw_count;
uint32_t host_als_dark_index;
uint32_t host_als_dark_count;
uint32_t host_als_extreme_dark;
uint32_t host_als_raw_value;
uint32_t host_als_peak_value;
uint32_t host_als_bucket;
uint32_t host_als_curve_brightness;
uint32_t host_als_target_brightness;
uint32_t host_als_last_brightness;
uint32_t host_als_previous_brightness;
uint32_t host_als_notify_application;
uint32_t host_als_learn_count;
uint32_t host_als_learn_complete;
uint32_t host_als_persisted_scale;
uint32_t host_als_scale;
uint32_t host_als_previous_scale;
uint32_t host_als_lux_base;
uint32_t host_als_raw_samples[5];
uint32_t host_als_dark_samples[20];
uint32_t host_als_manual_lock_tick;
uint8_t host_als_opt_device[64];

uint32_t host_als_sync_count;
uint32_t host_als_sync_event;
uint32_t host_als_sync_size;
uint8_t host_als_sync_record[2];
float host_als_pitch;
uint32_t host_als_power_sensor;
uint32_t host_als_power_enabled;
uint32_t host_als_power_count;
uint32_t host_als_delay_ticks;
uint32_t host_als_opt_assign_count;
int32_t host_als_manufacturer;
int32_t host_als_device_id;
uint32_t host_als_field_write_count;
uint32_t host_als_config_value;
uint32_t host_als_range_value;
uint32_t host_als_register_value;
uint32_t host_als_brightness;
uint32_t host_als_tick;
uint32_t host_als_timer_start_count;
uint32_t host_als_timer_ticks;
uint32_t host_als_timer_stop_count;
uint32_t host_als_apply_count;
uint32_t host_als_applied_brightness;
uint32_t host_als_display_count;
uint32_t host_als_display_brightness_value;
uint32_t host_als_notify_count;

void host_als_reset(void)
{
    memset(&host_als_opened, 0, sizeof(host_als_opened));
    host_als_process_status = 0u;
    host_als_raw_index = 0u;
    host_als_raw_count = 0u;
    host_als_dark_index = 0u;
    host_als_dark_count = 0u;
    host_als_extreme_dark = 0u;
    host_als_raw_value = 0u;
    host_als_peak_value = 0u;
    host_als_bucket = 0u;
    host_als_curve_brightness = 0u;
    host_als_target_brightness = 0u;
    host_als_last_brightness = 0u;
    host_als_previous_brightness = 0u;
    host_als_notify_application = 0u;
    host_als_learn_count = 0u;
    host_als_learn_complete = 0u;
    host_als_persisted_scale = 1024u;
    host_als_scale = 1024u;
    host_als_previous_scale = 1024u;
    host_als_lux_base = 0u;
    memset(host_als_raw_samples, 0, sizeof(host_als_raw_samples));
    memset(host_als_dark_samples, 0, sizeof(host_als_dark_samples));
    host_als_manual_lock_tick = 0u;
    memset(host_als_opt_device, 0, sizeof(host_als_opt_device));
    host_als_sync_count = 0u;
    host_als_sync_event = 0u;
    host_als_sync_size = 0u;
    memset(host_als_sync_record, 0, sizeof(host_als_sync_record));
    host_als_pitch = 0.0f;
    host_als_power_sensor = 0u;
    host_als_power_enabled = 0u;
    host_als_power_count = 0u;
    host_als_delay_ticks = 0u;
    host_als_opt_assign_count = 0u;
    host_als_manufacturer = 0x5449;
    host_als_device_id = 0x3001;
    host_als_field_write_count = 0u;
    host_als_config_value = 0u;
    host_als_range_value = UINT32_MAX;
    host_als_register_value = 0u;
    host_als_brightness = 50u;
    host_als_tick = 0u;
    host_als_timer_start_count = 0u;
    host_als_timer_ticks = 0u;
    host_als_timer_stop_count = 0u;
    host_als_apply_count = 0u;
    host_als_applied_brightness = 0u;
    host_als_display_count = 0u;
    host_als_display_brightness_value = 0u;
    host_als_notify_count = 0u;
}

void open_cfw_retained_zero(void *destination, uint32_t size)
{
    memset(destination, 0, size);
}

int32_t open_cfw_retained_sync_send(
    uint32_t event, const void *data, uint32_t size, uint32_t timeout)
{
    (void)timeout;
    ++host_als_sync_count;
    host_als_sync_event = event;
    host_als_sync_size = size;
    if (data != NULL && size == 2u) {
        memcpy(host_als_sync_record, data, 2u);
    }
    return 0;
}

float open_cfw_retained_imu_pitch(void) { return host_als_pitch; }

void open_cfw_retained_sensor_power(uint32_t sensor, uint32_t enabled)
{
    ++host_als_power_count;
    host_als_power_sensor = sensor;
    host_als_power_enabled = enabled;
}

void open_cfw_retained_delay(uint32_t ticks) { host_als_delay_ticks = ticks; }

void open_cfw_retained_opt3007_assign_register_map(void *device)
{
    if (device == host_als_opt_device) {
        ++host_als_opt_assign_count;
    }
}

int32_t open_cfw_retained_opt3007_field_read(const void *field)
{
    uintptr_t offset = (uintptr_t)field - (uintptr_t)host_als_opt_device;
    return offset == 0x33u ? host_als_manufacturer : host_als_device_id;
}

void open_cfw_retained_opt3007_field_write(void *field, uint32_t value)
{
    uintptr_t offset = (uintptr_t)field - (uintptr_t)host_als_opt_device;
    ++host_als_field_write_count;
    if (offset == 0x0cu) {
        host_als_config_value = value;
    } else if (offset == 0x09u) {
        host_als_range_value = value;
    }
}

uint32_t open_cfw_retained_opt3007_register_read(uint32_t reg)
{
    (void)reg;
    return host_als_register_value;
}

uint32_t open_cfw_retained_brightness_get(void) { return host_als_brightness; }
uint32_t open_cfw_retained_tick_get(uint32_t source)
{
    (void)source;
    return host_als_tick;
}

int32_t open_cfw_retained_sensor_hub_timer_start(uint32_t ticks)
{
    ++host_als_timer_start_count;
    host_als_timer_ticks = ticks;
    return 0;
}

int32_t open_cfw_retained_sensor_hub_timer_stop(void)
{
    ++host_als_timer_stop_count;
    return 0;
}

void open_cfw_retained_brightness_apply(uint8_t brightness)
{
    ++host_als_apply_count;
    host_als_applied_brightness = brightness;
    host_als_brightness = brightness;
}

void open_cfw_retained_display_brightness(uint8_t brightness)
{
    ++host_als_display_count;
    host_als_display_brightness_value = brightness;
}

void open_cfw_retained_brightness_notify(void) { ++host_als_notify_count; }
