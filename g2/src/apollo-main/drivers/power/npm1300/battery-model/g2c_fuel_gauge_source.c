/* SPDX-License-Identifier: MIT
 * Source-only, deliberately uncalibrated fuel-gauge provider for the G2 build.
 *
 * This implements the five Nordic API calls used by the stock npm1300 driver.
 * It does not reproduce Nordic's proprietary model or interpret its undocumented
 * battery_model fields. SOC is a bounded voltage estimate blended with measured
 * charge flow for the stock firmware's 80 mAh design capacity. The result is a
 * development candidate, not a battery calibration or a hardware-qualified port.
 */
#include "../../../../../../../third-party/upstream/nrf-fuel-gauge-1.0.1/include/nrf_fuel_gauge.h"

const char *nrf_fuel_gauge_version = "openCFW-source-0.1";
const char *nrf_fuel_gauge_build_date = "source-only";
const enum nrf_fuel_gauge_variant_type nrf_fuel_gauge_variant =
    NRF_FUEL_GAUGE_VARIANT_SECONDARY;

static struct {
    float soc;
    float current;
    float charge_factor;
    float discharge_factor;
    float charge_limit;
    float term_current;
    enum nrf_fuel_gauge_charge_state charge_state;
    bool initialized;
    bool vbus;
} gauge;

/* Conservative development estimate; these are not fitted EVENBAT parameters. */
static float voltage_soc(float voltage)
{
    static const float volts[] = {3.10f, 3.50f, 3.65f, 3.75f, 3.87f,
                                  3.97f, 4.08f, 4.20f};
    static const float percent[] = {0.0f, 5.0f, 15.0f, 30.0f, 50.0f,
                                    70.0f, 90.0f, 100.0f};
    if (voltage <= volts[0]) return 0.0f;
    for (unsigned index = 1; index < sizeof(volts) / sizeof(volts[0]); ++index) {
        if (voltage <= volts[index])
            return percent[index - 1] +
                (voltage - volts[index - 1]) *
                (percent[index] - percent[index - 1]) /
                (volts[index] - volts[index - 1]);
    }
    return 100.0f;
}

static float bounded_soc(float value)
{
    if (value < 0.0f) return 0.0f;
    if (value > 100.0f) return 100.0f;
    return value;
}

int nrf_fuel_gauge_init(const struct nrf_fuel_gauge_init_parameters *parameters,
                        float *adjusted_voltage)
{
    if (parameters == 0 || parameters->model == 0 ||
        !__builtin_isfinite(parameters->v0) ||
        !__builtin_isfinite(parameters->i0) ||
        !__builtin_isfinite(parameters->t0) ||
        parameters->v0 < 2.0f || parameters->v0 > 5.0f ||
        parameters->state != 0)
        return -22;
    gauge.soc = voltage_soc(parameters->v0);
    gauge.current = parameters->i0;
    gauge.charge_factor = 1.0f;
    gauge.discharge_factor = 1.0f;
    gauge.charge_limit = 0.0f;
    gauge.term_current = 0.0f;
    gauge.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_IDLE;
    gauge.vbus = false;
    gauge.initialized = true;
    if (adjusted_voltage != 0) *adjusted_voltage = parameters->v0;
    return 0;
}

int nrf_fuel_gauge_ext_state_update(enum nrf_fuel_gauge_ext_state_info_type type,
                                     union nrf_fuel_gauge_ext_state_info_data *data)
{
    if (!gauge.initialized) return -22;
    switch (type) {
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_VBUS_CONNECTED:
        gauge.vbus = true;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_VBUS_DISCONNECTED:
        gauge.vbus = false;
        gauge.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_IDLE;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_STATE_CHANGE:
        if (data == 0 || data->charge_state < NRF_FUEL_GAUGE_CHARGE_STATE_IDLE ||
            data->charge_state > NRF_FUEL_GAUGE_CHARGE_STATE_COMPLETE)
            return -22;
        gauge.charge_state = data->charge_state;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_CORRECTION:
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_DISCHARGE_CURRENT_CORRECTION:
        if (data == 0 || !__builtin_isfinite(data->current_correction_factor) ||
            data->current_correction_factor <= 0.0f) return -22;
        if (type == NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_CORRECTION)
            gauge.charge_factor = data->current_correction_factor;
        else
            gauge.discharge_factor = data->current_correction_factor;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_LIMIT:
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_TERM_CURRENT:
        if (data == 0 || !__builtin_isfinite(data->charge_current_limit) ||
            data->charge_current_limit < 0.0f) return -22;
        if (type == NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_LIMIT)
            gauge.charge_limit = data->charge_current_limit;
        else
            gauge.term_current = data->charge_term_current;
        return 0;
    default:
        return -22;
    }
}

float nrf_fuel_gauge_process(float voltage, float current, float temperature,
                             float seconds, struct nrf_fuel_gauge_state_info *state)
{
    if (!gauge.initialized || !__builtin_isfinite(voltage) ||
        !__builtin_isfinite(current) || !__builtin_isfinite(temperature) ||
        !__builtin_isfinite(seconds) || seconds < 0.0f)
        return __builtin_nanf("");
    float corrected = current * (current < 0.0f ? gauge.charge_factor :
                                 gauge.discharge_factor);
    /* Positive current means discharge in the Nordic API. 80 mAh is the
     * stock firmware's design-capacity value, not the cell's rated 96 mAh. */
    if (seconds > 0.0f && seconds <= 86400.0f)
        gauge.soc = bounded_soc(gauge.soc - corrected * seconds *
                               (100.0f / (0.080f * 3600.0f)));
    /* Voltage is most useful near rest. Avoid following load transients. */
    if (corrected > -0.002f && corrected < 0.002f)
        gauge.soc = bounded_soc(0.98f * gauge.soc + 0.02f * voltage_soc(voltage));
    gauge.current = corrected;
    if (state != 0) {
        state->yhat = voltage;
        state->r0 = __builtin_nanf("");
        state->T_truncated = temperature;
        state->i_corrected = corrected;
        state->soc_raw = gauge.soc;
    }
    return gauge.soc;
}

float nrf_fuel_gauge_tte_get(void)
{
    if (!gauge.initialized || gauge.current <= 0.0f) return __builtin_nanf("");
    return gauge.soc * (0.080f * 3600.0f / 100.0f) / gauge.current;
}

float nrf_fuel_gauge_ttf_get(void)
{
    if (!gauge.initialized || !gauge.vbus || gauge.current >= 0.0f ||
        gauge.charge_state == NRF_FUEL_GAUGE_CHARGE_STATE_IDLE)
        return __builtin_nanf("");
    return (100.0f - gauge.soc) * (0.080f * 3600.0f / 100.0f) /
        -gauge.current;
}
