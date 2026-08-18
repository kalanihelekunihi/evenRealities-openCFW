#include "openr1_battery_zephyr.h"

#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1/r1_dispatch.h"
#include "openr1/r1_nv_recovery.h"
#include "openr1_analog_zephyr.h"
#include "openr1_databases_zephyr.h"
#include "openr1_yhm2710_zephyr.h"

typedef struct {
    int (*initialize)(r1_runtime *runtime);
    int (*refresh)(void);
    uint32_t (*update_count)(void);
    int (*last_error)(void);
} openr1_battery_zephyr_api;

K_MUTEX_DEFINE(battery_service_mutex);

static r1_runtime *battery_runtime;
static int16_t voltage_compensation_millivolts;
static int64_t last_success_uptime_ms;
static atomic_t successful_updates;
static atomic_t last_error;
static bool has_successful_update;
static bool battery_service_initialized;

static void record_error(int error) {
    if (error != 0) {
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static uint32_t elapsed_seconds(int64_t now_ms) {
    if (!has_successful_update || now_ms <= last_success_uptime_ms) {
        return 0u;
    }
    const uint64_t elapsed =
        (uint64_t)(now_ms - last_success_uptime_ms) / UINT64_C(1000);
    return elapsed > UINT32_MAX ? UINT32_MAX : (uint32_t)elapsed;
}

int openr1_battery_zephyr_refresh(void) {
    if (!battery_service_initialized || battery_runtime == NULL) {
        return -EACCES;
    }
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    int error = k_mutex_lock(&battery_service_mutex, K_SECONDS(5));
    if (error != 0) {
        record_error(error);
        return error;
    }
    r1_charge_state charge = R1_CHARGE_NOT_CHARGING;
    error = openr1_yhm2710_zephyr_charge_state(&charge);
    const int64_t now_ms = k_uptime_get();
    if (error == 0) {
        error = openr1_analog_zephyr_update_runtime_battery(
            battery_runtime, voltage_compensation_millivolts, charge,
            elapsed_seconds(now_ms));
    }
    if (error == 0) {
        last_success_uptime_ms = now_ms;
        has_successful_update = true;
        atomic_inc(&successful_updates);
        atomic_clear(&last_error);
    } else {
        record_error(error);
    }
    (void)k_mutex_unlock(&battery_service_mutex);
    return error;
}

static void observe_request(void *context, const r1_model *request) {
    (void)context;
    if (request != NULL && request->module == R1_MODULE_SYSTEM &&
        request->command == R1_COMMAND_SYSTEM &&
        request->subcommand == R1_SYSTEM_SUBCOMMAND_DEVICE_STATUS &&
        (request->status & UINT8_C(0x02)) == 0u) {
        (void)openr1_battery_zephyr_refresh();
    }
}

int openr1_battery_zephyr_initialize(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    if (battery_service_initialized) {
        return -EALREADY;
    }
    battery_runtime = runtime;
    voltage_compensation_millivolts = 0;
    last_success_uptime_ms = 0;
    has_successful_update = false;
    atomic_clear(&successful_updates);
    atomic_clear(&last_error);

    r1_nv_battery_configuration configuration;
    if (openr1_databases_zephyr_battery_configuration(&configuration) &&
        configuration.voltage_compensation_valid) {
        voltage_compensation_millivolts =
            configuration.voltage_compensation_millivolts;
    }
    battery_service_initialized = true;
    r1_runtime_set_request_observer(runtime, observe_request, NULL);

    /* Stock refreshes the same runtime service from its status accessors.
     * Seed the protocol-visible state once at boot; an unavailable PMIC/ADC
     * is recorded but does not prevent the rest of the ring from starting. */
    (void)openr1_battery_zephyr_refresh();
    return 0;
}

uint32_t openr1_battery_zephyr_update_count(void) {
    return (uint32_t)atomic_get(&successful_updates);
}

int openr1_battery_zephyr_last_error(void) {
    return (int)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_battery_zephyr_api battery_zephyr_api = {
    openr1_battery_zephyr_initialize,
    openr1_battery_zephyr_refresh,
    openr1_battery_zephyr_update_count,
    openr1_battery_zephyr_last_error,
};
