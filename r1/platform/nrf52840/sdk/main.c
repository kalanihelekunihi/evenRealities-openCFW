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
#include "openr1_clock.h"
#include "openr1_cmbacktrace_port.h"
#include "openr1_connection_control.h"
#include "openr1_connection_params.h"
#include "openr1_databases.h"
#include "openr1_event_bus.h"
#include "openr1_gatt.h"
#include "openr1_i2c5_resources.h"
#include "openr1_motion.h"
#include "openr1_nfc.h"
#include "openr1_peer.h"
#include "openr1_reset_reason.h"
#include "openr1_rtc.h"
#include "openr1_scheduler.h"
#include "openr1_storage.h"
#include "openr1_touch.h"
#include "openr1_twim1_arbiter.h"

#include "openr1/r1_runtime.h"
#include "openr1/r1_battery.h"
#include "openr1/r1_connection_params.h"
#include "openr1/r1_event.h"
#include "openr1/r1_goodix.h"
#include "r1_gh3x2x_bind.h"
#include "openr1/r1_health.h"
#include "openr1/r1_kv_store.h"
#include "openr1/r1_motion.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_peer_target.h"
#include "openr1/r1_storage.h"
#include "openr1/r1_state.h"
#include "model_data/r1_model_data.h"

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
typedef r1_error (*openr1_delayed_event_cancel_fn)(
    r1_delayed_event_state *, uint32_t, uint32_t, uint32_t,
    r1_delayed_event_cancel_result *);
typedef r1_error (*openr1_health_settings_plan_fn)(
    bool, const r1_health_settings_record *, const uint8_t *, size_t,
    r1_health_settings_command_plan *);
typedef r1_battery_diagnostic_cadence (*openr1_battery_diagnostic_cadence_fn)(
    uint8_t);
typedef r1_error (*openr1_ep_scan_cursor_fn)(
    const uint8_t *, size_t, r1_ep_scan_result *);
typedef r1_error (*openr1_ep_initialization_plan_fn)(
    bool, bool, bool, uint32_t, r1_ep_initialization_plan *);
typedef r1_error (*openr1_kv_store_get_fn)(
    const r1_kv_store *, r1_kv_class, uint8_t *, size_t, size_t *);
typedef r1_error (*openr1_legacy_device_info_fn)(
    const uint8_t[R1_LEGACY_DEVICE_INFO_PREFIX_BYTES],
    const r1_legacy_device_info_sources *, r1_legacy_device_info_response *);
typedef r1_error (*openr1_eus_fragment_fn)(
    const uint8_t *, size_t, r1_fragment_set *);
typedef r1_error (*openr1_system_settings_plan_fn)(
    bool, bool, const uint8_t *, size_t, r1_system_settings_command_plan *);
typedef r1_error (*openr1_temperature_mode_plan_fn)(
    uint8_t, uint8_t, bool, bool, r1_temperature_mode_transition_plan *);
typedef r1_error (*openr1_heart_rate_mode_plan_fn)(
    uint8_t, uint8_t, bool, bool, bool, bool,
    r1_heart_rate_mode_transition_plan *);
typedef r1_error (*openr1_ring_stability_fn)(
    r1_ring_stability_state *, float, bool, r1_ring_stability_result *);
typedef r1_error (*openr1_phy_update_plan_fn)(
    uint16_t, bool, uint8_t, uint8_t, r1_phy_update_plan *);
typedef uint32_t (*openr1_phy_update_request_fn)(uint16_t, uint8_t, uint8_t);
typedef r1_error (*openr1_goodix_diagnostic_select_fn)(
    uint8_t[R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES], uint8_t, uint8_t *,
    size_t, size_t *);
typedef const r1_goodix_provider_ops *(*openr1_gh3x2x_provider_ops_fn)(void);
typedef void (*openr1_gh3x2x_pool_fatal_fn)(void);
typedef const void *(*openr1_gh3x2x_spo2_config_instance_fn)(void);
typedef void (*openr1_gh3x2x_spo2_config_version_fn)(char *, uint8_t);
typedef r1_error (*openr1_sleep_sync_ack_plan_fn)(
    bool, bool, r1_sleep_sync_ack_plan *);
typedef r1_error (*openr1_sleep_sync_report_plan_fn)(
    bool, uint8_t, uint8_t, uint16_t, r1_sleep_sync_report_plan *);
typedef r1_error (*openr1_system_control_37_plan_fn)(
    uint8_t, uint32_t, uint8_t, uint8_t,
    r1_system_control_command_37_result *);
typedef uint32_t (*openr1_connection_parameter_mode_apply_fn)(
    uint16_t, uint16_t, uint16_t, uint8_t, uint8_t, bool, bool,
    r1_connection_parameter_mode_plan *);
typedef r1_error (*openr1_activity_flash_record_enqueue_fn)(
    r1_activity_offline_queue *, uint32_t, int16_t, uint8_t,
    const uint32_t[6], uint32_t, uint32_t, uint32_t,
    r1_activity_flash_record_enqueue_result *);
typedef r1_error (*openr1_sensor_stream_registration_plan_fn)(
    r1_sensor_stream_registration_plan_result *);
typedef r1_error (*openr1_latest_valid_flash_slot_scan_fn)(
    const r1_flash *, uint32_t, uint32_t, uint8_t, uint32_t,
    r1_latest_valid_flash_slot_scan_result *);
typedef uint32_t (*openr1_connection_control_adv_start_fn)(
    const uint8_t *, const uint8_t *);

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
static const openr1_delayed_event_cancel_fn retained_delayed_event_cancel =
    r1_delayed_event_cancel;
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
static const openr1_ep_initialization_plan_fn retained_ep_initialization_plan =
    r1_ep_plan_initialization;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_kv_store_get_fn retained_kv_store_get =
    r1_kv_store_get;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_legacy_device_info_fn retained_legacy_device_info =
    r1_legacy_device_info_build;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_eus_fragment_fn retained_eus_fragment =
    r1_fragment_message;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_system_settings_plan_fn retained_system_settings_plan =
    r1_system_settings_plan_command;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_temperature_mode_plan_fn retained_temperature_mode_plan =
    r1_temperature_mode_plan_transition;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_heart_rate_mode_plan_fn retained_heart_rate_mode_plan =
    r1_heart_rate_mode_plan_transition;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_ring_stability_fn retained_ring_stability =
    r1_ring_stability_observe;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_phy_update_plan_fn retained_phy_update_plan =
    r1_connection_phy_update_plan;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_phy_update_request_fn retained_phy_update_request =
    openr1_bae8_request_phy_update;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_goodix_diagnostic_select_fn retained_goodix_diagnostic_select =
    r1_goodix_diagnostic_select;
/* Retains the GH3X2X democode provider (bind table, driver subset, port
 * trampolines, and fail-closed algorithm stubs) in the image through
 * --gc-sections.  Retention only: no board ops exist yet, so the provider
 * stays unbound and unreachable from any command path. */
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_gh3x2x_provider_ops_fn retained_gh3x2x_provider_ops =
    r1_gh3x2x_bind_provider_ops;
/* goodix_mem integrator surface and the pinned SPO2 config table
 * (gh3x2x-v2.23_7ecd2a, the R1's exact config tag); both are retained for
 * image parity but have no live caller while the algorithm layer is
 * absent. */
void Gh3x2xPoolIsNotEnough(void);
const void *goodix_spo2_config_get_instance(void);
void goodix_spo2_config_get_version(char *ver, uint8_t ver_len);
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_gh3x2x_pool_fatal_fn retained_gh3x2x_pool_fatal =
    Gh3x2xPoolIsNotEnough;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_gh3x2x_spo2_config_instance_fn
    retained_gh3x2x_spo2_config_instance = goodix_spo2_config_get_instance;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_gh3x2x_spo2_config_version_fn
    retained_gh3x2x_spo2_config_version = goodix_spo2_config_get_version;
/* Retain the source-admitted generated-model parameters in the application
 * image.  These typed views replace the former implicit reads from stock
 * flash addresses; algorithm runtime adoption remains separately gated. */
__attribute__((used, section(".openr1_frontier_api")))
static const r1_model_data_view *const retained_model_data[] = {
    &r1_goodix_generated_model,
    &r1_gomore_sleep_model_below_100,
    &r1_gomore_sleep_model_100_and_above,
};
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_sleep_sync_ack_plan_fn retained_sleep_sync_ack_plan =
    r1_sleep_sync_plan_acknowledgement;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_sleep_sync_report_plan_fn retained_sleep_sync_report_plan =
    r1_sleep_sync_plan_report_callback;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_system_control_37_plan_fn retained_system_control_37_plan =
    r1_system_control_command_37_plan;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_connection_parameter_mode_apply_fn
    retained_connection_parameter_mode_apply =
        openr1_connection_parameter_mode_apply;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_activity_flash_record_enqueue_fn
    retained_activity_flash_record_enqueue =
        r1_activity_flash_record_enqueue_plan;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_sensor_stream_registration_plan_fn
    retained_sensor_stream_registration_plan =
        r1_sensor_stream_registration_plan;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_latest_valid_flash_slot_scan_fn
    retained_latest_valid_flash_slot_scan =
        r1_latest_valid_flash_slot_scan_adapter;
/* Retains the advStart two-target worker entry point independently of its
 * authorized dispatcher-to-queue binding. */
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_connection_control_adv_start_fn
    retained_connection_control_adv_start =
        openr1_connection_control_adv_start;
typedef r1_event_bus *(*openr1_databases_event_bus_fn)(void);
typedef uint32_t (*openr1_event_bus_last_error_fn)(void);
/* Retains the platform event-bus access and observability seams: the
 * per-window queue sink and consumer thread are bound at startup
 * (openr1_event_bus.c), but no production publisher exists yet, so these
 * entry points have no live caller. */
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_databases_event_bus_fn retained_databases_event_bus =
    openr1_databases_event_bus;
__attribute__((used, section(".openr1_frontier_api")))
static const openr1_event_bus_last_error_fn retained_event_bus_last_error =
    openr1_event_bus_last_error;

static void touch_enabled_changed(void *context, bool enabled) {
    (void)context;
    const ret_code_t error = openr1_touch_set_enabled(enabled);
    if (error != NRF_SUCCESS) {
        startup_error = error;
    }
}

static r1_error nv_recovery_requested(
    void *context, const uint8_t body[R1_NV_RECOVERY_BODY_BYTES],
    uint16_t expected_crc) {
    (void)context;
    const ret_code_t error = openr1_databases_queue_nv_recovery(
        body, expected_crc);
    return error == NRF_SUCCESS ? R1_OK : R1_ERROR_CAPACITY;
}

static r1_error remove_ring_requested(void *context) {
    (void)context;
    return openr1_databases_queue_remove_ring() == NRF_SUCCESS
        ? R1_OK : R1_ERROR_CAPACITY;
}

/* Recovered REG1 persistence: a system-settings write for switch type zero
 * persists the normalized enable flag at kv dev_info byte 24 bit 1.  The
 * persist is deferred to the storage worker (this hook runs on the
 * SoftDevice event thread, which may not mutate flash).  The
 * sd_power_dcdc_mode_set regulator SVC stays deliberately scoped out. */
static void system_settings_changed(
    void *context, const uint8_t system_settings[R1_SYSTEM_SETTINGS_BYTES]) {
    (void)context;
    if (system_settings[4] != R1_SYSTEM_SETTINGS_SWITCH_TYPE_REG1) {
        return;
    }
    const ret_code_t error =
        openr1_databases_persist_reg1(system_settings[5] != 0u);
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
    error = openr1_twim1_arbiter_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
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
    error = openr1_rtc_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_clock_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    /* Binds kv.bin synchronously and starts the storage worker that runs the
     * health TSDB startup and sleep.db bind in the recovered order.  Placed
     * after the clock so the health startup ops can adopt/report time, and
     * after openr1_storage_initialize (above) for the FAL table. */
    error = openr1_databases_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    error = openr1_connection_control_initialize();
    if (error != NRF_SUCCESS) {
        fail(error);
    }
    r1_runtime_set_nv_recovery_handler(
        runtime, nv_recovery_requested, NULL);
    r1_runtime_set_remove_ring_handler(
        runtime, remove_ring_requested, NULL);
    /* Adopt the persisted normalized REG1 flag (kv dev_info byte 24 bit 1)
     * into the runtime system settings so reads reflect the stored state,
     * and route later settings writes to the deferred persist. */
    if (openr1_databases_kv_ready()) {
        runtime->device.system_settings[5] =
            openr1_databases_reg1_enabled() ? 1u : 0u;
    }
    r1_runtime_set_settings_handler(runtime, system_settings_changed, NULL);
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
