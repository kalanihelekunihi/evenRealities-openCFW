#include "openr1/r1_battery.h"

#include <stddef.h>
#include <stdint.h>

#define BATTERY_SCALE_NUMERATOR UINT32_C(0x000d5154)
#define BATTERY_SCALE_DENOMINATOR UINT32_C(0x00079d38)
#define BATTERY_COMPENSATION_MIN (-299)
#define BATTERY_COMPENSATION_MAX 299
#define BATTERY_CHARGING_DIVIDER 0x1.0d9168p+0f
#define BATTERY_INVALID_MILLIVOLTS UINT16_C(2399)
#define BATTERY_INVALID_PERCENT UINT8_C(50)
#define BATTERY_FIRST_MILLIVOLTS UINT16_C(3350)
#define BATTERY_FULL_MILLIVOLTS UINT16_C(4341)
#define BATTERY_FULL_REFRESH_COUNT UINT8_C(5)
#define BATTERY_REFRESH_COUNT_MAX UINT8_C(8)
#define BATTERY_ELAPSED_CAP UINT32_C(180)
#define BATTERY_STUCK_PERCENT_MAX UINT8_C(98)
#define BATTERY_STUCK_MILLIVOLTS_MIN UINT16_C(2400)
#define BATTERY_STUCK_RISE_MIN UINT16_C(35)
#define BATTERY_STUCK_SECONDS_MIN UINT32_C(120)
#define PMIC_THERMAL_LOW_MAX UINT8_C(14)
#define PMIC_THERMAL_MID_MIN UINT8_C(15)
#define PMIC_THERMAL_MID_MAX UINT8_C(44)

static const uint8_t pmic_status_version[] = {
    UINT8_C('2'), UINT8_C('.'), UINT8_C('2'), UINT8_C('.'), UINT8_C('6'),
    UINT8_C('.'), UINT8_C('0'), UINT8_C('0'), UINT8_C('0'), UINT8_C('9'),
};

static const uint16_t discharge_bounds
    [R1_BATTERY_PROFILE_COUNT][R1_BATTERY_CURVE_SEGMENTS] = {
    {3622, 3668, 3682, 3714, 3742, 3769, 3795, 3820, 3845, 3874,
     3902, 3928, 3978, 4027, 4077, 4128, 4175, 4223, 4262, 4310},
    {3609, 3669, 3683, 3713, 3742, 3769, 3792, 3816, 3844, 3870,
     3902, 3928, 3977, 4032, 4077, 4127, 4177, 4225, 4265, 4310},
    {3531, 3653, 3676, 3704, 3725, 3742, 3758, 3776, 3797, 3822,
     3850, 3885, 3926, 3965, 4024, 4071, 4124, 4179, 4241, 4310},
    {3609, 3653, 3677, 3703, 3721, 3739, 3755, 3774, 3796, 3821,
     3852, 3889, 3926, 3967, 4026, 4070, 4120, 4172, 4232, 4310},
};

static const uint16_t charging_bounds
    [R1_BATTERY_PROFILE_COUNT][R1_BATTERY_CURVE_SEGMENTS] = {
    {3799, 3848, 3887, 3918, 3940, 3960, 3978, 3999, 4021, 4048,
     4078, 4112, 4152, 4200, 4250, 4303, 4320, 4330, 4340, 4310},
    {3784, 3809, 3845, 3871, 3885, 3898, 3913, 3933, 3956, 3983,
     4013, 4043, 4074, 4121, 4167, 4211, 4261, 4318, 4330, 4350},
    {3799, 3848, 3887, 3918, 3940, 3960, 3978, 3999, 4021, 4048,
     4078, 4112, 4152, 4200, 4250, 4303, 4320, 4330, 4340, 4350},
    {3784, 3809, 3845, 3871, 3885, 3898, 3913, 3933, 3956, 3983,
     4013, 4043, 4074, 4121, 4167, 4211, 4261, 4318, 4330, 4350},
};

static const uint16_t charge_step_seconds[R1_BATTERY_PROFILE_COUNT][4] = {
    {38, 60, 108, 480},
    {48, 72, 144, 480},
    {38, 60, 108, 480},
    {48, 72, 144, 480},
};

r1_battery_diagnostic_cadence r1_battery_diagnostic_cadence_step(
    uint8_t previous_counter) {
    const uint8_t incremented = (uint8_t)(previous_counter + 1u);
    r1_battery_diagnostic_cadence result = {
        .next_counter = incremented,
        .status_log_requested =
            incremented % R1_BATTERY_DIAGNOSTIC_STATUS_PERIOD == 0u,
    };
    if (incremented >= R1_BATTERY_DIAGNOSTIC_FULL_PERIOD) {
        result.next_counter = 0u;
        result.compensation_log_requested = true;
    }
    return result;
}

r1_error r1_analog_close_plan_build(
    r1_analog_channel channel, const r1_analog_close_state *state,
    r1_analog_close_plan *plan) {
    if (state == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_analog_close_plan){0};
    if (channel < R1_ANALOG_CHANNEL_BATTERY ||
        channel > R1_ANALOG_CHANNEL_NFC_RECTIFIER) {
        plan->provider_status = R1_ANALOG_PROVIDER_STATUS_NOT_FOUND;
        return R1_OK;
    }
    plan->provider_status = R1_ANALOG_PROVIDER_STATUS_OK;
    const size_t selected = (size_t)channel;
    if (!state->channel_open[selected]) {
        return R1_OK;
    }
    /* The stock records select nrfx channels with their AIN selectors. */
    static const uint8_t nrfx_channels[R1_ANALOG_CHANNEL_COUNT] = {6u, 4u, 3u};
    plan->uninitialize_channel = true;
    plan->nrfx_channel = nrfx_channels[selected];
    plan->clear_channel_open = true;
    bool another_open = false;
    for (size_t index = 0u; index < R1_ANALOG_CHANNEL_COUNT; ++index) {
        if (index != selected && state->channel_open[index]) {
            another_open = true;
        }
    }
    plan->uninitialize_driver = state->driver_initialized && !another_open;
    plan->clear_driver_initialized = plan->uninitialize_driver;
    return R1_OK;
}

r1_error r1_factory_pmic_current_diagnostic_plan_build(
    uint32_t current_sense_millivolts,
    r1_factory_pmic_current_diagnostic_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_pmic_current_diagnostic_plan){
        .current_sense_millivolts = current_sense_millivolts,
        .handler_return_value = 1u,
    };
    return R1_OK;
}

r1_error r1_factory_pmic_power_off_plan_build(
    uint32_t timestamp, uint16_t battery_millivolts,
    r1_factory_pmic_power_off_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const uint16_t stored_millivolts = (uint16_t)(
        battery_millivolts & R1_FACTORY_PMIC_BATTERY_MILLIVOLT_MASK);
    *plan = (r1_factory_pmic_power_off_plan){
        .timestamp = timestamp,
        .raw_battery_millivolts = battery_millivolts,
        .stored_battery_millivolts = stored_millivolts,
        .packed_dev_info_word = (uint16_t)(
            (uint16_t)(stored_millivolts << 2u) |
            R1_FACTORY_PMIC_POWER_STATE_OFF),
        .persist_dev_info_requested = true,
        .signal_power_thread_requested = true,
        .power_thread_flags = R1_FACTORY_PMIC_POWER_THREAD_FLAG,
        .handler_return_value = 1u,
    };
    return R1_OK;
}

r1_error r1_factory_pmic_register_diagnostic_plan_build(
    uint8_t register_9, r1_factory_pmic_register_diagnostic_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_pmic_register_diagnostic_plan){
        .formatted_registers = {register_9},
        .handler_return_value = 1u,
    };
    return R1_OK;
}

static size_t curve_profile(uint8_t battery_type) {
    return battery_type >= 1u && battery_type <= R1_BATTERY_PROFILE_COUNT
        ? (size_t)(battery_type - 1u) : R1_BATTERY_PROFILE_COUNT - 1u;
}

static size_t cadence_profile(uint8_t battery_type) {
    return battery_type >= 1u && battery_type <= R1_BATTERY_PROFILE_COUNT
        ? (size_t)(battery_type - 1u) : 0u;
}

static uint8_t curve_percent(const uint16_t *upper_bounds,
                             uint16_t millivolts) {
    uint16_t voltage = millivolts;
    if (voltage < BATTERY_FIRST_MILLIVOLTS) {
        voltage = BATTERY_FIRST_MILLIVOLTS;
    }
    if (voltage > upper_bounds[R1_BATTERY_CURVE_SEGMENTS - 1u]) {
        voltage = upper_bounds[R1_BATTERY_CURVE_SEGMENTS - 1u];
    }
    uint16_t lower = BATTERY_FIRST_MILLIVOLTS;
    uint8_t accumulated = 0u;
    for (size_t index = 0u; index < R1_BATTERY_CURVE_SEGMENTS; ++index) {
        const uint16_t upper = upper_bounds[index];
        if (voltage <= upper) {
            const uint16_t width = (uint16_t)(upper - lower);
            if (width == 0u) {
                return accumulated;
            }
            const uint16_t within = (uint16_t)(
                UINT16_C(5) * (uint16_t)(voltage - lower) / width);
            return (uint8_t)(accumulated + within);
        }
        accumulated = (uint8_t)(accumulated + 5u);
        lower = upper;
    }
    return accumulated;
}

bool r1_battery_base_millivolts(const uint16_t *samples, size_t count,
                                uint16_t *millivolts) {
    if (samples == NULL || millivolts == NULL ||
        count != R1_BATTERY_SAMPLE_COUNT) {
        return false;
    }
    uint16_t sorted[R1_BATTERY_SAMPLE_COUNT];
    for (size_t index = 0u; index < R1_BATTERY_SAMPLE_COUNT; ++index) {
        sorted[index] = samples[index];
        size_t cursor = index;
        while (cursor > 0u && sorted[cursor] < sorted[cursor - 1u]) {
            const uint16_t prior = sorted[cursor - 1u];
            sorted[cursor - 1u] = sorted[cursor];
            sorted[cursor] = prior;
            --cursor;
        }
    }
    uint32_t retained = 0u;
    for (size_t index = 2u; index < R1_BATTERY_SAMPLE_COUNT; ++index) {
        retained += sorted[index];
    }
    const uint32_t average = retained / UINT32_C(3);
    *millivolts = (uint16_t)(
        average * BATTERY_SCALE_NUMERATOR / BATTERY_SCALE_DENOMINATOR);
    return true;
}

bool r1_battery_runtime_millivolts(const uint16_t *samples, size_t count,
                                   int16_t nv_compensation_millivolts,
                                   r1_charge_state charge,
                                   uint16_t *millivolts) {
    uint16_t base = 0u;
    if (!r1_battery_base_millivolts(samples, count, &base) ||
        millivolts == NULL) {
        return false;
    }
    int32_t compensation = nv_compensation_millivolts;
    if (compensation < BATTERY_COMPENSATION_MIN ||
        compensation > BATTERY_COMPENSATION_MAX) {
        compensation = 0;
    }
    int32_t result = (int32_t)base + compensation;
    if (charge == R1_CHARGE_CHARGING) {
        result = (int32_t)((float)result / BATTERY_CHARGING_DIVIDER);
    }
    *millivolts = (uint16_t)result;
    return true;
}

bool r1_nfc_rectifier_millivolts(const int16_t *samples, size_t count,
                                 uint16_t *millivolts) {
    if (samples == NULL || millivolts == NULL ||
        count != R1_NFC_RECTIFIER_SAMPLE_COUNT) {
        return false;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index < R1_NFC_RECTIFIER_SAMPLE_COUNT; ++index) {
        if (samples[index] > 0) {
            sum += (uint16_t)samples[index];
        }
    }
    const uint32_t average = sum / UINT32_C(3);
    const uint32_t first = ((average * UINT32_C(3600) + UINT32_C(2048)) &
                            UINT32_C(0x0fffffff)) >> 12u;
    *millivolts = (uint16_t)(first * UINT32_C(331) / UINT32_C(51));
    return true;
}

bool r1_pmic_current_sense_millivolts(const int16_t *samples, size_t count,
                                      uint16_t *millivolts) {
    if (samples == NULL || millivolts == NULL ||
        count != R1_PMIC_CURRENT_SAMPLE_COUNT) {
        return false;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index < R1_PMIC_CURRENT_SAMPLE_COUNT; ++index) {
        if (samples[index] > 0) {
            sum += (uint16_t)samples[index];
        }
    }
    const uint32_t average = sum / UINT32_C(3);
    *millivolts = (uint16_t)(
        (average * UINT32_C(1200) + UINT32_C(2048)) >> 12u);
    return true;
}

uint8_t r1_battery_discharge_percent(uint16_t millivolts,
                                     uint8_t battery_type,
                                     uint8_t charged_refresh_count) {
    if (millivolts <= BATTERY_INVALID_MILLIVOLTS) {
        return BATTERY_INVALID_PERCENT;
    }
    if (millivolts >= BATTERY_FULL_MILLIVOLTS &&
        charged_refresh_count >= BATTERY_FULL_REFRESH_COUNT) {
        return 100u;
    }
    return curve_percent(discharge_bounds[curve_profile(battery_type)],
                         millivolts);
}

uint8_t r1_battery_charging_initial_percent(uint16_t millivolts,
                                            uint8_t battery_type) {
    if (millivolts <= BATTERY_INVALID_MILLIVOLTS) {
        return BATTERY_INVALID_PERCENT;
    }
    return curve_percent(charging_bounds[curve_profile(battery_type)],
                         millivolts);
}

r1_battery_charge_result r1_battery_advance_charging(
    r1_battery_charge_progress state, uint32_t elapsed_seconds,
    uint8_t battery_type, uint16_t millivolts,
    uint8_t charged_refresh_count) {
    r1_battery_charge_result result = {state, state.percent};
    if (state.percent >= 100u) {
        result.reported_percent = 100u;
        return result;
    }
    const uint16_t *thresholds = charge_step_seconds[
        cadence_profile(battery_type)];
    const uint32_t accepted = elapsed_seconds < BATTERY_ELAPSED_CAP
        ? elapsed_seconds : BATTERY_ELAPSED_CAP;
    state.accumulated_seconds += accepted;
    while (state.percent < 100u && state.accumulated_seconds != 0u) {
        size_t band = 3u;
        if (state.percent < 85u) {
            band = 0u;
        } else if (state.percent < 90u) {
            band = 1u;
        } else if (state.percent < 95u) {
            band = 2u;
        }
        const uint32_t threshold = thresholds[band];
        if (threshold == 0u || state.accumulated_seconds < threshold) {
            break;
        }
        state.accumulated_seconds -= threshold;
        ++state.percent;
    }
    result.state = state;
    result.reported_percent =
        millivolts >= BATTERY_FULL_MILLIVOLTS &&
        charged_refresh_count >= BATTERY_FULL_REFRESH_COUNT
        ? 100u : state.percent;
    return result;
}

uint8_t r1_battery_updated_charged_refresh_count(
    uint8_t previous, r1_charge_state charge) {
    if (charge != R1_CHARGE_FULL) {
        return 0u;
    }
    return previous < BATTERY_REFRESH_COUNT_MAX
        ? (uint8_t)(previous + 1u) : BATTERY_REFRESH_COUNT_MAX;
}

bool r1_battery_stalled_replacement(
    uint8_t current_percent, uint8_t previous_percent,
    uint16_t previous_millivolts, uint16_t current_millivolts,
    uint32_t unchanged_seconds, bool already_recovered,
    uint8_t battery_type, uint8_t *replacement_percent) {
    if (replacement_percent == NULL || current_percent != previous_percent ||
        already_recovered || current_percent > BATTERY_STUCK_PERCENT_MAX ||
        previous_millivolts < BATTERY_STUCK_MILLIVOLTS_MIN ||
        current_millivolts < BATTERY_STUCK_MILLIVOLTS_MIN ||
        (uint32_t)current_millivolts <
            (uint32_t)previous_millivolts + BATTERY_STUCK_RISE_MIN ||
        unchanged_seconds < BATTERY_STUCK_SECONDS_MIN) {
        return false;
    }
    const uint8_t mapped = r1_battery_charging_initial_percent(
        current_millivolts, battery_type);
    uint8_t replacement = mapped > current_percent ? mapped : current_percent;
    if (replacement > 100u) {
        replacement = 100u;
    }
    *replacement_percent = replacement;
    return true;
}

r1_battery_stuck_result r1_battery_update_stuck_recovery(
    r1_battery_stuck_state state, r1_charge_state charge,
    uint8_t current_percent, uint16_t current_millivolts,
    uint32_t unchanged_seconds, uint8_t battery_type) {
    r1_battery_stuck_result result = {state, false, 0u, false, false};
    if (charge != R1_CHARGE_CHARGING) {
        result.state.has_previous_percent = false;
        result.state.already_recovered = false;
        return result;
    }
    if (current_percent == 0u) {
        return result;
    }
    if (!state.has_previous_percent ||
        current_percent != state.previous_percent) {
        result.state.has_previous_percent = true;
        result.state.previous_percent = current_percent;
        result.state.previous_millivolts = current_millivolts;
        result.state.already_recovered = false;
        result.observation_baseline_updated = true;
        return result;
    }
    uint8_t replacement = 0u;
    if (!r1_battery_stalled_replacement(
            current_percent, state.previous_percent,
            state.previous_millivolts, current_millivolts,
            unchanged_seconds, state.already_recovered,
            battery_type, &replacement)) {
        return result;
    }
    result.state.previous_millivolts = current_millivolts;
    result.state.already_recovered = true;
    result.has_replacement_percent = true;
    result.replacement_progress_percent = replacement;
    result.observation_baseline_updated = true;
    result.should_reset_charge_progress = true;
    return result;
}

void r1_battery_controller_initialize(
    r1_battery_controller *controller, uint8_t battery_type,
    uint8_t initial_percent, r1_charge_state initial_charge) {
    if (controller == NULL) {
        return;
    }
    controller->battery_type = battery_type;
    controller->charge = initial_charge;
    controller->millivolts = 0u;
    controller->percent = initial_percent;
    controller->charged_refresh_count = 0u;
    controller->charge_progress.percent = initial_percent;
    controller->charge_progress.accumulated_seconds = 0u;
    controller->stuck.has_previous_percent = false;
    controller->stuck.previous_percent = 0u;
    controller->stuck.previous_millivolts = 0u;
    controller->stuck.already_recovered = false;
    controller->stuck_unchanged_seconds = 0u;
}

void r1_battery_controller_set_type(
    r1_battery_controller *controller, uint8_t battery_type) {
    if (controller != NULL) {
        controller->battery_type = battery_type;
    }
}

static uint32_t elapsed_add(uint32_t accumulated, uint32_t elapsed) {
    return UINT32_MAX - accumulated < elapsed
        ? UINT32_MAX : accumulated + elapsed;
}

bool r1_battery_controller_update(
    r1_battery_controller *controller, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds) {
    if (controller == NULL ||
        (charge != R1_CHARGE_CHARGING &&
         charge != R1_CHARGE_NOT_CHARGING &&
         charge != R1_CHARGE_FULL)) {
        return false;
    }

    const bool entering_charging =
        controller->charge != R1_CHARGE_CHARGING &&
        charge == R1_CHARGE_CHARGING;
    controller->charged_refresh_count =
        r1_battery_updated_charged_refresh_count(
            controller->charged_refresh_count, charge);
    controller->charge = charge;
    controller->millivolts = millivolts;

    if (charge != R1_CHARGE_CHARGING) {
        controller->charge_progress.percent = 0u;
        controller->charge_progress.accumulated_seconds = 0u;
        controller->stuck.has_previous_percent = false;
        controller->stuck.already_recovered = false;
        controller->stuck_unchanged_seconds = 0u;
        controller->percent = r1_battery_discharge_percent(
            millivolts, controller->battery_type,
            controller->charged_refresh_count);
        return true;
    }

    uint32_t accepted_elapsed = elapsed_seconds;
    if (entering_charging) {
        controller->charge_progress.percent =
            controller->percent == 0u ? 1u : controller->percent;
        controller->charge_progress.accumulated_seconds = 0u;
        controller->stuck.has_previous_percent = false;
        controller->stuck.already_recovered = false;
        controller->stuck_unchanged_seconds = 0u;
        accepted_elapsed = 0u;
    }

    controller->stuck_unchanged_seconds = elapsed_add(
        controller->stuck_unchanged_seconds, accepted_elapsed);
    const r1_battery_stuck_result recovery =
        r1_battery_update_stuck_recovery(
            controller->stuck, charge, controller->percent, millivolts,
            controller->stuck_unchanged_seconds, controller->battery_type);
    controller->stuck = recovery.state;
    if (recovery.observation_baseline_updated) {
        controller->stuck_unchanged_seconds = 0u;
    }
    if (recovery.has_replacement_percent) {
        controller->charge_progress.percent =
            recovery.replacement_progress_percent;
        controller->charge_progress.accumulated_seconds = 0u;
        /* Stock recovery clears the cadence timestamp before the next walk. */
        accepted_elapsed = 0u;
    }

    const r1_battery_charge_result advanced = r1_battery_advance_charging(
        controller->charge_progress, accepted_elapsed,
        controller->battery_type, millivolts,
        controller->charged_refresh_count);
    controller->charge_progress = advanced.state;
    controller->percent = advanced.reported_percent;
    return true;
}

static void clear_pmic_plan(r1_pmic_charge_plan *plan) {
    uint8_t *bytes = (uint8_t *)plan;
    for (size_t index = 0u; index < sizeof *plan; ++index) {
        bytes[index] = 0u;
    }
}

static bool pmic_wire_charge(r1_charge_state charge, uint8_t *wire_charge) {
    if (wire_charge == NULL) {
        return false;
    }
    switch (charge) {
        case R1_CHARGE_NOT_CHARGING:
            *wire_charge = 0u;
            return true;
        case R1_CHARGE_CHARGING:
            *wire_charge = 1u;
            return true;
        case R1_CHARGE_FULL:
            *wire_charge = 2u;
            return true;
        case R1_CHARGE_UNKNOWN:
        default:
            return false;
    }
}

static void write_little_endian_u16(uint8_t *destination, uint16_t value) {
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
}

bool r1_pmic_plan_charge_event(
    const r1_pmic_charge_observation *observation,
    r1_pmic_charge_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return false;
    }
    uint8_t wire_charge = 0u;
    if (!pmic_wire_charge(observation->charge, &wire_charge)) {
        return false;
    }

    clear_pmic_plan(plan);
    plan->cancel_event_work =
        observation->event != R1_PMIC_CHARGE_EVENT_PRESERVE_WORK;
    if (observation->charge == R1_CHARGE_NOT_CHARGING) {
        /* The stock transition performs a second unconditional cancellation. */
        plan->cancel_event_work = true;
        plan->transition = R1_PMIC_TRANSITION_NOT_CHARGING;
        return true;
    }
    if (observation->event != R1_PMIC_CHARGE_EVENT_SAMPLE) {
        return true;
    }

    const uint8_t temperature = (uint8_t)(
        (observation->charge_temperature_milliunits / UINT16_C(1000)) &
        UINT16_C(0x3f));
    plan->process_dock_mailbox = true;
    plan->dock_status[1] = UINT8_C(1);
    plan->dock_status[2] = UINT8_C(2);
    plan->dock_status[3] = observation->battery_percent;
    plan->dock_status[4] = (uint8_t)(wire_charge | (uint8_t)(temperature << 2u));
    write_little_endian_u16(&plan->dock_status[5],
                            observation->battery_millivolts);
    write_little_endian_u16(&plan->dock_status[7],
                            observation->nfc_rectifier_millivolts);
    plan->dock_status[9] = observation->raw_power_flags;
    plan->dock_status[10] = observation->pmic_ready_flag;
    for (size_t index = 0u; index < sizeof pmic_status_version; ++index) {
        plan->dock_status[13u + index] = pmic_status_version[index];
    }

    if (temperature >= UINT8_C(1) && temperature <= PMIC_THERMAL_LOW_MAX) {
        if (observation->current_thermal_target_word !=
            R1_PMIC_THERMAL_LOW_TARGET_WORD) {
            plan->thermal_action = R1_PMIC_THERMAL_ACTION_SET_TARGET;
            plan->thermal_target_word = R1_PMIC_THERMAL_LOW_TARGET_WORD;
        }
    } else if (temperature >= PMIC_THERMAL_MID_MIN &&
               temperature <= PMIC_THERMAL_MID_MAX) {
        if (observation->current_thermal_target_word !=
            R1_PMIC_THERMAL_MID_TARGET_WORD) {
            plan->thermal_action = R1_PMIC_THERMAL_ACTION_SET_TARGET;
            plan->thermal_target_word = R1_PMIC_THERMAL_MID_TARGET_WORD;
        }
    } else if (temperature > PMIC_THERMAL_MID_MAX) {
        plan->thermal_action = R1_PMIC_THERMAL_ACTION_WRITE_LIMIT_REGISTER;
        plan->thermal_register = R1_PMIC_THERMAL_LIMIT_REGISTER;
        plan->thermal_register_value = R1_PMIC_THERMAL_LIMIT_VALUE;
    }
    return true;
}

static void clear_pmic_charged_plan(r1_pmic_charged_plan *plan) {
    uint8_t *bytes = (uint8_t *)plan;
    for (size_t index = 0u; index < sizeof *plan; ++index) {
        bytes[index] = 0u;
    }
}

static void plan_pmic_charged_completion(
    const r1_pmic_charged_observation *observation,
    r1_pmic_charged_plan *plan) {
    plan->inspect_interrupt_status = true;
    if (observation->interrupt_status_read_succeeded) {
        if (observation->interrupt_status == 0u &&
            observation->mailbox_charge == R1_CHARGE_NOT_CHARGING) {
            plan->cancel_retry_work = true;
            plan->invoke_charge_event = true;
            plan->charge_event = 0u;
            return;
        }
        plan->close_touch_source_one =
            (observation->interrupt_status &
             R1_PMIC_CHARGED_IT_TOUCH_CLOSE_MASK) != 0u;
    }

    plan->cancel_retry_work = true;
    plan->read_mailbox_control = true;
    if (observation->mailbox_control_first_status == 0u) {
        plan->enable_mailbox = true;
        plan->reread_mailbox_control = true;
        plan->charge_event = observation->mailbox_control_second_status;
    } else {
        plan->charge_event = observation->mailbox_control_first_status;
    }
    plan->invoke_charge_event = true;
    plan->schedule_post_charge = true;
    plan->post_charge_delay_milliseconds = R1_PMIC_CHARGED_POST_DELAY_MS;
    plan->invoke_post_charge_device_callback = true;
}

bool r1_pmic_plan_charged_notification(
    const r1_pmic_charged_observation *observation,
    r1_pmic_charged_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return false;
    }

    clear_pmic_charged_plan(plan);
    uint8_t retry_counter = observation->retry_counter;
    if (retry_counter == R1_PMIC_CHARGED_RETRY_MARKER) {
        retry_counter = 0u;
        if (observation->marker_charge == R1_CHARGE_NOT_CHARGING) {
            plan->retry_counter = retry_counter;
            plan->cancel_retry_work = true;
            plan->thread_flags_to_set = R1_PMIC_CHARGED_THREAD_FLAG;
            return true;
        }
    }

    plan->retry_counter = retry_counter;
    if (observation->current_sense_millivolts <
            R1_PMIC_CHARGED_CURRENT_THRESHOLD_MV &&
        observation->battery_millivolts <
            R1_PMIC_CHARGED_BATTERY_THRESHOLD_MV) {
        const uint8_t old_counter = retry_counter;
        retry_counter = (uint8_t)(retry_counter + UINT8_C(1));
        plan->retry_counter = retry_counter;
        if (old_counter <= R1_PMIC_CHARGED_RETRY_MAX_OLD_COUNT) {
            if (observation->retry_charge != R1_CHARGE_NOT_CHARGING &&
                observation->retry_charge != R1_CHARGE_FULL) {
                plan->pulse_recovery_pin = true;
                plan->recovery_pulse_milliseconds =
                    R1_PMIC_CHARGED_RECOVERY_PULSE_MS;
                plan->schedule_retry = true;
                plan->retry_delay_milliseconds =
                    R1_PMIC_CHARGED_RETRY_DELAY_MS;
                return true;
            }
            if (observation->retry_charge == R1_CHARGE_FULL) {
                plan->retry_counter = 0u;
            }
            plan_pmic_charged_completion(observation, plan);
            return true;
        }
    }

    plan->retry_counter = 0u;
    plan_pmic_charged_completion(observation, plan);
    return true;
}

r1_pmic_delayed_callback_plan r1_pmic_retry_callback_plan(void) {
    return (r1_pmic_delayed_callback_plan){
        .reschedule_self = true,
        .delay_argument = R1_PMIC_CHARGED_RETRY_DELAY_MS,
        .thread_flags_to_set = R1_PMIC_RETRY_CALLBACK_THREAD_FLAG,
    };
}

r1_pmic_delayed_callback_plan r1_pmic_post_timer_callback_plan(void) {
    return (r1_pmic_delayed_callback_plan){
        .thread_flags_to_set = R1_PMIC_POST_TIMER_THREAD_FLAG,
    };
}

r1_pmic_delayed_callback_plan r1_pmic_post_device_callback_plan(void) {
    return (r1_pmic_delayed_callback_plan){
        .invoke_device_slot_0c = true,
        .thread_flags_to_set = R1_PMIC_POST_DEVICE_THREAD_FLAG,
    };
}

r1_pmic_delayed_callback_plan r1_pmic_charge_i2c_callback_plan(void) {
    return (r1_pmic_delayed_callback_plan){
        .invoke_device_slot_0c = true,
        .thread_flags_to_set = R1_PMIC_CHARGE_I2C_THREAD_FLAG,
    };
}

r1_error r1_pmic_late_init_plan_build(
    uint8_t configuration_byte, r1_pmic_late_init_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_pmic_late_init_plan){
        .actions = {
            R1_PMIC_LATE_INIT_CLEAR_READY_FLAG,
            R1_PMIC_LATE_INIT_ACQUIRE_NFC_RESOURCE,
            R1_PMIC_LATE_INIT_DELAY,
            R1_PMIC_LATE_INIT_CONFIGURE_ST25DVXXKC,
            R1_PMIC_LATE_INIT_RELEASE_NFC_RESOURCE,
            R1_PMIC_LATE_INIT_RUN_CHARGE_I2C_EVENT_ZERO,
            R1_PMIC_LATE_INIT_INSTALL_YHM_CALLBACK,
            R1_PMIC_LATE_INIT_INSTALL_DEVICE_CALLBACK,
        },
        .action_count = R1_PMIC_LATE_INIT_ACTION_COUNT - 1u,
        .settle_milliseconds = R1_PMIC_LATE_INIT_SETTLE_MS,
        .factory_callback_delay_ticks =
            R1_PMIC_LATE_INIT_FACTORY_DELAY_TICKS,
    };
    if (configuration_byte == UINT8_C(0x55)) {
        plan->actions[plan->action_count++] =
            R1_PMIC_LATE_INIT_SCHEDULE_FACTORY_CALLBACK;
    }
    return R1_OK;
}
