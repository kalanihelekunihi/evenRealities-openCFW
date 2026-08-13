#ifndef OPENR1_R1_STATE_H
#define OPENR1_R1_STATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_health.h"

typedef enum {
    R1_CHARGE_UNKNOWN = 0,
    R1_CHARGE_CHARGING = 1,
    R1_CHARGE_NOT_CHARGING = 2,
    R1_CHARGE_FULL = 3
} r1_charge_state;

typedef enum {
    R1_WEAR_UNKNOWN = 0,
    R1_WEAR_NOT_WORN = 1,
    R1_WEAR_WORN = 2
} r1_wear_state;

typedef struct {
    uint8_t gender;
    uint8_t age_years;
    uint16_t height_cm;
    uint16_t weight_kg;
    bool valid;
} r1_user_profile;

typedef struct {
    uint8_t age_years;
    uint8_t binary_sex;
    uint8_t height_cm;
    uint8_t weight_kg;
    int16_t parameter_a;
    int16_t parameter_b;
    int16_t parameter_c;
    uint16_t reserved;
} r1_algorithm_user_profile;

typedef struct {
    bool valid;
    bool changed;
    bool persist;
    bool significant_change;
    bool reinitialize_provider;
} r1_user_profile_transition_plan;

#define R1_SYSTEM_SETTINGS_BYTES 12u
#define R1_SYSTEM_SETTINGS_SWITCH_TYPE_REG1 0u
#define R1_TEMPERATURE_TIMED_MODE_PERIOD 600u

typedef struct {
    bool write_command;
    bool acknowledgement_precedes_effects;
    bool response_requested;
    bool payload_valid;
    bool persistent_update_requested;
    bool regulator_update_requested;
    bool normalized_enabled;
    uint8_t response[R1_SYSTEM_SETTINGS_BYTES];
} r1_system_settings_command_plan;

typedef struct {
    bool changed;
    bool unregister_previous_stream;
    bool stop_timed_mode;
    bool create_timed_mode;
    uint32_t timed_mode_period;
} r1_temperature_mode_transition_plan;

typedef struct {
    uint8_t battery_percent;
    r1_charge_state charge;
    r1_wear_state wear;
    bool touch_enabled;
    uint16_t timezone_minutes_raw;
    uint32_t unix_seconds;
    r1_user_profile profile;
    uint8_t health_settings[12];
    uint8_t system_settings[12];
    uint8_t serial_number[15];
    char application_version[16];
    char hardware_version[16];
    r1_health_state health;
} r1_device_state;

void r1_state_initialize(r1_device_state *state);
bool r1_algorithm_user_profile_valid(const r1_algorithm_user_profile *profile);
r1_error r1_user_profile_plan_transition(
    const r1_algorithm_user_profile *current,
    const r1_algorithm_user_profile *next,
    bool provider_initialized, r1_user_profile_transition_plan *plan);
r1_error r1_system_settings_plan_command(
    bool write_command, bool stored_enabled, const uint8_t *payload,
    size_t payload_length, r1_system_settings_command_plan *plan);
r1_error r1_temperature_mode_plan_transition(
    uint8_t previous_mode, uint8_t next_mode,
    bool previous_stream_registered, bool timed_mode_registered,
    r1_temperature_mode_transition_plan *plan);

#endif
