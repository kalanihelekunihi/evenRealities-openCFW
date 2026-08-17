#ifndef OPENR1_R1_ST25DVXXKC_H
#define OPENR1_R1_ST25DVXXKC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * R1 product policy around ST's attributable ST25DVxxKC component driver.
 *
 * Register access, device identification, password framing, dynamic-register
 * decoding, and mailbox transport remain in the pinned ST provider.  This
 * adapter contains only recovered R1 orchestration and memory-safety policy.
 */
#define R1_ST25DVXXKC_INITIALIZE_RETRIES 10u
#define R1_ST25DVXXKC_GPO_RETRIES 10u
#define R1_ST25DVXXKC_SETTLE_TICKS UINT32_C(5)
#define R1_ST25DVXXKC_GPO1_CONFIGURATION UINT8_C(0x21)
#define R1_ST25DVXXKC_GPO2_CLEAR_MASK UINT8_C(0x03)
#define R1_ST25DVXXKC_ICREF_04KC UINT8_C(0x50)
#define R1_ST25DVXXKC_ICREF_64KC UINT8_C(0x51)
#define R1_ST25DVXXKC_MAILBOX_CAPACITY 20u
#define R1_ST25DVXXKC_DOCK_CONTROL_PACKET_SIZE 23u
#define R1_ST25DVXXKC_DOCK_VERSION_SIZE 11u
#define R1_ST25DVXXKC_DOCK_HEADER_SIZE 9u
#define R1_ST25DVXXKC_DOCK_MAILBOX_READY UINT8_C(0x81)
#define R1_ST25DVXXKC_DOCK_ADVERTISED UINT8_C(0xaa)
#define R1_ST25DVXXKC_DOCK_HEARTBEAT_LIMIT UINT8_C(60)
#define R1_ST25DVXXKC_DOCK_DELAY_THRESHOLD UINT8_C(44)
#define R1_ST25DVXXKC_DOCK_DELAY_SHORT UINT8_C(4)
#define R1_ST25DVXXKC_DOCK_DELAY_LONG UINT8_C(60)
#define R1_ST25DVXXKC_CHARGE_FIELD_DELAY_TICKS UINT32_C(0x800)
#define R1_ST25DVXXKC_BUS_READY_DELAY_TICKS UINT32_C(10)

/* Recovered values deliberately fail password authentication to close SSO. */
#define R1_ST25DVXXKC_SESSION_CLOSE_MSB UINT32_C(0x12345678)
#define R1_ST25DVXXKC_SESSION_CLOSE_LSB UINT32_C(0x13245678)

typedef enum {
    R1_ST25DVXXKC_MESSAGE_NONE = 0,
    R1_ST25DVXXKC_MESSAGE_HOST = 1,
    R1_ST25DVXXKC_MESSAGE_RF = 2
} r1_st25dvxxkc_message_owner;

typedef struct {
    bool mailbox_enabled;
    bool host_put_message;
    bool rf_put_message;
    bool host_missed_message;
    bool rf_missed_message;
    r1_st25dvxxkc_message_owner current_message;
} r1_st25dvxxkc_mailbox_status;

typedef struct {
    int32_t (*initialize)(void *context);
    void (*deinitialize)(void *context);
    int32_t (*read_id)(void *context, uint8_t *ic_reference);
    int32_t (*read_security_session)(void *context, bool *open);
    int32_t (*present_password)(void *context, uint32_t most_significant,
                                uint32_t least_significant);
    int32_t (*read_mailbox_mode)(void *context, bool *enabled);
    int32_t (*read_mailbox_status)(void *context,
                                   r1_st25dvxxkc_mailbox_status *status);
    int32_t (*set_mailbox_enabled)(void *context);
    int32_t (*reset_energy_harvesting)(void *context);
    int32_t (*set_gpo1)(void *context, uint8_t configuration);
    int32_t (*read_gpo2)(void *context, uint8_t *configuration);
    int32_t (*set_gpo2)(void *context, uint8_t configuration);
    int32_t (*read_mailbox_length)(void *context, uint8_t *encoded_length);
    int32_t (*read_mailbox)(void *context, uint16_t offset, uint8_t *bytes,
                            size_t length);
    void (*delay)(void *context, uint32_t ticks);
} r1_st25dvxxkc_provider_ops;

/* Transparent form of the six callbacks installed in the stock
 * ST25DVxxKC_IO_t at 0x00044C34. The generic device-registry transport and
 * board resource lease remain explicit caller-supplied providers. */
typedef struct {
    void (*acquire)(void *context);
    void (*release)(void *context);
    void (*delay)(void *context, uint32_t ticks);
    uint32_t (*tick_get)(void *context);
    int32_t (*read)(void *context, uint8_t device_address, uint16_t register_address,
                    uint8_t *bytes, uint16_t length);
    int32_t (*write)(void *context, uint8_t device_address, uint16_t register_address,
                     const uint8_t *bytes, uint16_t length);
} r1_st25dvxxkc_bus_io_ops;

typedef void (*r1_st25dvxxkc_frame_callback)(void *context,
                                             const uint8_t *bytes,
                                             size_t length);

typedef struct {
    const r1_st25dvxxkc_provider_ops *provider;
    void *provider_context;
    r1_st25dvxxkc_frame_callback frame_callback;
    void *frame_context;
    uint8_t mailbox[R1_ST25DVXXKC_MAILBOX_CAPACITY];
    uint8_t ic_reference;
    uint32_t accepted_frames;
    uint32_t rejected_lengths;
    bool initialized;
} r1_st25dvxxkc_adapter;

/*
 * Product state carried by the R1 dock protocol.  The ST provider remains
 * responsible for obtaining mailbox_control and transmitting control_packet.
 */
typedef struct {
    uint8_t adc_reference;
    uint8_t advertisement_marker;
    uint8_t dock_accessory;
    uint8_t heartbeat_count;
    uint8_t cached_field_delay;
    uint8_t charge_temperature;
    uint8_t dock_advertising_enabled;
    uint8_t dock_hardware_revision;
    bool field_seen;
    char dock_version[R1_ST25DVXXKC_DOCK_VERSION_SIZE];
} r1_st25dvxxkc_dock_state;

typedef enum {
    R1_ST25DVXXKC_DOCK_ACTION_NONE = 0,
    R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET,
    R1_ST25DVXXKC_DOCK_ACTION_SCHEDULE_CHARGE_FIELD
} r1_st25dvxxkc_dock_action;

void r1_st25dvxxkc_adapter_initialize(r1_st25dvxxkc_adapter *adapter);
r1_error r1_st25dvxxkc_adapter_bind(
    r1_st25dvxxkc_adapter *adapter,
    const r1_st25dvxxkc_provider_ops *provider, void *provider_context);
void r1_st25dvxxkc_set_frame_callback(r1_st25dvxxkc_adapter *adapter,
                                      r1_st25dvxxkc_frame_callback callback,
                                      void *context);
r1_error r1_st25dvxxkc_activate(r1_st25dvxxkc_adapter *adapter);
void r1_st25dvxxkc_deactivate(r1_st25dvxxkc_adapter *adapter);
r1_error r1_st25dvxxkc_poll(r1_st25dvxxkc_adapter *adapter, bool *received);
bool r1_st25dvxxkc_provider_available(const r1_st25dvxxkc_adapter *adapter);
uint32_t r1_st25dvxxkc_bus_tick_get(const r1_st25dvxxkc_bus_io_ops *ops,
                                    void *context);
int32_t r1_st25dvxxkc_bus_initialize(const r1_st25dvxxkc_bus_io_ops *ops,
                                     void *context);
int32_t r1_st25dvxxkc_bus_deinitialize(const r1_st25dvxxkc_bus_io_ops *ops,
                                       void *context);
int32_t r1_st25dvxxkc_bus_is_ready(const r1_st25dvxxkc_bus_io_ops *ops,
                                   void *context, uint16_t device_address,
                                   uint32_t trials);
int32_t r1_st25dvxxkc_bus_read(const r1_st25dvxxkc_bus_io_ops *ops,
                               void *context, uint16_t device_address,
                               uint16_t register_address, uint8_t *bytes,
                               uint16_t length);
int32_t r1_st25dvxxkc_bus_write(const r1_st25dvxxkc_bus_io_ops *ops,
                                void *context, uint16_t device_address,
                                uint16_t register_address,
                                const uint8_t *bytes, uint16_t length);
bool r1_st25dvxxkc_mailbox_length_allowed(size_t length);
void r1_st25dvxxkc_dock_state_initialize(r1_st25dvxxkc_dock_state *state);
void r1_st25dvxxkc_dock_hardware_clear(r1_st25dvxxkc_dock_state *state);
uint8_t r1_st25dvxxkc_dock_hardware_get(
    const r1_st25dvxxkc_dock_state *state);
void r1_st25dvxxkc_dock_version_clear(r1_st25dvxxkc_dock_state *state);
const char *r1_st25dvxxkc_dock_version_get(
    const r1_st25dvxxkc_dock_state *state, uint8_t *length);
void r1_st25dvxxkc_charge_temperature_set(
    r1_st25dvxxkc_dock_state *state, uint8_t temperature);
void r1_st25dvxxkc_dock_advertising_set(
    r1_st25dvxxkc_dock_state *state, uint8_t enabled);
bool r1_st25dvxxkc_is_dock_identity_frame(const uint8_t *frame,
                                           size_t length);
r1_error r1_st25dvxxkc_plan_dock_frame(
    r1_st25dvxxkc_dock_state *state, const uint8_t *frame,
    size_t frame_length, uint8_t mailbox_control, uint8_t *control_packet,
    size_t control_packet_length, r1_st25dvxxkc_dock_action *action);

#endif
