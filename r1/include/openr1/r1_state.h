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
/* Recovered persistence site of the normalized REG1 enable flag: bit 1 of
 * byte 24 in the kv.bin `dev_info` payload (R1-196,
 * FRONTIER-256-262-CORRELATION.md). */
#define R1_DEV_INFO_REG1_FLAG_OFFSET 24u
#define R1_DEV_INFO_REG1_FLAG_MASK UINT8_C(0x02)
#define R1_TEMPERATURE_TIMED_MODE_PERIOD 600u
#define R1_HEART_RATE_TIMED_MODE_PERIOD 600u
#define R1_SYSTEM_CONTROL_MAX_REPLY_BYTES 64u
#define R1_SYSTEM_CONTROL_DELAY_TICKS 200u

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
    bool changed;
    bool unregister_previous_stream;
    bool stop_mode_timer;
    bool stop_measurement_timer;
    bool stop_hrv_timer;
    bool clear_hrv_timing_state;
    bool create_mode_timer;
    uint32_t mode_timer_period;
} r1_heart_rate_mode_transition_plan;

typedef enum {
    R1_SYSTEM_CONTROL_RESET_NONE = 0,
    R1_SYSTEM_CONTROL_RESET_STANDARD = 4,
    R1_SYSTEM_CONTROL_RESET_CONFIRMED = 5,
    R1_SYSTEM_CONTROL_RESET_MARKED = 6,
    R1_SYSTEM_CONTROL_RESET_ALTERNATE = 7
} r1_system_control_reset_action;

typedef struct {
    bool send_reply;
    size_t reply_length;
    bool zero_reply_byte4;
    bool set_configuration_byte;
    uint8_t configuration_byte;
    bool refresh_configuration;
    bool delay_requested;
    uint32_t delay_ticks;
    bool persist_reset_trace;
    bool system_reset_requested;
    r1_system_control_reset_action reset_action;
} r1_system_control_command_37_result;

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
/* Reads the persisted normalized REG1 enable flag from a kv.bin `dev_info`
 * payload image.  Returns false for a short or absent image (fail closed;
 * the kv defaults are zeroed). */
bool r1_system_settings_reg1_enabled(const uint8_t *dev_info, size_t length);
/* Sets or clears the persisted REG1 flag in a `dev_info` payload image
 * without touching any other byte. */
r1_error r1_system_settings_store_reg1(
    uint8_t *dev_info, size_t length, bool enabled);
r1_error r1_temperature_mode_plan_transition(
    uint8_t previous_mode, uint8_t next_mode,
    bool previous_stream_registered, bool timed_mode_registered,
    r1_temperature_mode_transition_plan *plan);
r1_error r1_heart_rate_mode_plan_transition(
    uint8_t previous_mode, uint8_t next_mode,
    bool previous_stream_registered, bool mode_timer_registered,
    bool measurement_timer_registered, bool hrv_timer_registered,
    r1_heart_rate_mode_transition_plan *plan);
r1_error r1_system_control_command_37_plan(
    uint8_t subcommand, uint32_t request_word, uint8_t configuration_byte,
    uint8_t variable_reply_bytes, r1_system_control_command_37_result *plan);

#endif
