#include "openr1_analog_zephyr.h"

#include <errno.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/kernel.h>

#include "openr1/r1_battery.h"
#include "openr1/r1_runtime.h"

#define OPENR1_ANALOG_NODE DT_NODELABEL(openr1_analog)
#define OPENR1_ANALOG_SAMPLE_DELAY K_MSEC(2)

static const struct adc_dt_spec battery_channel =
    ADC_DT_SPEC_GET_BY_NAME(OPENR1_ANALOG_NODE, battery);
static const struct adc_dt_spec pmic_current_channel =
    ADC_DT_SPEC_GET_BY_NAME(OPENR1_ANALOG_NODE, pmic_current);
static const struct adc_dt_spec nfc_rectifier_channel =
    ADC_DT_SPEC_GET_BY_NAME(OPENR1_ANALOG_NODE, nfc_rectifier);

K_MUTEX_DEFINE(analog_mutex);

static openr1_analog_zephyr_power_ops battery_power;
static void *battery_power_context;
static bool battery_power_bound;
static bool analog_ready;

static int configure_channel(const struct adc_dt_spec *channel) {
    if (!adc_is_ready_dt(channel)) {
        return -ENODEV;
    }
    return adc_channel_setup_dt(channel);
}

static int sample_channel(const struct adc_dt_spec *channel,
                          int16_t *samples, size_t count) {
    if (samples == NULL || count == 0u) {
        return -EINVAL;
    }
    if (!analog_ready) {
        return -EACCES;
    }
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    int error = k_mutex_lock(&analog_mutex, K_SECONDS(5));
    if (error != 0) {
        return error;
    }
    for (size_t index = 0u; index < count; ++index) {
        struct adc_sequence sequence = {
            .buffer = &samples[index],
            .buffer_size = sizeof(samples[index]),
        };
        error = adc_sequence_init_dt(channel, &sequence);
        if (error == 0) {
            error = adc_read_dt(channel, &sequence);
        }
        if (error != 0) {
            break;
        }
        if (index + 1u < count) {
            k_sleep(OPENR1_ANALOG_SAMPLE_DELAY);
        }
    }
    (void)k_mutex_unlock(&analog_mutex);
    return error;
}

int openr1_analog_zephyr_initialize(void) {
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    int error = k_mutex_lock(&analog_mutex, K_SECONDS(5));
    if (error != 0) {
        return error;
    }
    if (analog_ready) {
        error = -EALREADY;
    } else {
        error = configure_channel(&battery_channel);
        if (error == 0) {
            error = configure_channel(&pmic_current_channel);
        }
        if (error == 0) {
            error = configure_channel(&nfc_rectifier_channel);
        }
        if (error == 0) {
            /* The recovered port executed two raw 64,000-cycle delays. */
            k_busy_wait(1000u);
            k_busy_wait(1000u);
            analog_ready = true;
        }
    }
    (void)k_mutex_unlock(&analog_mutex);
    return error;
}

int openr1_analog_zephyr_bind_power(
    const openr1_analog_zephyr_power_ops *operations, void *context) {
    if (!analog_ready) {
        return -EACCES;
    }
    if (operations == NULL || operations->acquire_battery_power == NULL ||
        operations->release_battery_power == NULL) {
        return -EINVAL;
    }
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    int error = k_mutex_lock(&analog_mutex, K_SECONDS(5));
    if (error != 0) {
        return error;
    }
    if (battery_power_bound) {
        error = -EALREADY;
    } else {
        battery_power = *operations;
        battery_power_context = context;
        battery_power_bound = true;
    }
    (void)k_mutex_unlock(&analog_mutex);
    return error;
}

int openr1_analog_zephyr_battery_millivolts(
    int16_t nv_compensation_millivolts, r1_charge_state charge,
    uint16_t *millivolts) {
    if (millivolts == NULL) {
        return -EINVAL;
    }
    if (!battery_power_bound ||
        !battery_power.acquire_battery_power(battery_power_context)) {
        return -ENOTSUP;
    }
    int16_t raw[R1_BATTERY_SAMPLE_COUNT];
    const int error = sample_channel(
        &battery_channel, raw, R1_BATTERY_SAMPLE_COUNT);
    battery_power.release_battery_power(battery_power_context);
    if (error != 0) {
        return error;
    }
    uint16_t samples[R1_BATTERY_SAMPLE_COUNT];
    for (size_t index = 0u; index < R1_BATTERY_SAMPLE_COUNT; ++index) {
        samples[index] = raw[index] > 0 ? (uint16_t)raw[index] : 0u;
    }
    return r1_battery_runtime_millivolts(
        samples, R1_BATTERY_SAMPLE_COUNT, nv_compensation_millivolts,
        charge, millivolts) ? 0 : -EIO;
}

int openr1_analog_zephyr_update_runtime_battery(
    r1_runtime *runtime, int16_t nv_compensation_millivolts,
    r1_charge_state charge, uint32_t elapsed_seconds) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    uint16_t millivolts = 0u;
    const int error = openr1_analog_zephyr_battery_millivolts(
        nv_compensation_millivolts, charge, &millivolts);
    if (error != 0) {
        return error;
    }
    return r1_runtime_update_battery(
        runtime, charge, millivolts, elapsed_seconds) ? 0 : -EINVAL;
}

int openr1_analog_zephyr_pmic_current_millivolts(uint16_t *millivolts) {
    if (millivolts == NULL) {
        return -EINVAL;
    }
    int16_t samples[R1_PMIC_CURRENT_SAMPLE_COUNT];
    const int error = sample_channel(
        &pmic_current_channel, samples, R1_PMIC_CURRENT_SAMPLE_COUNT);
    if (error != 0) {
        return error;
    }
    return r1_pmic_current_sense_millivolts(
        samples, R1_PMIC_CURRENT_SAMPLE_COUNT, millivolts) ? 0 : -EIO;
}

int openr1_analog_zephyr_nfc_rectifier_millivolts(uint16_t *millivolts) {
    if (millivolts == NULL) {
        return -EINVAL;
    }
    int16_t samples[R1_NFC_RECTIFIER_SAMPLE_COUNT];
    const int error = sample_channel(
        &nfc_rectifier_channel, samples, R1_NFC_RECTIFIER_SAMPLE_COUNT);
    if (error != 0) {
        return error;
    }
    return r1_nfc_rectifier_millivolts(
        samples, R1_NFC_RECTIFIER_SAMPLE_COUNT, millivolts) ? 0 : -EIO;
}

__attribute__((used, section(".openr1_platform_api")))
const openr1_analog_zephyr_api openr1_analog_zephyr_api_table = {
    openr1_analog_zephyr_initialize,
    openr1_analog_zephyr_bind_power,
    openr1_analog_zephyr_battery_millivolts,
    openr1_analog_zephyr_update_runtime_battery,
    openr1_analog_zephyr_pmic_current_millivolts,
    openr1_analog_zephyr_nfc_rectifier_millivolts,
};
