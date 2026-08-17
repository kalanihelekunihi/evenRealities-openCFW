#ifndef OPENR1_R1_EVENT_H
#define OPENR1_R1_EVENT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_NORMAL_QUEUE_CAPACITY 20u
#define R1_EUS_QUEUE_CAPACITY 50u
#define R1_HVN_CREDIT_MAX 4u
#define R1_TX_ENQUEUE_WAIT_TICKS 100u
#define R1_EUS_CREDIT_WAIT_TICKS 200u
#define R1_EUS_RESOURCE_RETRY_TICKS 1000u
#define R1_CHANNEL1_TASK_QUEUE_RECORD_BYTES 4u
#define R1_CHANNEL1_TASK_SYNC_GROUP 10u
#define R1_CHANNEL1_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_CHANNEL1_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_CHANNEL1_TASK_DISPATCH_FLAG UINT32_C(1u << 0)
#define R1_CHANNEL1_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_BAE8_INPUT_TASK_QUEUE_CAPACITY 50u
#define R1_BAE8_INPUT_TASK_QUEUE_RECORD_BYTES 4u
#define R1_BAE8_INPUT_TASK_SYNC_GROUP 2u
#define R1_BAE8_INPUT_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_BAE8_INPUT_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_BAE8_INPUT_TASK_DISPATCH_FLAG UINT32_C(1u << 22)
#define R1_BAE8_INPUT_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_SHARED_TX_TASK_QUEUE_RECORD_BYTES 4u
#define R1_SHARED_TX_TASK_SYNC_GROUP 3u
#define R1_SHARED_TX_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_SHARED_TX_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_SHARED_TX_TASK_DISPATCH_FLAG UINT32_C(1u << 0)
#define R1_SHARED_TX_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_FACTORY_INPUT_TASK_QUEUE_CAPACITY 8u
#define R1_FACTORY_INPUT_TASK_QUEUE_RECORD_BYTES 4u
#define R1_FACTORY_INPUT_TASK_SYNC_GROUP 6u
#define R1_FACTORY_INPUT_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_FACTORY_INPUT_TASK_DISPATCH_FLAG UINT32_C(1u << 22)
#define R1_FACTORY_INPUT_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_FACTORY_INPUT_TASK_STARTUP_ACTION_COUNT 5u
#define R1_FACTORY_INPUT_THREAD_STACK_BYTES UINT32_C(8192)
#define R1_FACTORY_INPUT_THREAD_PRIORITY_RAW INT32_C(39)
#define R1_FACTORY_INPUT_THREAD_TRUSTZONE_MODULE UINT32_C(1)
#define R1_SENSOR_TASK_QUEUE_CAPACITY 50u
#define R1_SENSOR_TASK_QUEUE_RECORD_BYTES 16u
#define R1_SENSOR_TASK_SYNC_GROUP 5u
#define R1_SENSOR_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_SENSOR_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_SENSOR_TASK_MOTION_INTERRUPT_FLAG UINT32_C(1u << 1)
#define R1_SENSOR_TASK_DISPATCH_FLAG UINT32_C(1u << 22)
#define R1_SENSOR_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_SENSOR_TASK_STARTUP_ACTION_COUNT 5u
#define R1_SENSOR_TASK_STARTUP_EVENT_ID UINT32_C(5)
#define R1_SYSTEM_TASK_QUEUE_CAPACITY 50u
#define R1_SYSTEM_TASK_QUEUE_RECORD_BYTES 44u
#define R1_SYSTEM_TASK_SYNC_GROUP 1u
#define R1_SYSTEM_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_SYSTEM_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_SYSTEM_TASK_WORKSPACE_CLEAR_BYTES UINT32_C(30720)
#define R1_SYSTEM_TASK_STARTUP_ACTION_COUNT 3u
#define R1_BLE_TASK_QUEUE_CAPACITY 8u
#define R1_BLE_TASK_QUEUE_RECORD_BYTES 4u
#define R1_BLE_TASK_SYNC_GROUP 4u
#define R1_BLE_TASK_WATCHDOG_TICKS UINT32_C(10000)
#define R1_BLE_TASK_WAIT_FLAGS UINT32_C(0x00ffffff)
#define R1_BLE_TASK_ROLE_SYNC_DELAY_TICKS UINT32_C(3072)
#define R1_BLE_TASK_SLOW_POLICY_DELAY_TICKS UINT32_C(10240)
#define R1_BLE_TASK_CONNECTION_CONTROL_FLAG UINT32_C(1u << 22)
#define R1_BLE_TASK_ADVERTISING_STOP_FLAG UINT32_C(1u << 7)
#define R1_BLE_TASK_ADVERTISING_RESTART_3_FLAG UINT32_C(1u << 8)
#define R1_BLE_TASK_ADVERTISING_RESTART_4_FLAG UINT32_C(1u << 10)
#define R1_BLE_TASK_PERIPHERAL_WATCHDOG_FLAG UINT32_C(1u << 13)
#define R1_BLE_TASK_DFU_PREPARE_FLAG UINT32_C(1u << 2)
#define R1_BLE_TASK_TX_POWER_LOW_FLAG UINT32_C(1u << 11)
#define R1_BLE_TASK_TX_POWER_HIGH_FLAG UINT32_C(1u << 12)
#define R1_BLE_TASK_SUSPEND_FLAG UINT32_C(1u << 23)
#define R1_BLE_TASK_STARTUP_ACTION_COUNT 2u
#define R1_DELAYED_EVENT_CAPACITY 64u
#define R1_DELAYED_EVENT_ELAPSED_TAG UINT32_C(0xff000000)
#define R1_DELAYED_EVENT_ELAPSED_MASK UINT32_C(0x00ffffff)
#define R1_TASK_SUSPEND_TARGET_COUNT 9u
#define R1_TASK_SUSPEND_THREAD_FLAG UINT32_C(0x00800000)
#define R1_TASK_SUSPEND_BARRIER_WAIT_TICKS UINT32_C(0x00005000)
#define R1_TASK_TOPOLOGY_TARGET_COUNT 9u
#define R1_TASK_TOPOLOGY_FACTORY_MARKER UINT8_C(0x55)
#define R1_TASK_TOPOLOGY_INITIAL_PRIORITY UINT8_C(8)
#define R1_TASK_TOPOLOGY_FINAL_PRIORITY UINT8_C(0x35)

typedef struct {
    uint16_t connection;
    uint8_t channel;
    uint8_t bytes[R1_BLE_VALUE_MAX];
    size_t length;
    uint8_t resource_retries;
    bool credit_wait_started;
    bool resource_retry_pending;
    uint32_t deadline_tick;
} r1_tx_event;

typedef struct {
    r1_tx_event entries[R1_EUS_QUEUE_CAPACITY];
    size_t head;
    size_t count;
    size_t capacity;
} r1_event_queue;

typedef struct {
    r1_event_queue normal;
    r1_event_queue eus;
    uint8_t hvn_credits;
} r1_event_plane;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    const char *registry_name;
    uint32_t watchdog_ticks;
} r1_channel1_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool drain_queue;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_channel1_task_flag_plan;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    const char *registry_name;
    uint32_t watchdog_ticks;
} r1_bae8_input_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool drain_queue;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_bae8_input_task_flag_plan;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    const char *registry_name;
    uint32_t watchdog_ticks;
} r1_shared_tx_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool drain_queue;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_shared_tx_task_flag_plan;

typedef enum {
    R1_FACTORY_INPUT_WEAR_BUFFER_FILL = 0,
    R1_FACTORY_INPUT_SENSOR_STREAM_INITIALIZE,
    R1_FACTORY_INPUT_ACCELEROMETER_STREAM_CREATE,
    R1_FACTORY_INPUT_STREAM_NAMESPACE_REGISTER,
    R1_FACTORY_INPUT_TEMPERATURE_STREAM_CREATE
} r1_factory_input_task_startup_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    r1_factory_input_task_startup_action
        actions[R1_FACTORY_INPUT_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
} r1_factory_input_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool drain_queue;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool run_periodic_operation;
    bool wait_again;
} r1_factory_input_task_flag_plan;

typedef struct {
    const char *name;
    uint32_t stack_bytes;
    int32_t priority_raw;
    uint32_t trustzone_module;
    bool request_thread_create;
    bool store_returned_handle;
    bool null_handle_enters_fail_stop;
} r1_factory_input_thread_creation_plan;

typedef enum {
    R1_FACTORY_INPUT_RECORD_STANDARD = 0,
    R1_FACTORY_INPUT_RECORD_AT_COMMAND
} r1_factory_input_record_route;

typedef struct {
    r1_factory_input_record_route route;
    uint16_t message_type;
    uint16_t dispatch_length;
    size_t observed_length;
    bool append_terminator;
    size_t terminator_index;
    bool release_record;
} r1_factory_input_record_plan;

typedef enum {
    R1_FACTORY_F2_DELAYED_RESET = 0,
    R1_FACTORY_F2_PPG_STOP,
    R1_FACTORY_F2_PPG_PROFILE_4000,
    R1_FACTORY_F2_PPG_PROFILE_2000,
    R1_FACTORY_F2_SHIP_MODE_MARKED,
    R1_FACTORY_F2_SHIP_MODE
} r1_factory_f2_action;

/* Pure plan for the four high-risk factory command-0xF2 handlers. */
typedef struct {
    r1_factory_f2_action action;
    bool response_requested;
    uint8_t response_length;
    uint16_t delay_before_action_ms;
    uint16_t delay_after_action_ms;
    bool reset_reason_write_requested;
    uint8_t reset_reason;
    bool system_reset_requested;
    bool device_marker_write_requested;
    uint8_t device_marker;
    bool ship_mode_sequence_requested;
} r1_factory_f2_action_plan;

typedef enum {
    R1_SENSOR_TASK_STREAM_INITIALIZE = 0,
    R1_SENSOR_TASK_ACCELEROMETER_STREAM_CREATE,
    R1_SENSOR_TASK_STREAM_NAMESPACE_REGISTER,
    R1_SENSOR_TASK_TEMPERATURE_STREAM_CREATE,
    R1_SENSOR_TASK_HEALTH_SERVICES_INITIALIZE
} r1_sensor_task_startup_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    r1_sensor_task_startup_action
        actions[R1_SENSOR_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
    const char *registry_name;
    uint32_t watchdog_ticks;
    bool publish_startup_event;
    uint32_t startup_event_id;
    size_t startup_event_payload_bytes;
    bool use_sensor_stream_timeout;
} r1_sensor_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool drain_event_records;
    bool dispatch_motion_interrupt;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool wait_again;
} r1_sensor_task_flag_plan;

typedef enum {
    R1_SYSTEM_TASK_PRODUCT_SERVICES_INITIALIZE = 0,
    R1_SYSTEM_TASK_WORKSPACE_CLEAR,
    R1_SYSTEM_TASK_NFC_LATE_INITIALIZE
} r1_system_task_startup_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    r1_system_task_startup_action
        actions[R1_SYSTEM_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
    uint32_t workspace_clear_bytes;
    const char *registry_name;
    uint32_t watchdog_ticks;
} r1_system_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool dispatch_system_flags;
    bool feed_watchdog;
    bool wait_again;
} r1_system_task_flag_plan;

typedef enum {
    R1_BLE_TASK_PEER_RECORD_COMMIT = 0,
    R1_BLE_TASK_NORDIC_BOOTSTRAP_CONFIGURE
} r1_ble_task_startup_action;

typedef enum {
    R1_BLE_TASK_ADVERTISING_NONE = 0,
    R1_BLE_TASK_ADVERTISING_STOP,
    R1_BLE_TASK_ADVERTISING_RESTART_MODE_3,
    R1_BLE_TASK_ADVERTISING_RESTART_MODE_4
} r1_ble_task_advertising_action;

typedef struct {
    bool queue_create_failed;
    bool enter_fail_stop;
    uint32_t queue_capacity;
    uint32_t queue_record_bytes;
    uint8_t sync_group;
    r1_ble_task_startup_action actions[R1_BLE_TASK_STARTUP_ACTION_COUNT];
    size_t action_count;
    uint32_t role_sync_delay_ticks;
    uint32_t slow_policy_delay_ticks;
    const char *registry_name;
    uint32_t watchdog_ticks;
} r1_ble_task_startup_plan;

typedef struct {
    uint32_t observed_flags;
    bool provider_wait_error;
    bool poll_softdevice_before;
    bool dispatch_connection_control;
    r1_ble_task_advertising_action advertising_action;
    bool run_peripheral_watchdog;
    bool prepare_buttonless_dfu;
    bool request_low_tx_power;
    bool request_high_tx_power;
    bool poll_softdevice_after;
    bool feed_before_suspend;
    bool signal_suspend;
    bool enter_suspend_wait;
    bool feed_watchdog;
    bool wait_again;
} r1_ble_task_flag_plan;

typedef enum {
    R1_ADVERTISING_EVENT_LOG_NONE = 0,
    R1_ADVERTISING_EVENT_LOG_FAST,
    R1_ADVERTISING_EVENT_LOG_SLOW
} r1_advertising_event_log;

typedef struct {
    bool publish_status;
    bool advertising_active;
    uint8_t advertising_mode;
    r1_advertising_event_log log;
} r1_advertising_event_plan;

typedef struct {
    uint8_t sync_group;
    uint32_t acknowledgment_flag;
} r1_task_suspend_target;

typedef struct {
    r1_task_suspend_target targets[R1_TASK_SUSPEND_TARGET_COUNT];
    size_t target_count;
    uint32_t thread_flag;
    uint32_t acknowledgment_mask;
} r1_task_suspend_broadcast_plan;

typedef struct {
    r1_task_suspend_target targets[R1_TASK_SUSPEND_TARGET_COUNT];
    size_t target_count;
    uint32_t thread_flag;
    uint32_t per_target_wait_ticks;
} r1_task_suspend_barrier_plan;

/* Provider-neutral startup order for the nine task creators selected by the
 * stock thread manager. CMSIS handles and scatter-loaded creator pointers are
 * deliberately absent. */
typedef struct {
    bool initialize_firmware_event_loop;
    bool initialize_watchdog_registry;
    uint8_t sync_groups[R1_TASK_TOPOLOGY_TARGET_COUNT];
    size_t target_count;
    uint8_t initial_thread_priority;
    uint8_t final_thread_priority;
    bool factory_group_selected;
} r1_task_topology_startup_plan;

typedef struct {
    uint32_t event;
    uint32_t context;
    uint32_t remaining_milliseconds;
} r1_delayed_event_slot;

typedef struct {
    r1_delayed_event_slot slots[R1_DELAYED_EVENT_CAPACITY];
    uint32_t last_timer_delay_milliseconds;
    uint32_t last_timer_start_milliseconds;
} r1_delayed_event_state;

typedef struct {
    uint32_t event;
    uint32_t context;
} r1_delayed_event_due;

typedef struct {
    r1_delayed_event_due due[R1_DELAYED_EVENT_CAPACITY];
    size_t due_count;
    uint32_t elapsed_milliseconds;
    uint32_t next_delay_milliseconds;
    bool elapsed_override_used;
    bool timer_start_requested;
    bool stock_empty_reload_quirk;
    bool stock_int32_max_suppression_quirk;
} r1_delayed_event_step_result;

typedef enum {
    R1_DELAYED_EVENT_IMMEDIATE = 0,
    R1_DELAYED_EVENT_SCHEDULED,
    R1_DELAYED_EVENT_TABLE_FULL
} r1_delayed_event_schedule_action;

typedef struct {
    r1_delayed_event_schedule_action action;
    size_t slot_index;
    uint32_t elapsed_milliseconds;
    bool immediate_push_requested;
    bool worker_wakeup_requested;
    r1_delayed_event_step_result timer_step;
} r1_delayed_event_schedule_result;

typedef struct {
    size_t removed_count;
    uint32_t elapsed_milliseconds;
    bool worker_wakeup_requested;
    r1_delayed_event_step_result timer_step;
} r1_delayed_event_cancel_result;

void r1_event_plane_initialize(r1_event_plane *plane);
r1_error r1_event_enqueue(r1_event_plane *plane, bool eus, const r1_tx_event *event);
bool r1_event_take(r1_event_plane *plane, bool eus, r1_tx_event *event);
bool r1_event_peek(const r1_event_plane *plane, bool eus, r1_tx_event *event);
r1_tx_event *r1_event_front(r1_event_plane *plane, bool eus);
bool r1_event_drop(r1_event_plane *plane, bool eus);
void r1_event_remove_connection(r1_event_plane *plane, uint16_t connection);
bool r1_event_consume_credit(r1_event_plane *plane);
void r1_event_complete(r1_event_plane *plane, uint8_t completed);
void r1_event_disconnect(r1_event_plane *plane);
r1_error r1_channel1_task_plan_startup(
    bool queue_created, r1_channel1_task_startup_plan *plan);
r1_error r1_channel1_task_plan_flags(
    uint32_t flags, r1_channel1_task_flag_plan *plan);
r1_error r1_bae8_input_task_plan_startup(
    bool queue_created, r1_bae8_input_task_startup_plan *plan);
r1_error r1_bae8_input_task_plan_flags(
    uint32_t flags, r1_bae8_input_task_flag_plan *plan);
r1_error r1_shared_tx_task_plan_startup(
    bool queue_created, r1_shared_tx_task_startup_plan *plan);
r1_error r1_shared_tx_task_plan_flags(
    uint32_t flags, r1_shared_tx_task_flag_plan *plan);
r1_error r1_factory_input_task_plan_startup(
    bool queue_created, r1_factory_input_task_startup_plan *plan);
r1_error r1_factory_input_task_plan_flags(
    uint32_t flags, r1_factory_input_task_flag_plan *plan);
r1_error r1_factory_input_thread_creation_plan_build(
    r1_factory_input_thread_creation_plan *plan);
r1_error r1_factory_input_record_plan_dispatch(
    uint16_t message_type, const uint8_t *payload, size_t payload_length,
    size_t payload_capacity, r1_factory_input_record_plan *plan);
r1_error r1_factory_f2_delayed_reset_plan(
    r1_factory_f2_action_plan *plan);
r1_error r1_factory_f2_ppg_mode_plan(
    const uint8_t *payload, size_t payload_length,
    r1_factory_f2_action_plan *plan);
r1_error r1_factory_f2_marked_ship_mode_plan(
    r1_factory_f2_action_plan *plan);
r1_error r1_factory_f2_ship_mode_plan(
    r1_factory_f2_action_plan *plan);
r1_error r1_sensor_task_plan_startup(
    bool queue_created, r1_sensor_task_startup_plan *plan);
r1_error r1_sensor_task_plan_flags(
    uint32_t flags, r1_sensor_task_flag_plan *plan);
r1_error r1_system_task_plan_startup(
    bool queue_created, r1_system_task_startup_plan *plan);
r1_error r1_system_task_plan_flags(
    uint32_t flags, r1_system_task_flag_plan *plan);
r1_error r1_ble_task_plan_startup(
    bool queue_created, r1_ble_task_startup_plan *plan);
r1_error r1_ble_task_plan_flags(
    uint32_t flags, r1_ble_task_flag_plan *plan);
r1_error r1_advertising_event_plan_build(
    uint32_t provider_event, r1_advertising_event_plan *plan);
r1_error r1_task_suspend_broadcast_plan_build(
    uint8_t configuration_byte, r1_task_suspend_broadcast_plan *plan);
r1_error r1_task_suspend_barrier_plan_build(
    uint8_t configuration_byte, r1_task_suspend_barrier_plan *plan);
r1_error r1_task_topology_startup_plan_build(
    uint8_t configuration_byte, r1_task_topology_startup_plan *plan);
r1_error r1_delayed_event_timer_step(
    r1_delayed_event_state *state, uint32_t callback_argument,
    uint32_t kernel_tick, r1_delayed_event_step_result *result);
r1_error r1_delayed_event_schedule(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t delay_milliseconds, uint32_t kernel_tick,
    r1_delayed_event_schedule_result *result);
r1_error r1_delayed_event_cancel(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t kernel_tick, r1_delayed_event_cancel_result *result);

#endif
