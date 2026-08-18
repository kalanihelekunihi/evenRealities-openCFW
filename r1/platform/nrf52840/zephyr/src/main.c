#include <stdint.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>

#include "openr1_bae8_zephyr.h"
#include "openr1_analog_zephyr.h"
#include "openr1_battery_zephyr.h"
#include "openr1_clock_zephyr.h"
#include "openr1_databases_zephyr.h"
#include "openr1_health_results_zephyr.h"
#include "openr1_gomore_zephyr.h"
#include "openr1_motion_zephyr.h"
#include "openr1_nfc_zephyr.h"
#include "openr1_nfc_resources_zephyr.h"
#include "openr1_optical_zephyr.h"
#include "openr1_power_zephyr.h"
#include "openr1_reset_zephyr.h"
#include "openr1_rtc_zephyr.h"
#include "openr1_sensor_stream_zephyr.h"
#include "openr1_storage_zephyr.h"
#include "openr1_temperature_zephyr.h"
#include "openr1_touch_zephyr.h"
#include "openr1_watchdog_zephyr.h"
#include "openr1_yhm2710_zephyr.h"

void openr1_platform_initialize(void);
r1_runtime *openr1_platform_runtime(void);
uint32_t openr1_platform_poll(uint32_t now_tick);

static void touch_enabled_changed(void *context, bool enabled) {
    (void)context;
    (void)openr1_touch_zephyr_set_enabled(enabled);
}

int main(void) {
    openr1_reset_zephyr_initialize();
    openr1_platform_initialize();
    int error = openr1_watchdog_zephyr_initialize();
    if (error == 0) {
        error = openr1_storage_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_rtc_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_clock_zephyr_initialize(openr1_platform_runtime());
    }
    if (error == 0) {
        error = openr1_databases_zephyr_initialize(openr1_platform_runtime());
    }
    if (error == 0) {
        error = openr1_power_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_motion_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_nfc_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_touch_zephyr_initialize();
    }
    if (error == 0) {
        r1_runtime *runtime = openr1_platform_runtime();
        r1_runtime_set_touch_handler(runtime, touch_enabled_changed, NULL);
        touch_enabled_changed(NULL, runtime->device.touch_enabled);
    }
    if (error == 0) {
        error = openr1_analog_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_yhm2710_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_battery_zephyr_initialize(openr1_platform_runtime());
    }
    if (error == 0) {
        error = openr1_temperature_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_sensor_stream_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_optical_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_health_results_zephyr_initialize(
            openr1_platform_runtime());
    }
    if (error == 0) {
        openr1_sensor_stream_zephyr_health_policy_request(
            openr1_platform_runtime()->device.health_settings[4] != 0u);
    }
    if (error == 0) {
        error = openr1_nfc_resources_zephyr_initialize();
    }
    if (error == 0) {
        error = bt_enable(NULL);
    }
    if (error == 0) {
        error = settings_load();
    }
    if (error == 0) {
        error = openr1_bae8_zephyr_initialize();
    }
    if (error == 0) {
        error = openr1_bae8_zephyr_start_advertising();
    }
    if (error != 0) {
        return error;
    }

    for (;;) {
        uint32_t epoch_seconds = 0u;
        if (openr1_clock_zephyr_epoch(&epoch_seconds)) {
            (void)r1_runtime_schedule_automatic_health_sync(
                openr1_platform_runtime(), epoch_seconds);
            /* Service is intentionally drain-aware: R1_ERROR_STATE means a
             * prior leg is still occupying the recovered shared BLE queue. */
            (void)r1_runtime_service_automatic_health_sync(
                openr1_platform_runtime());
        }
        (void)openr1_gomore_zephyr_sync(openr1_platform_runtime());
        uint32_t wait = openr1_platform_poll(k_uptime_get_32());
        const uint32_t stream_wait = openr1_sensor_stream_zephyr_poll();
        (void)openr1_gomore_zephyr_poll(openr1_platform_runtime());
        if (wait == UINT32_MAX) {
            wait = 100u;
        }
        if (stream_wait < wait) {
            wait = stream_wait;
        }
        k_sleep(K_MSEC(wait));
    }
    return 0;
}
