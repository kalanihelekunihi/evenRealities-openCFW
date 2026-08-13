#include "openr1_analog.h"

#include <stddef.h>
#include <stdint.h>

#include "cmsis_os2.h"
#include "nrf_delay.h"
#include "nrfx_saadc.h"

#include "openr1/r1_battery.h"
#include "openr1/r1_runtime.h"

#define OPENR1_ANALOG_MUTEX_WAIT UINT32_C(5000)
#define OPENR1_ANALOG_BATTERY_CHANNEL 0u
#define OPENR1_ANALOG_PMIC_CURRENT_CHANNEL 1u
#define OPENR1_ANALOG_NFC_RECTIFIER_CHANNEL 2u
#define OPENR1_ANALOG_SAMPLE_DELAY_TICKS UINT32_C(2)

static osMutexId_t analog_mutex;
static const openr1_analog_power_ops *power_ops;
static void *power_context;
static bool analog_ready;

static void analog_event_handler(const nrfx_saadc_evt_t *event) {
    (void)event;
}

static nrf_saadc_channel_config_t slow_channel(nrf_saadc_input_t input) {
    const nrf_saadc_channel_config_t configuration = {
        .resistor_p = NRF_SAADC_RESISTOR_DISABLED,
        .resistor_n = NRF_SAADC_RESISTOR_DISABLED,
        .gain = NRF_SAADC_GAIN1_2,
        .reference = NRF_SAADC_REFERENCE_INTERNAL,
        .acq_time = NRF_SAADC_ACQTIME_40US,
        .mode = NRF_SAADC_MODE_SINGLE_ENDED,
        .burst = NRF_SAADC_BURST_DISABLED,
        .pin_p = input,
        .pin_n = NRF_SAADC_INPUT_DISABLED,
    };
    return configuration;
}

static nrf_saadc_channel_config_t rectifier_channel(void) {
    const nrf_saadc_channel_config_t configuration = {
        .resistor_p = NRF_SAADC_RESISTOR_DISABLED,
        .resistor_n = NRF_SAADC_RESISTOR_DISABLED,
        .gain = NRF_SAADC_GAIN1_6,
        .reference = NRF_SAADC_REFERENCE_INTERNAL,
        .acq_time = NRF_SAADC_ACQTIME_10US,
        .mode = NRF_SAADC_MODE_SINGLE_ENDED,
        .burst = NRF_SAADC_BURST_DISABLED,
        .pin_p = NRF_SAADC_INPUT_AIN2,
        .pin_n = NRF_SAADC_INPUT_DISABLED,
    };
    return configuration;
}

static ret_code_t sample_channel(uint8_t channel, int16_t *samples,
                                 size_t count) {
    if (!analog_ready || samples == NULL || count == 0u ||
        osMutexAcquire(analog_mutex, OPENR1_ANALOG_MUTEX_WAIT) != osOK) {
        return NRF_ERROR_INVALID_STATE;
    }
    ret_code_t result = NRF_SUCCESS;
    for (size_t index = 0u; index < count; ++index) {
        nrf_saadc_value_t sample = 0;
        result = nrfx_saadc_sample_convert(channel, &sample);
        if (result != NRFX_SUCCESS) {
            break;
        }
        samples[index] = sample;
        (void)osDelay(OPENR1_ANALOG_SAMPLE_DELAY_TICKS);
    }
    (void)osMutexRelease(analog_mutex);
    return result;
}

ret_code_t openr1_analog_initialize(void) {
    if (analog_ready || analog_mutex != NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    analog_mutex = osMutexNew(NULL);
    if (analog_mutex == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    const nrfx_saadc_config_t driver = {
        .resolution = NRF_SAADC_RESOLUTION_12BIT,
        .oversample = NRF_SAADC_OVERSAMPLE_DISABLED,
        .interrupt_priority = 6u,
        .low_power_mode = false,
    };
    ret_code_t result = nrfx_saadc_init(&driver, analog_event_handler);
    nrf_saadc_channel_config_t channel = slow_channel(NRF_SAADC_INPUT_AIN5);
    if (result == NRFX_SUCCESS) {
        result = nrfx_saadc_channel_init(
            OPENR1_ANALOG_BATTERY_CHANNEL, &channel);
    }
    channel = slow_channel(NRF_SAADC_INPUT_AIN3);
    if (result == NRFX_SUCCESS) {
        result = nrfx_saadc_channel_init(
            OPENR1_ANALOG_PMIC_CURRENT_CHANNEL, &channel);
    }
    channel = rectifier_channel();
    if (result == NRFX_SUCCESS) {
        result = nrfx_saadc_channel_init(
            OPENR1_ANALOG_NFC_RECTIFIER_CHANNEL, &channel);
    }
    if (result != NRFX_SUCCESS) {
        nrfx_saadc_uninit();
        return result;
    }
    /* The recovered port invokes Nordic's raw 64,000-cycle delay body twice. */
    nrf_delay_us(1000u);
    nrf_delay_us(1000u);
    analog_ready = true;
    return NRF_SUCCESS;
}

ret_code_t openr1_analog_bind_power(
    const openr1_analog_power_ops *operations, void *context) {
    if (!analog_ready) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (operations == NULL || operations->acquire_battery_power == NULL ||
        operations->release_battery_power == NULL) {
        return NRF_ERROR_INVALID_PARAM;
    }
    if (power_ops != NULL) {
        return NRF_ERROR_BUSY;
    }
    power_ops = operations;
    power_context = context;
    return NRF_SUCCESS;
}

ret_code_t openr1_analog_battery_millivolts(
    int16_t nv_compensation_millivolts, r1_charge_state charge,
    uint16_t *millivolts) {
    if (millivolts == NULL) {
        return NRF_ERROR_NULL;
    }
    if (power_ops == NULL ||
        !power_ops->acquire_battery_power(power_context)) {
        return NRF_ERROR_NOT_SUPPORTED;
    }
    int16_t raw[R1_BATTERY_SAMPLE_COUNT];
    const ret_code_t sample_result = sample_channel(
        OPENR1_ANALOG_BATTERY_CHANNEL, raw, R1_BATTERY_SAMPLE_COUNT);
    power_ops->release_battery_power(power_context);
    if (sample_result != NRF_SUCCESS) {
        return sample_result;
    }
    uint16_t samples[R1_BATTERY_SAMPLE_COUNT];
    for (size_t index = 0u; index < R1_BATTERY_SAMPLE_COUNT; ++index) {
        samples[index] = raw[index] > 0 ? (uint16_t)raw[index] : 0u;
    }
    return r1_battery_runtime_millivolts(
        samples, R1_BATTERY_SAMPLE_COUNT, nv_compensation_millivolts,
        charge, millivolts) ? NRF_SUCCESS : NRF_ERROR_INTERNAL;
}

ret_code_t openr1_analog_update_runtime_battery(
    r1_runtime *runtime, int16_t nv_compensation_millivolts,
    r1_charge_state charge, uint32_t elapsed_seconds) {
    if (runtime == NULL) {
        return NRF_ERROR_NULL;
    }
    uint16_t millivolts = 0u;
    const ret_code_t result = openr1_analog_battery_millivolts(
        nv_compensation_millivolts, charge, &millivolts);
    if (result != NRF_SUCCESS) {
        return result;
    }
    return r1_runtime_update_battery(
        runtime, charge, millivolts, elapsed_seconds)
        ? NRF_SUCCESS : NRF_ERROR_INVALID_PARAM;
}

ret_code_t openr1_analog_pmic_current_millivolts(uint16_t *millivolts) {
    if (millivolts == NULL) {
        return NRF_ERROR_NULL;
    }
    int16_t samples[R1_PMIC_CURRENT_SAMPLE_COUNT];
    const ret_code_t result = sample_channel(
        OPENR1_ANALOG_PMIC_CURRENT_CHANNEL, samples,
        R1_PMIC_CURRENT_SAMPLE_COUNT);
    if (result != NRF_SUCCESS) {
        return result;
    }
    return r1_pmic_current_sense_millivolts(
        samples, R1_PMIC_CURRENT_SAMPLE_COUNT, millivolts)
        ? NRF_SUCCESS : NRF_ERROR_INTERNAL;
}

ret_code_t openr1_analog_nfc_rectifier_millivolts(uint16_t *millivolts) {
    if (millivolts == NULL) {
        return NRF_ERROR_NULL;
    }
    int16_t samples[R1_NFC_RECTIFIER_SAMPLE_COUNT];
    const ret_code_t result = sample_channel(
        OPENR1_ANALOG_NFC_RECTIFIER_CHANNEL, samples,
        R1_NFC_RECTIFIER_SAMPLE_COUNT);
    if (result != NRF_SUCCESS) {
        return result;
    }
    return r1_nfc_rectifier_millivolts(
        samples, R1_NFC_RECTIFIER_SAMPLE_COUNT, millivolts)
        ? NRF_SUCCESS : NRF_ERROR_INTERNAL;
}

typedef struct {
    ret_code_t (*initialize)(void);
    ret_code_t (*bind_power)(const openr1_analog_power_ops *, void *);
    ret_code_t (*battery_millivolts)(int16_t, r1_charge_state, uint16_t *);
    void (*configure_battery)(r1_runtime *, uint8_t);
    ret_code_t (*update_runtime_battery)(
        r1_runtime *, int16_t, r1_charge_state, uint32_t);
    ret_code_t (*pmic_current_millivolts)(uint16_t *);
    ret_code_t (*nfc_rectifier_millivolts)(uint16_t *);
    bool (*plan_charge_event)(const r1_pmic_charge_observation *,
                              r1_pmic_charge_plan *);
    bool (*plan_charged_notification)(
        const r1_pmic_charged_observation *, r1_pmic_charged_plan *);
} openr1_analog_api;

__attribute__((used, section(".openr1_analog_api")))
static const openr1_analog_api retained_analog_api = {
    openr1_analog_initialize,
    openr1_analog_bind_power,
    openr1_analog_battery_millivolts,
    r1_runtime_configure_battery,
    openr1_analog_update_runtime_battery,
    openr1_analog_pmic_current_millivolts,
    openr1_analog_nfc_rectifier_millivolts,
    r1_pmic_plan_charge_event,
    r1_pmic_plan_charged_notification,
};
