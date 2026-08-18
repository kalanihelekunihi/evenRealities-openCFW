#ifndef OPENR1_R1_RUNTIME_H
#define OPENR1_R1_RUNTIME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_dispatch.h"
#include "openr1/r1_battery.h"
#include "openr1/r1_event.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_state.h"

#define R1_RUNTIME_LINK_MAX 3u
#define R1_INVALID_CONNECTION UINT16_C(0xffff)
#define R1_RUNTIME_WAIT_FOREVER UINT32_MAX
#define R1_BLE_THREAD_MESSAGE_HEADER_BYTES 12u
#define R1_GLASSES_SLOW_DELAY_TICKS UINT32_C(0x96000)
#define R1_GLASSES_DCDC_DELAY_TICKS UINT32_C(0x7800)
#define R1_PERIPHERAL_WATCHDOG_DELAY_TICKS UINT32_C(0x2800)
#define R1_PERIPHERAL_WATCHDOG_LOG_PERIOD 60u
#define R1_ADVERTISING_MODE_DIRECTED_OR_FAST 3u
#define R1_BAE8_CCCD_NOTIFICATION_BIT UINT16_C(0x0001)
#define R1_BAE8_CONNECTION_EVENT_TYPE 0u
#define R1_BAE8_CONNECTION_EVENT_RECORD_BYTES 24u
#define R1_GAP_EVT_CONNECTED UINT16_C(0x0010)
#define R1_GAP_EVT_DISCONNECTED UINT16_C(0x0011)
#define R1_GAP_EVT_PHY_UPDATE_REQUEST UINT16_C(0x0021)
#define R1_GAP_EVT_PHY_UPDATE UINT16_C(0x0022)
#define R1_GATTC_EVT_TIMEOUT UINT16_C(0x003b)
#define R1_GATTS_EVT_TIMEOUT UINT16_C(0x0056)
#define R1_GAP_CONNECTION_TIMEOUT_TICKS UINT32_C(0x0000f000)
#define R1_GAP_FACTORY_ROLE_DELAY_TICKS UINT32_C(0x00007800)
#define R1_GAP_ADVERTISING_RETRY_TICKS UINT32_C(0x00000066)
#define R1_NFC_CHARGE_EVENT_CHARGED_NOTIFICATION UINT32_C(0x00000001)
#define R1_NFC_CHARGE_EVENT_STANDARD_COMMAND_IRQ UINT32_C(0x00000002)
#define R1_NFC_CHARGE_EVENT_CHARGED_NOTIFICATION_CLEAR UINT32_C(0x00000004)
#define R1_NFC_CHARGE_EVENT_PMIC_CHARGE UINT32_C(0x00000008)
#define R1_NFC_CHARGE_EVENT_NOT_CHARGING UINT32_C(0x00000010)
#define R1_NFC_CHARGE_EVENT_BATTERY_UPDATE UINT32_C(0x00000020)
#define R1_NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATE UINT32_C(0x00000040)
#define R1_NFC_CHARGE_EVENT_MESSAGE_PENDING UINT32_C(0x00400000)
#define R1_NFC_CHARGE_EVENT_TERMINATE UINT32_C(0x00800000)
#define R1_NFC_CHARGE_MESSAGE_BYTES 44u
#define R1_NFC_CHARGE_TEMPERATURE_ATTEMPTS 3u
#define R1_NFC_CHARGE_ST25_DYNAMIC_REGISTER UINT16_C(0x100b)
#define R1_NFC_CHARGE_STANDARD_DELAY_TICKS UINT32_C(0x00000800)
#define R1_NFC_CHARGE_NOT_CHARGING_DELAY_TICKS UINT32_C(0x00001000)
#define R1_NFC_CHARGE_TEMPERATURE_RETRY_TICKS UINT32_C(100)
#define R1_NFC_CHARGE_ZERO_BATTERY_UPDATE_COUNT 8u
#define R1_NFC_CHARGE_ZERO_BATTERY_UPDATE_TICKS UINT32_C(10)

typedef enum {
    R1_TX_SENT = 0,
    R1_TX_RESOURCES,
    R1_TX_DROP
} r1_tx_status;

typedef enum {
    R1_BAE8_EVENT_IGNORE = 0,
    R1_BAE8_EVENT_BC_RX,
    R1_BAE8_EVENT_EUS_RX,
    R1_BAE8_EVENT_LINK_GROUP_A,
    R1_BAE8_EVENT_LINK_GROUP_B
} r1_bae8_event_route;

typedef struct {
    r1_bae8_event_route route;
    bool assign_glasses_role;
    bool requires_link_context;
} r1_bae8_event_plan;

/* Pure plan for the custom-service BLE_GAP_EVT_CONNECTED handler. Provider
 * calls, live link-context writes, logging, and callback dispatch stay in the
 * platform binding. */
typedef struct {
    bool log_link_context_lookup_failure;
    bool request_channel1_cccd_read;
    bool request_channel2_cccd_read;
    bool mark_channel1_notifications_enabled;
    bool mark_channel2_notifications_enabled;
    bool dispatch_connection_event;
    uint8_t callback_event_type;
    size_t callback_event_record_bytes;
} r1_bae8_connection_event_plan;

typedef enum {
    R1_GAP_EVENT_IGNORE = 0,
    R1_GAP_EVENT_CONNECTED,
    R1_GAP_EVENT_DISCONNECTED,
    R1_GAP_EVENT_PHY_UPDATE_REQUEST,
    R1_GAP_EVENT_PHY_UPDATE_COMPLETE,
    R1_GAP_EVENT_GATTC_TIMEOUT,
    R1_GAP_EVENT_GATTS_TIMEOUT
} r1_gap_event_route;

typedef enum {
    R1_GAP_DISCONNECTED_UNASSIGNED = 0,
    R1_GAP_DISCONNECTED_PHONE = 1,
    R1_GAP_DISCONNECTED_GLASSES = 2
} r1_gap_disconnected_role;

typedef enum {
    R1_GAP_PHY_RESULT_NONE = 0,
    R1_GAP_PHY_RESULT_CODED,
    R1_GAP_PHY_RESULT_NON_CODED,
    R1_GAP_PHY_RESULT_FAILED
} r1_gap_phy_result;

/* Provider observations used by the pure GAP event planner. event_byte8..10
 * retain the stock BLE-event byte layout: request RX/TX for event 0x21,
 * status/TX/RX for event 0x22, and disconnect reason for event 0x11. */
typedef struct {
    uint16_t event_id;
    uint16_t connection;
    uint8_t event_byte8;
    uint8_t event_byte9;
    uint8_t event_byte10;
    uint16_t phone_connection;
    uint16_t glasses_connection;
    uint8_t factory_marker;
    bool free_link_slot_available;
    bool link_context_initialization_succeeded;
    bool advertising_tx_power_configured;
    uint32_t advertising_tx_power_status;
    uint32_t advertising_start_status;
} r1_gap_event_observation;

typedef struct {
    r1_gap_event_route route;
    bool cancel_connection_timeout;
    bool schedule_connection_timeout;
    uint32_t connection_timeout_ticks;
    bool cache_peer_record;
    bool cancel_role_timers;
    bool schedule_factory_role_timer_a;
    bool schedule_factory_role_timer_b;
    bool request_no_phone_advertising_policy;
    uint32_t factory_role_delay_ticks;
    bool store_latest_connection;
    bool register_link_context;
    bool enter_fail_stop_on_link_context_error;
    bool clear_connection_latch;
    bool release_link_context;
    bool clear_peer_record;
    bool query_peripheral_link_count;
    r1_gap_disconnected_role disconnected_role;
    uint8_t disconnect_reason;
    bool publish_disconnect_status;
    bool reset_glasses_transport;
    bool apply_phone_disconnect_policy;
    bool clear_phone_connection;
    bool clear_glasses_connection;
    bool inspect_advertising_tx_power;
    bool enter_fail_stop_on_tx_power_error;
    bool start_advertising;
    uint8_t advertising_mode;
    bool schedule_advertising_retry;
    uint32_t advertising_retry_ticks;
    bool clear_latest_connection;
    bool request_phy_update;
    bool use_glasses_local_phy_preference;
    uint8_t transmit_phy;
    uint8_t receive_phy;
    r1_gap_phy_result phy_result;
    bool log_gatt_timeout;
} r1_gap_event_plan;

/* Pure observation/intent form of the stock NFC charge-task flag handler.
 * The three temperature-ID pairs are provider observations in attempt order;
 * no ST25, touch, battery, RTOS, watchdog, or task operation is performed. */
typedef struct {
    uint32_t event_flags;
    uint8_t battery_percent;
    uint8_t temperature_ids[R1_NFC_CHARGE_TEMPERATURE_ATTEMPTS][2];
} r1_nfc_charge_task_observation;

typedef struct {
    bool wait_for_message;
    size_t message_bytes;
    bool set_charged_notification;
    bool clear_charged_notification;
    bool open_touch;
    bool close_touch;
    bool run_standard_command_irq_sequence;
    bool run_not_charging_sequence;
    bool clear_nfc_field_seen;
    bool reset_battery_charge_latches;
    uint16_t st25_dynamic_register;
    uint8_t standard_command_register_value;
    uint8_t not_charging_register_value;
    uint32_t standard_command_delay_ticks;
    uint32_t not_charging_delay_ticks;
    uint8_t temperature_id_read_count;
    uint8_t temperature_retry_delay_count;
    uint32_t temperature_retry_delay_ticks;
    bool temperature_ids_valid;
    uint8_t temperature_successful_attempt;
    bool enable_watchdog_reset;
    bool dispatch_pmic_charge_event;
    uint8_t pmic_charge_event;
    bool report_charging_battery_percent;
    uint8_t charging_zero_battery_update_calls;
    uint32_t charging_zero_battery_update_delay_ticks;
    uint8_t periodic_battery_update_calls;
    bool terminate_task;
    bool release_task_synchronization;
    bool deregister_watchdog;
    uint32_t terminal_delay_ticks;
} r1_nfc_charge_task_plan;

typedef enum {
    R1_BUTTONLESS_DFU_PREPARE = 0,
    R1_BUTTONLESS_DFU_ENTER = 1,
    R1_BUTTONLESS_DFU_ENTER_FAILED = 2,
    R1_BUTTONLESS_DFU_RESPONSE_SEND_ERROR = 3,
    R1_BUTTONLESS_DFU_UNKNOWN
} r1_buttonless_dfu_diagnostic;

typedef struct {
    r1_buttonless_dfu_diagnostic diagnostic;
    bool disable_advertising_on_disconnect;
    bool disconnect_all_connected_links;
    bool report_disconnected_link_count;
} r1_buttonless_dfu_event_plan;

typedef struct {
    bool release_credit;
    bool retry_once;
    uint32_t retry_delay_ticks;
} r1_bae8_hvx_retry_plan;

typedef struct {
    bool wear_changed;
    bool secondary_mode_changed;
    bool cancel_slow_event;
    bool schedule_slow_event;
    bool cancel_dcdc_event;
    bool schedule_dcdc_enable;
    bool disable_dcdc_now;
    bool open_touch;
    bool set_ble_slow_mode;
    bool set_touch_fast_mode;
    uint32_t slow_delay_ticks;
    uint32_t dcdc_delay_ticks;
    size_t response_length;
} r1_glasses_status_plan;

typedef struct {
    uint8_t next_counter;
    bool report_link_count;
    bool connection_invariant_violation;
    bool cancel_pending_restart;
    bool start_advertising;
    bool report_advertising_start_failure;
    bool schedule_next_check;
    uint8_t advertising_mode;
    uint32_t next_delay_ticks;
} r1_peripheral_watchdog_plan;

typedef r1_tx_status (*r1_runtime_transmit_fn)(void *context,
                                               const r1_tx_event *event);
typedef r1_error (*r1_runtime_enqueue_fn)(void *context, bool shared_queue,
                                         const r1_tx_event *event,
                                         uint32_t wait_ticks);
typedef bool (*r1_runtime_queue_idle_fn)(void *context, bool shared_queue);
typedef bool (*r1_runtime_lock_fn)(void *context);
typedef void (*r1_runtime_unlock_fn)(void *context);
typedef r1_error (*r1_runtime_role_fn)(void *context, uint16_t connection,
                                      r1_peer_role role);
typedef void (*r1_runtime_touch_fn)(void *context, bool enabled);
/* Invoked after a dispatch that changed the 12-byte system-settings record;
 * the platform owns any persistence or hardware effect. */
typedef void (*r1_runtime_settings_fn)(
    void *context, const uint8_t system_settings[R1_SYSTEM_SETTINGS_BYTES]);
/* Invoked only after an accepted health-settings write has had its protocol
 * acknowledgement queued. The plan preserves the recovered distinction
 * between raw private-event transitions and normalized durable changes. */
typedef void (*r1_runtime_health_settings_fn)(
    void *context, const r1_health_settings_command_plan *plan);

/* Called after a complete authenticated wire model is decoded and before
 * dispatch snapshots protocol-visible state. Platform services may refresh
 * already-admitted live inputs (for example battery/charge state); they may
 * not rewrite the request. */
typedef void (*r1_runtime_request_observer_fn)(
    void *context, const r1_model *request);

typedef struct {
    bool active;
    uint16_t connection;
    r1_reassembler reassembler;
    r1_session session;
} r1_runtime_link;

typedef struct r1_runtime {
    r1_device_state device;
    r1_battery_controller battery;
    r1_event_plane events;
    r1_runtime_link links[R1_RUNTIME_LINK_MAX];
    r1_dispatch_result dispatch_scratch;
    r1_fragment_set fragment_scratch;
    r1_runtime_transmit_fn transmit;
    void *transmit_context;
    r1_runtime_enqueue_fn enqueue;
    void *enqueue_context;
    r1_runtime_queue_idle_fn queue_idle;
    void *queue_idle_context;
    r1_runtime_lock_fn lock;
    r1_runtime_unlock_fn unlock;
    void *lock_context;
    r1_runtime_role_fn role_handler;
    void *role_context;
    r1_runtime_touch_fn touch_handler;
    void *touch_context;
    r1_runtime_settings_fn settings_handler;
    void *settings_context;
    r1_runtime_health_settings_fn health_settings_handler;
    void *health_settings_context;
    r1_runtime_request_observer_fn request_observer;
    void *request_observer_context;
    /* The recovered automatic publisher calls five legs synchronously, but
     * the BLE worker owns an exact 50-record queue.  Keep the observed order
     * as a bitset and compose one leg only when that queue has drained. */
    uint8_t automatic_health_pending_mask;
    uint8_t automatic_health_next_leg;
    uint32_t automatic_health_batch_timestamp;
    uint32_t automatic_health_legs_scheduled;
    uint32_t automatic_health_legs_enqueued;
    uint32_t automatic_health_leg_failures;
} r1_runtime;

void r1_runtime_initialize(r1_runtime *runtime,
                           r1_runtime_transmit_fn transmit,
                           void *transmit_context);
void r1_runtime_set_transmit(r1_runtime *runtime,
                             r1_runtime_transmit_fn transmit,
                             void *transmit_context);
void r1_runtime_set_enqueue(r1_runtime *runtime,
                            r1_runtime_enqueue_fn enqueue,
                            void *enqueue_context);
void r1_runtime_set_queue_idle(r1_runtime *runtime,
                               r1_runtime_queue_idle_fn queue_idle,
                               void *queue_idle_context);
void r1_runtime_set_lock(r1_runtime *runtime, r1_runtime_lock_fn lock,
                         r1_runtime_unlock_fn unlock, void *lock_context);
void r1_runtime_set_role_handler(r1_runtime *runtime,
                                 r1_runtime_role_fn role_handler,
                                 void *role_context);
void r1_runtime_set_touch_handler(r1_runtime *runtime,
                                  r1_runtime_touch_fn touch_handler,
                                  void *touch_context);
void r1_runtime_set_settings_handler(r1_runtime *runtime,
                                     r1_runtime_settings_fn settings_handler,
                                     void *settings_context);
void r1_runtime_set_health_settings_handler(
    r1_runtime *runtime,
    r1_runtime_health_settings_fn health_settings_handler,
    void *health_settings_context);
void r1_runtime_set_request_observer(
    r1_runtime *runtime, r1_runtime_request_observer_fn observer,
    void *observer_context);
void r1_runtime_configure_battery(r1_runtime *runtime, uint8_t battery_type);
bool r1_runtime_update_battery(
    r1_runtime *runtime, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds);
r1_health_auto_sync_result r1_runtime_run_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context);
/* Live target composition for the retained automatic-sync controller.  The
 * schedule call applies the exact authenticated-phone/three-hour gate and
 * records all five serial-zero legs.  Service emits at most one leg and only
 * when the exact shared BLE queue is empty, so the historical 50-record bound
 * is never bypassed. */
r1_health_auto_sync_result r1_runtime_schedule_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds);
r1_error r1_runtime_service_automatic_health_sync(r1_runtime *runtime);
r1_error r1_runtime_connect(r1_runtime *runtime, uint16_t connection);
void r1_runtime_disconnect(r1_runtime *runtime, uint16_t connection);
r1_error r1_runtime_set_security(r1_runtime *runtime, uint16_t connection,
                                 bool encrypted, bool bonded, bool authorized);
r1_peer_role r1_runtime_connection_role(const r1_runtime *runtime,
                                        uint16_t connection);
void r1_runtime_role_occupancy(const r1_runtime *runtime,
                               bool *phone_occupied, bool *glasses_occupied);
r1_bae8_event_plan r1_runtime_plan_bae8_event(uint8_t event_type);
r1_error r1_bae8_connection_event_plan_build(
    bool link_context_lookup_succeeded, bool callback_installed,
    bool channel1_cccd_read_succeeded, uint16_t channel1_cccd,
    bool channel2_cccd_read_succeeded, uint16_t channel2_cccd,
    r1_bae8_connection_event_plan *plan);
r1_error r1_gap_event_plan_build(
    const r1_gap_event_observation *observation, r1_gap_event_plan *plan);
r1_error r1_nfc_charge_task_plan_build(
    const r1_nfc_charge_task_observation *observation,
    r1_nfc_charge_task_plan *plan);
r1_buttonless_dfu_event_plan r1_runtime_plan_buttonless_dfu_event(
    uint32_t event_type);
r1_error r1_bae8_plan_hvx_result(
    bool serialized_path, bool credit_acquired, r1_tx_status status,
    uint8_t completed_retries, r1_bae8_hvx_retry_plan *plan);
r1_error r1_ble_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes);
r1_error r1_ble_tx_queue_dispatch_type0(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes);
r1_error r1_ble_tx_queue_dispatch_type1(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes);
r1_error r1_ble_tx_queue_dispatch_type2(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes);
r1_error r1_factory_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes);
r1_error r1_peripheral_watchdog_plan_step(
    uint8_t previous_counter, uint32_t peripheral_connection_count,
    bool right_handle_valid, bool left_handle_valid,
    int advertising_stop_result, int advertising_start_result,
    r1_peripheral_watchdog_plan *plan);
r1_error r1_glasses_status_plan_command(
    bool command_valid, uint8_t status_bits, bool previous_worn,
    bool previous_secondary_mode, bool dcdc_policy_enabled,
    r1_glasses_status_plan *plan);
r1_error r1_runtime_receive_eus(r1_runtime *runtime, uint16_t connection,
                                const uint8_t *value, size_t length);
void r1_runtime_hvn_complete(r1_runtime *runtime, uint8_t completed);
uint32_t r1_runtime_poll(r1_runtime *runtime, uint32_t now_tick);

#endif
