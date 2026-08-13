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
typedef r1_error (*r1_runtime_role_fn)(void *context, uint16_t connection,
                                      r1_peer_role role);
typedef void (*r1_runtime_touch_fn)(void *context, bool enabled);

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
    r1_runtime_role_fn role_handler;
    void *role_context;
    r1_runtime_touch_fn touch_handler;
    void *touch_context;
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
void r1_runtime_set_role_handler(r1_runtime *runtime,
                                 r1_runtime_role_fn role_handler,
                                 void *role_context);
void r1_runtime_set_touch_handler(r1_runtime *runtime,
                                  r1_runtime_touch_fn touch_handler,
                                  void *touch_context);
void r1_runtime_configure_battery(r1_runtime *runtime, uint8_t battery_type);
bool r1_runtime_update_battery(
    r1_runtime *runtime, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds);
r1_health_auto_sync_result r1_runtime_run_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context);
r1_error r1_runtime_connect(r1_runtime *runtime, uint16_t connection);
void r1_runtime_disconnect(r1_runtime *runtime, uint16_t connection);
r1_error r1_runtime_set_security(r1_runtime *runtime, uint16_t connection,
                                 bool encrypted, bool bonded, bool authorized);
r1_peer_role r1_runtime_connection_role(const r1_runtime *runtime,
                                        uint16_t connection);
r1_bae8_event_plan r1_runtime_plan_bae8_event(uint8_t event_type);
r1_error r1_bae8_plan_hvx_result(
    bool serialized_path, bool credit_acquired, r1_tx_status status,
    uint8_t completed_retries, r1_bae8_hvx_retry_plan *plan);
r1_error r1_ble_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes);
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
