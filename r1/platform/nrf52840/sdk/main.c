#include <stdint.h>
#include <string.h>

#include "ble.h"
#include "app_timer.h"
#include "nrf.h"
#include "nrf_error.h"
#include "nrf_soc.h"
#include "nrf_sdh.h"
#include "nrf_sdh_ble.h"

#include "openr1_bae8.h"
#include "openr1_advertising.h"
#include "openr1_analog.h"
#include "openr1_cmbacktrace_port.h"
#include "openr1_gatt.h"
#include "openr1_i2c5_resources.h"
#include "openr1_motion.h"
#include "openr1_nfc.h"
#include "openr1_peer.h"
#include "openr1_reset_reason.h"
#include "openr1_scheduler.h"
#include "openr1_storage.h"
#include "openr1_touch.h"

#include "openr1/r1_runtime.h"
#include "openr1/r1_battery.h"
#include "openr1/r1_health.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_peer_target.h"
#include "openr1/r1_storage.h"

void openr1_platform_initialize(void);
r1_runtime *openr1_platform_runtime(void);

#define OPENR1_CONNECTION_CONFIGURATION_TAG 1u
#define OPENR1_EXPECTED_RAM_START UINT32_C(0x200064a8)
#define OPENR1_HVN_QUEUE_SIZE 4u

static volatile uint32_t startup_error;

typedef r1_error (*openr1_delayed_event_step_fn)(
    r1_delayed_event_state *, uint32_t, uint32_t,
    r1_delayed_event_step_result *);

__attribute__((used, section(".openr1_event_api")))
static const openr1_delayed_event_step_fn retained_delayed_event_step =
    r1_delayed_event_timer_step;

typedef r1_response_result (*openr1_response_send_fn)(
    uint16_t, bool, bool, const r1_response_header *, uint8_t,
    uint16_t *, const uint8_t *, size_t, r1_protocol_allocate_fn,
    r1_protocol_release_fn, r1_protocol_send_fn, void *);

__attribute__((used, section(".openr1_protocol_api")))
static const openr1_response_send_fn retained_response_send =
    r1_protocol_send_response;

typedef r1_error (*openr1_ble_thread_encode_fn)(
    uint32_t, uint32_t, const uint8_t *, size_t, uint8_t *, size_t, size_t *);
typedef r1_error (*openr1_profile_transition_fn)(
    const r1_algorithm_user_profile *, const r1_algorithm_user_profile *,
    bool, r1_user_profile_transition_plan *);
typedef r1_bond_diagnostic_result (*openr1_bond_diagnostic_fn)(uint16_t, int);
typedef r1_error (*openr1_glasses_status_fn)(
    bool, uint8_t, bool, bool, bool, r1_glasses_status_plan *);
typedef r1_error (*openr1_peripheral_watchdog_fn)(
    uint8_t, uint32_t, bool, bool, int, int, r1_peripheral_watchdog_plan *);
typedef r1_error (*openr1_temperature_pair_reduce_fn)(
    const int32_t[R1_TEMPERATURE_PAIR_SENSOR_COUNT]
                 [R1_TEMPERATURE_PAIR_SAMPLE_COUNT],
    const r1_temperature_pair_calibration *, r1_temperature_pair_result *);
typedef r1_error (*openr1_health_clear_all_fn)(
    bool, uint32_t, int16_t, r1_activity_history *, r1_health_u8_history *,
    r1_health_u8_history *, r1_health_u8_history *, r1_health_u8_history *,
    r1_health_u16_history *, r1_health_clear_all_result *);
typedef r1_error (*openr1_pb_fragment_fn)(
    uint8_t, const uint8_t *, size_t, r1_pb_fragment_set *);
typedef r1_error (*openr1_delayed_event_schedule_fn)(
    r1_delayed_event_state *, uint32_t, uint32_t, uint32_t, uint32_t,
    r1_delayed_event_schedule_result *);
typedef r1_error (*openr1_health_settings_plan_fn)(
    bool, const r1_health_settings_record *, const uint8_t *, size_t,
    r1_health_settings_command_plan *);
typedef r1_battery_diagnostic_cadence (*openr1_battery_diagnostic_cadence_fn)(
    uint8_t);
typedef r1_error (*openr1_ep_scan_cursor_fn)(
    const uint8_t *, size_t, r1_ep_scan_result *);
typedef r1_error (*openr1_eus_fragment_fn)(
    const uint8_t *, size_t, r1_fragment_set *);

__attribute__((used, section(".openr1_frontier_api")))
static const openr1_ble_thread_encode_fn retained_ble_thread_encode =
    r1_ble_thread_message_encode;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_profile_transition_fn retained_profile_transition =
    r1_user_profile_plan_transition;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_bond_diagnostic_fn retained_bond_diagnostic =
    r1_peer_bond_diagnostic_plan;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_glasses_status_fn retained_glasses_status =
    r1_glasses_status_plan_command;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_ble_thread_encode_fn retained_factory_thread_encode =
    r1_factory_thread_message_encode;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_peripheral_watchdog_fn retained_peripheral_watchdog =
    r1_peripheral_watchdog_plan_step;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_temperature_pair_reduce_fn retained_temperature_pair_reduce =
    r1_temperature_pair_reduce;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_health_clear_all_fn retained_health_clear_all =
    r1_health_clear_all_caches;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_pb_fragment_fn retained_pb_fragment =
    r1_pb_fragment_message;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_delayed_event_schedule_fn retained_delayed_event_schedule =
    r1_delayed_event_schedule;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_health_settings_plan_fn retained_health_settings_plan =
    r1_health_settings_plan_command;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_battery_diagnostic_cadence_fn retained_battery_diagnostic_cadence =
    r1_battery_diagnostic_cadence_step;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_ep_scan_cursor_fn retained_ep_scan_cursor =
    r1_ep_scan_cursor;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_eus_fragment_fn retained_eus_fragment =
    r1_fragment_message;

static void touch_enabled_changed(void *context, bool enabled) {
    (void)context;
    const ret_code_t error = openr1_touch_set_enabled(enabled);
    if (error != NRF_SUCCESS) {
        startup_error = error;
    }
}

static void fail(ret_code_t error) {
    startup_error = error;
    for (;;) {
        __WFE();
    }
}

static ret_code_t configure_hvn_queue(uint32_t ram_start) {
    ble_cfg_t configuration;
    memset(&configuration, 0, sizeof configuration);
    configuration.conn_cfg.conn_cfg_tag = OPENR1_CONNECTION_CONFIGURATION_TAG;
    configuration.conn_cfg.params.gatts_conn_cfg.hvn_tx_queue_size =
        OPENR1_HVN_QUEUE_SIZE;
    return sd_ble_cfg_set(BLE_CONN_CFG_GATTS, &configuration, ram_start);
}

static ret_code_t enable_extended_rc_calibration(void) {
    ble_opt_t option;
    memset(&option, 0, sizeof option);
    option.common_opt.extended_rc_cal.enable = 1u;
    return sd_ble_opt_set(BLE_COMMON_OPT_EXTENDED_RC_CAL, &option);
}

static void softdevice_initialize(void) {
    ret_code_t error = nrf_sdh_enable_request();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    uint32_t ram_start = OPENR1_EXPECTED_RAM_START;
    error = nrf_sdh_ble_default_cfg_set(OPENR1_CONNECTION_CONFIGURATION_TAG, &ram_start);
    if (error != NRF_SUCCESS || ram_start != OPENR1_EXPECTED_RAM_START) {
        fail(error == NRF_SUCCESS ? NRF_ERROR_INVALID_ADDR : error);
    }
    error = configure_hvn_queue(ram_start);
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = nrf_sdh_ble_enable(&ram_start);
    if (error != NRF_SUCCESS || ram_start != OPENR1_EXPECTED_RAM_START) {
        fail(error == NRF_SUCCESS ? NRF_ERROR_NO_MEM : error);
    }
    error = enable_extended_rc_calibration();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = app_timer_init();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_storage_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_analog_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_touch_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    r1_runtime *runtime = openr1_platform_runtime();
    r1_runtime_set_touch_handler(
        runtime, touch_enabled_changed, NULL);
    touch_enabled_changed(NULL, runtime->device.touch_enabled);
    error = openr1_nfc_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_i2c5_resources_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_motion_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_gatt_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_advertising_initialize(
        false, runtime->device.serial_number, false);
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_bae8_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_peer_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_advertising_start();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
}

int main(void) {
    openr1_reset_reason_initialize();
    openr1_cmbacktrace_initialize();
    openr1_platform_initialize();
    const ret_code_t error = openr1_scheduler_initialize(softdevice_initialize);
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    openr1_scheduler_start();
}
