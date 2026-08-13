#include "openr1/r1_state.h"

#include <stddef.h>

_Static_assert(sizeof(r1_algorithm_user_profile) == 12u,
               "algorithm user profile must retain its 12-byte wire shape");

static void clear_bytes(uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

static void copy_string(char *output, size_t capacity, const char *input) {
    size_t index = 0u;
    while (index + 1u < capacity && input[index] != '\0') {
        output[index] = input[index];
        ++index;
    }
    while (index < capacity) {
        output[index] = '\0';
        ++index;
    }
}

bool r1_algorithm_user_profile_valid(const r1_algorithm_user_profile *profile) {
    return profile != NULL && profile->age_years >= 11u &&
        profile->age_years <= 99u && profile->binary_sex <= 1u &&
        profile->height_cm >= 101u && profile->height_cm <= 219u &&
        profile->weight_kg >= 31u && profile->weight_kg <= 149u;
}

static uint8_t absolute_u8_difference(uint8_t left, uint8_t right) {
    return left >= right ? (uint8_t)(left - right) : (uint8_t)(right - left);
}

r1_error r1_user_profile_plan_transition(
    const r1_algorithm_user_profile *current,
    const r1_algorithm_user_profile *next,
    bool provider_initialized, r1_user_profile_transition_plan *plan) {
    if (current == NULL || next == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_user_profile_transition_plan){0};
    plan->valid = r1_algorithm_user_profile_valid(next);
    const uint8_t *old_bytes = (const uint8_t *)current;
    const uint8_t *new_bytes = (const uint8_t *)next;
    for (size_t index = 0u; index < 12u; ++index) {
        plan->changed = plan->changed || old_bytes[index] != new_bytes[index];
    }
    plan->persist = plan->valid && plan->changed;
    plan->significant_change = plan->persist &&
        (current->binary_sex != next->binary_sex ||
         absolute_u8_difference(current->age_years, next->age_years) > 2u ||
         absolute_u8_difference(current->height_cm, next->height_cm) > 9u ||
         absolute_u8_difference(current->weight_kg, next->weight_kg) > 9u);
    plan->reinitialize_provider = provider_initialized && plan->significant_change;
    return R1_OK;
}

r1_error r1_system_settings_plan_command(
    bool write_command, bool stored_enabled, const uint8_t *payload,
    size_t payload_length, r1_system_settings_command_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_system_settings_command_plan){
        .write_command = write_command,
        .acknowledgement_precedes_effects = write_command,
    };
    if (!write_command) {
        plan->response_requested = true;
        plan->response[5] = stored_enabled ? 1u : 0u;
        return R1_OK;
    }
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length != R1_SYSTEM_SETTINGS_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (payload[4] != R1_SYSTEM_SETTINGS_SWITCH_TYPE_REG1) {
        return R1_OK;
    }
    plan->payload_valid = true;
    const uint8_t stored = stored_enabled ? 1u : 0u;
    if (payload[5] == stored) {
        plan->normalized_enabled = stored_enabled;
        return R1_OK;
    }
    plan->normalized_enabled = payload[5] != 0u;
    plan->persistent_update_requested = true;
    plan->regulator_update_requested = true;
    return R1_OK;
}

r1_error r1_temperature_mode_plan_transition(
    uint8_t previous_mode, uint8_t next_mode,
    bool previous_stream_registered, bool timed_mode_registered,
    r1_temperature_mode_transition_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_temperature_mode_transition_plan){0};
    if (previous_mode > 2u || next_mode > 2u) {
        return R1_ERROR_ARGUMENT;
    }
    if (previous_mode == next_mode) {
        return R1_OK;
    }
    plan->changed = true;
    plan->unregister_previous_stream = previous_stream_registered;
    plan->stop_timed_mode = previous_mode == 1u && timed_mode_registered;
    plan->create_timed_mode = next_mode == 1u && !timed_mode_registered;
    if (plan->create_timed_mode) {
        plan->timed_mode_period = R1_TEMPERATURE_TIMED_MODE_PERIOD;
    }
    return R1_OK;
}

void r1_state_initialize(r1_device_state *state) {
    if (state == NULL) {
        return;
    }
    state->battery_percent = 100u;
    state->charge = R1_CHARGE_NOT_CHARGING;
    state->wear = R1_WEAR_UNKNOWN;
    state->touch_enabled = true;
    state->timezone_minutes_raw = 0u;
    state->unix_seconds = 0u;
    state->profile.gender = 0u;
    state->profile.age_years = 0u;
    state->profile.height_cm = 0u;
    state->profile.weight_kg = 0u;
    state->profile.valid = false;
    clear_bytes(state->health_settings, sizeof state->health_settings);
    clear_bytes(state->system_settings, sizeof state->system_settings);
    clear_bytes(state->serial_number, sizeof state->serial_number);
    copy_string(state->application_version, sizeof state->application_version, "2.2.6.0009");
    copy_string(state->hardware_version, sizeof state->hardware_version, "603MV1.9.3");
    r1_health_initialize(&state->health);
}
