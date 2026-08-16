#include <stdint.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>

#include "openr1_bae8_zephyr.h"
#include "openr1_analog_zephyr.h"
#include "openr1_clock_zephyr.h"
#include "openr1_databases_zephyr.h"
#include "openr1_motion_zephyr.h"
#include "openr1_nfc_zephyr.h"
#include "openr1_nfc_resources_zephyr.h"
#include "openr1_optical_zephyr.h"
#include "openr1_power_zephyr.h"
#include "openr1_reset_zephyr.h"
#include "openr1_storage_zephyr.h"
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
        error = openr1_optical_zephyr_initialize();
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
        const uint32_t wait = openr1_platform_poll(k_uptime_get_32());
        k_sleep(wait == UINT32_MAX ? K_MSEC(100) : K_MSEC(wait));
    }
    return 0;
}
