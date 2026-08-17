#ifndef OPENR1_R1_BATTERY_H
#define OPENR1_R1_BATTERY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_state.h"

#define R1_BATTERY_SAMPLE_COUNT 5u
#define R1_NFC_RECTIFIER_SAMPLE_COUNT 3u
#define R1_PMIC_CURRENT_SAMPLE_COUNT 3u
#define R1_BATTERY_PROFILE_COUNT 4u
#define R1_BATTERY_CURVE_SEGMENTS 20u
#define R1_PMIC_CHARGE_STATUS_BUFFER_SIZE 24u
#define R1_PMIC_CHARGE_EVENT_SAMPLE UINT8_C(1)
#define R1_PMIC_CHARGE_EVENT_PRESERVE_WORK UINT8_C(0x5a)
#define R1_PMIC_THERMAL_LOW_TARGET_WORD UINT32_C(0x40808312)
#define R1_PMIC_THERMAL_MID_TARGET_WORD UINT32_C(0x4160f5c3)
#define R1_PMIC_THERMAL_LIMIT_REGISTER UINT8_C(2)
#define R1_PMIC_THERMAL_LIMIT_VALUE UINT8_C(0xf8)
#define R1_PMIC_CHARGED_RETRY_MARKER UINT8_C(0xa5)
#define R1_PMIC_CHARGED_CURRENT_THRESHOLD_MV UINT16_C(50)
#define R1_PMIC_CHARGED_BATTERY_THRESHOLD_MV UINT16_C(4200)
#define R1_PMIC_CHARGED_RETRY_MAX_OLD_COUNT UINT8_C(12)
#define R1_PMIC_CHARGED_RETRY_DELAY_MS UINT16_C(409)
#define R1_PMIC_CHARGED_RECOVERY_PULSE_MS UINT16_C(200)
#define R1_PMIC_CHARGED_POST_DELAY_MS UINT16_C(5120)
#define R1_PMIC_CHARGED_THREAD_FLAG UINT32_C(0x10)
#define R1_PMIC_CHARGE_I2C_THREAD_FLAG UINT32_C(0x02)
#define R1_PMIC_RETRY_CALLBACK_THREAD_FLAG UINT32_C(0x04)
#define R1_PMIC_POST_TIMER_THREAD_FLAG UINT32_C(0x08)
#define R1_PMIC_POST_DEVICE_THREAD_FLAG UINT32_C(0x01)
#define R1_PMIC_CHARGED_IT_TOUCH_CLOSE_MASK UINT8_C(0x08)
#define R1_BATTERY_DIAGNOSTIC_STATUS_PERIOD UINT8_C(5)
#define R1_BATTERY_DIAGNOSTIC_FULL_PERIOD UINT8_C(30)
#define R1_PMIC_LATE_INIT_SETTLE_MS UINT16_C(50)
#define R1_PMIC_LATE_INIT_FACTORY_DELAY_TICKS UINT16_C(1024)
#define R1_PMIC_LATE_INIT_ACTION_COUNT 9u
#define R1_FACTORY_PMIC_REGISTER_DIAGNOSTIC_BYTES 10u
#define R1_FACTORY_PMIC_POWER_STATE_OFF UINT8_C(2)
#define R1_FACTORY_PMIC_BATTERY_MILLIVOLT_MASK UINT16_C(0x3fff)
#define R1_FACTORY_PMIC_POWER_THREAD_FLAG UINT32_C(1)
#define R1_ANALOG_CHANNEL_COUNT 3u
#define R1_ANALOG_PROVIDER_STATUS_OK UINT8_C(0)
#define R1_ANALOG_PROVIDER_STATUS_NOT_FOUND UINT8_C(1)

typedef struct {
    uint8_t percent;
    uint32_t accumulated_seconds;
} r1_battery_charge_progress;

typedef struct {
    r1_battery_charge_progress state;
    uint8_t reported_percent;
} r1_battery_charge_result;

typedef struct {
    bool has_previous_percent;
    uint8_t previous_percent;
    uint16_t previous_millivolts;
    bool already_recovered;
} r1_battery_stuck_state;

typedef struct {
    r1_battery_stuck_state state;
    bool has_replacement_percent;
    uint8_t replacement_progress_percent;
    bool observation_baseline_updated;
    bool should_reset_charge_progress;
} r1_battery_stuck_result;

/*
 * R1-owned estimator state. Physical sampling and PMIC state must be supplied
 * by an admitted platform provider; this type contains no vendor transport.
 */
typedef struct {
    uint8_t battery_type;
    r1_charge_state charge;
    uint16_t millivolts;
    uint8_t percent;
    uint8_t charged_refresh_count;
    r1_battery_charge_progress charge_progress;
    r1_battery_stuck_state stuck;
    uint32_t stuck_unchanged_seconds;
} r1_battery_controller;

/*
 * Pure R1 charge-event policy. YHM register access, ST mailbox polling,
 * timers, logging, and internal-event publication stay with admitted
 * providers/executors and are intentionally absent from this interface.
 */
typedef struct {
    r1_charge_state charge;
    uint8_t event;
    uint8_t battery_percent;
    uint16_t charge_temperature_milliunits;
    uint16_t battery_millivolts;
    uint16_t nfc_rectifier_millivolts;
    uint8_t raw_power_flags;
    uint8_t pmic_ready_flag;
    uint32_t current_thermal_target_word;
} r1_pmic_charge_observation;

typedef enum {
    R1_PMIC_TRANSITION_NONE = 0,
    R1_PMIC_TRANSITION_NOT_CHARGING
} r1_pmic_transition;

typedef enum {
    R1_PMIC_THERMAL_ACTION_NONE = 0,
    R1_PMIC_THERMAL_ACTION_SET_TARGET,
    R1_PMIC_THERMAL_ACTION_WRITE_LIMIT_REGISTER
} r1_pmic_thermal_action;

typedef struct {
    bool cancel_event_work;
    bool process_dock_mailbox;
    r1_pmic_transition transition;
    r1_pmic_thermal_action thermal_action;
    uint32_t thermal_target_word;
    uint8_t thermal_register;
    uint8_t thermal_register_value;
    uint8_t dock_status[R1_PMIC_CHARGE_STATUS_BUFFER_SIZE];
} r1_pmic_charge_plan;

/*
 * Normalized inputs for the R1-owned PMIC-charged notification policy.
 * The three charge observations correspond to distinct stock call sites and
 * may be collected lazily. Nordic GPIO/CMSIS execution and ST25DVxxKC reads
 * remain outside this clean-room interface.
 */
typedef struct {
    uint8_t retry_counter;
    r1_charge_state marker_charge;
    uint16_t current_sense_millivolts;
    uint16_t battery_millivolts;
    r1_charge_state retry_charge;
    bool interrupt_status_read_succeeded;
    uint8_t interrupt_status;
    r1_charge_state mailbox_charge;
    uint8_t mailbox_control_first_status;
    uint8_t mailbox_control_second_status;
} r1_pmic_charged_observation;

typedef struct {
    uint8_t retry_counter;
    bool cancel_retry_work;
    uint32_t thread_flags_to_set;
    bool pulse_recovery_pin;
    uint16_t recovery_pulse_milliseconds;
    bool schedule_retry;
    uint16_t retry_delay_milliseconds;
    bool inspect_interrupt_status;
    bool close_touch_source_one;
    bool read_mailbox_control;
    bool enable_mailbox;
    bool reread_mailbox_control;
    bool invoke_charge_event;
    uint8_t charge_event;
    bool schedule_post_charge;
    uint16_t post_charge_delay_milliseconds;
    bool invoke_post_charge_device_callback;
} r1_pmic_charged_plan;

/* Exact action-only contracts of the four PMIC delayed callbacks that
 * Ghidra identified as Thumb labels rather than function entries.  The
 * executor owns timer, device-registry, and thread-flag provider calls. */
typedef struct {
    bool reschedule_self;
    uint16_t delay_argument;
    bool invoke_device_slot_0c;
    uint32_t thread_flags_to_set;
} r1_pmic_delayed_callback_plan;

typedef enum {
    R1_PMIC_LATE_INIT_CLEAR_READY_FLAG = 0,
    R1_PMIC_LATE_INIT_ACQUIRE_NFC_RESOURCE,
    R1_PMIC_LATE_INIT_DELAY,
    R1_PMIC_LATE_INIT_CONFIGURE_ST25DVXXKC,
    R1_PMIC_LATE_INIT_RELEASE_NFC_RESOURCE,
    R1_PMIC_LATE_INIT_RUN_CHARGE_I2C_EVENT_ZERO,
    R1_PMIC_LATE_INIT_INSTALL_YHM_CALLBACK,
    R1_PMIC_LATE_INIT_INSTALL_DEVICE_CALLBACK,
    R1_PMIC_LATE_INIT_SCHEDULE_FACTORY_CALLBACK
} r1_pmic_late_init_action;

typedef struct {
    r1_pmic_late_init_action actions[R1_PMIC_LATE_INIT_ACTION_COUNT];
    size_t action_count;
    uint16_t settle_milliseconds;
    uint16_t factory_callback_delay_ticks;
} r1_pmic_late_init_plan;

typedef struct {
    uint8_t next_counter;
    bool status_log_requested;
    bool compensation_log_requested;
} r1_battery_diagnostic_cadence;

/* Pure values consumed by the three eAT PMIC diagnostic handlers. Provider
 * reads, persistence, thread signaling, and text output remain external. */
typedef struct {
    uint32_t current_sense_millivolts;
    uint8_t handler_return_value;
} r1_factory_pmic_current_diagnostic_plan;

typedef struct {
    uint32_t timestamp;
    uint16_t raw_battery_millivolts;
    uint16_t stored_battery_millivolts;
    uint16_t packed_dev_info_word;
    bool persist_dev_info_requested;
    bool signal_power_thread_requested;
    uint32_t power_thread_flags;
    uint8_t handler_return_value;
} r1_factory_pmic_power_off_plan;

typedef struct {
    uint8_t formatted_registers[R1_FACTORY_PMIC_REGISTER_DIAGNOSTIC_BYTES];
    uint8_t handler_return_value;
} r1_factory_pmic_register_diagnostic_plan;

typedef enum {
    R1_ANALOG_CHANNEL_BATTERY = 0,
    R1_ANALOG_CHANNEL_PMIC_CURRENT = 1,
    R1_ANALOG_CHANNEL_NFC_RECTIFIER = 2,
    R1_ANALOG_CHANNEL_INVALID = 3
} r1_analog_channel;

typedef struct {
    bool channel_open[R1_ANALOG_CHANNEL_COUNT];
    bool driver_initialized;
} r1_analog_close_state;

typedef struct {
    uint8_t provider_status;
    bool uninitialize_channel;
    uint8_t nrfx_channel;
    bool clear_channel_open;
    bool uninitialize_driver;
    bool clear_driver_initialized;
} r1_analog_close_plan;

bool r1_battery_base_millivolts(const uint16_t *samples, size_t count,
                                uint16_t *millivolts);
bool r1_battery_runtime_millivolts(const uint16_t *samples, size_t count,
                                   int16_t nv_compensation_millivolts,
                                   r1_charge_state charge,
                                   uint16_t *millivolts);
bool r1_nfc_rectifier_millivolts(const int16_t *samples, size_t count,
                                 uint16_t *millivolts);
bool r1_pmic_current_sense_millivolts(const int16_t *samples, size_t count,
                                      uint16_t *millivolts);

uint8_t r1_battery_discharge_percent(uint16_t millivolts,
                                     uint8_t battery_type,
                                     uint8_t charged_refresh_count);
uint8_t r1_battery_charging_initial_percent(uint16_t millivolts,
                                            uint8_t battery_type);
r1_battery_charge_result r1_battery_advance_charging(
    r1_battery_charge_progress state, uint32_t elapsed_seconds,
    uint8_t battery_type, uint16_t millivolts,
    uint8_t charged_refresh_count);
uint8_t r1_battery_updated_charged_refresh_count(
    uint8_t previous, r1_charge_state charge);

bool r1_battery_stalled_replacement(
    uint8_t current_percent, uint8_t previous_percent,
    uint16_t previous_millivolts, uint16_t current_millivolts,
    uint32_t unchanged_seconds, bool already_recovered,
    uint8_t battery_type, uint8_t *replacement_percent);
r1_battery_stuck_result r1_battery_update_stuck_recovery(
    r1_battery_stuck_state state, r1_charge_state charge,
    uint8_t current_percent, uint16_t current_millivolts,
    uint32_t unchanged_seconds, uint8_t battery_type);

void r1_battery_controller_initialize(
    r1_battery_controller *controller, uint8_t battery_type,
    uint8_t initial_percent, r1_charge_state initial_charge);
void r1_battery_controller_set_type(
    r1_battery_controller *controller, uint8_t battery_type);
bool r1_battery_controller_update(
    r1_battery_controller *controller, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds);
bool r1_pmic_plan_charge_event(
    const r1_pmic_charge_observation *observation,
    r1_pmic_charge_plan *plan);
bool r1_pmic_plan_charged_notification(
    const r1_pmic_charged_observation *observation,
    r1_pmic_charged_plan *plan);
r1_pmic_delayed_callback_plan r1_pmic_retry_callback_plan(void);
r1_pmic_delayed_callback_plan r1_pmic_post_timer_callback_plan(void);
r1_pmic_delayed_callback_plan r1_pmic_post_device_callback_plan(void);
r1_pmic_delayed_callback_plan r1_pmic_charge_i2c_callback_plan(void);
r1_error r1_pmic_late_init_plan_build(
    uint8_t configuration_byte, r1_pmic_late_init_plan *plan);
r1_battery_diagnostic_cadence r1_battery_diagnostic_cadence_step(
    uint8_t previous_counter);
r1_error r1_factory_pmic_current_diagnostic_plan_build(
    uint32_t current_sense_millivolts,
    r1_factory_pmic_current_diagnostic_plan *plan);
r1_error r1_factory_pmic_power_off_plan_build(
    uint32_t timestamp, uint16_t battery_millivolts,
    r1_factory_pmic_power_off_plan *plan);
r1_error r1_factory_pmic_register_diagnostic_plan_build(
    uint8_t register_9, r1_factory_pmic_register_diagnostic_plan *plan);
r1_error r1_analog_close_plan_build(
    r1_analog_channel channel, const r1_analog_close_state *state,
    r1_analog_close_plan *plan);

#endif
