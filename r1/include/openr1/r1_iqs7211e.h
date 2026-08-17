#ifndef OPENR1_R1_IQS7211E_H
#define OPENR1_R1_IQS7211E_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * R1 product adapter around an attributable IQS7211E provider/transport.
 *
 * Register semantics and the initialization flow are supplied by the pinned
 * IQS7211E upstream references.  The tables, two electrode layouts, ring-size
 * records, retry limits, and board lifecycle policy are recovered R1 data.
 */
#define R1_IQS7211E_ADDRESS UINT8_C(0x56)
#define R1_IQS7211E_PRODUCT_NUMBER UINT16_C(0x0458)
#define R1_IQS7211E_REGISTER_GESTURES UINT8_C(0x0e)
#define R1_IQS7211E_REGISTER_INFO_FLAGS UINT8_C(0x0f)
#define R1_IQS7211E_REGISTER_SYSTEM_CONTROL UINT8_C(0x33)
#define R1_IQS7211E_REGISTER_CONFIG UINT8_C(0x34)
#define R1_IQS7211E_REGISTER_CHANNEL_DATA UINT8_C(0xe0)
#define R1_IQS7211E_REGISTER_ATI_COMPENSATION UINT8_C(0xe3)
#define R1_IQS7211E_REGISTER_COMMUNICATION_END UINT8_C(0xff)

#define R1_IQS7211E_INFO_ATI_ERROR UINT16_C(0x0008)
#define R1_IQS7211E_INFO_RE_ATI UINT16_C(0x0010)
#define R1_IQS7211E_INFO_SHOW_RESET UINT16_C(0x0080)
#define R1_IQS7211E_INFO_TOO_MANY_FINGERS UINT16_C(0x1000)
#define R1_IQS7211E_SYSTEM_TP_RESEED UINT16_C(0x0008)
#define R1_IQS7211E_SYSTEM_TP_RE_ATI UINT16_C(0x0020)
#define R1_IQS7211E_SYSTEM_ACK_RESET UINT16_C(0x0080)
#define R1_IQS7211E_SYSTEM_SUSPEND UINT16_C(0x0800)

#define R1_IQS7211E_RING_SIZE_MIN UINT8_C(6)
#define R1_IQS7211E_RING_SIZE_MAX UINT8_C(15)
#define R1_IQS7211E_CHANNEL_SLOT_COUNT 24u
#define R1_IQS7211E_CONFIG_MAX_WRITE 33u
#define R1_IQS7211E_ATI_RESTART_THRESHOLD UINT8_C(5)
#define R1_IQS7211E_ATI_RESTART_LIMIT UINT8_C(3)
#define R1_IQS7211E_RESTART_DELAY_TICKS UINT32_C(0x66)
#define R1_IQS7211E_ATI_AUDIT_INTERVAL_TICKS UINT32_C(10000)
#define R1_IQS7211E_ATI_AUDIT_MAX_CHANNELS 24u

typedef enum {
    R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX = 0,
    R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX = 1
} r1_iqs7211e_layout;

typedef struct {
    uint8_t compensation_divider;
    uint8_t fine_fractional_divider;
    uint8_t minimum_trim_index;
    uint8_t maximum_trim_index;
    uint8_t channel_slots[R1_IQS7211E_CHANNEL_SLOT_COUNT];
} r1_iqs7211e_calibration;

typedef struct {
    uint16_t info_flags;
    uint16_t finger_1_x;
    uint16_t finger_1_y;
} r1_iqs7211e_irq_sample;

typedef struct {
    int32_t (*read)(void *context, uint8_t device_address, uint8_t register_address,
                    uint8_t *bytes, size_t length);
    int32_t (*write)(void *context, uint8_t device_address, uint8_t register_address,
                     const uint8_t *bytes, size_t length);
} r1_iqs7211e_provider_ops;

typedef struct {
    bool (*open)(void *context);
    void (*close)(void *context);
    bool (*schedule_open)(void *context, uint32_t delay_ticks);
} r1_iqs7211e_board_ops;

#define R1_TOUCH_RECOVERY_OPEN_EVENT_FLAG UINT32_C(0x00000002)

typedef struct {
    bool clear_recovery_pending_latch;
    uint32_t task_event_flags;
} r1_touch_recovery_timer_plan;

typedef void (*r1_iqs7211e_sample_callback)(void *context,
                                            const r1_iqs7211e_irq_sample *sample);

typedef struct {
    const r1_iqs7211e_provider_ops *provider;
    void *provider_context;
    const r1_iqs7211e_board_ops *board;
    void *board_context;
    r1_iqs7211e_sample_callback sample_callback;
    void *sample_context;
    r1_iqs7211e_layout layout;
    uint8_t ring_size;
    uint8_t consecutive_ati_errors;
    uint8_t hardware_restart_attempts;
    bool configured;
    bool restart_pending;
} r1_iqs7211e_adapter;

typedef struct {
    uint32_t sequence;
    uint32_t last_tick;
} r1_iqs7211e_ati_audit_state;

typedef struct {
    r1_iqs7211e_ati_audit_state state;
    bool audit_due;
    uint8_t device_address;
    uint8_t register_address;
    uint8_t channel_count;
    uint8_t read_length_bytes;
} r1_iqs7211e_ati_audit_request;

typedef struct {
    uint8_t active_count;
    uint16_t minimum;
    uint16_t maximum;
    uint16_t active_values[R1_IQS7211E_ATI_AUDIT_MAX_CHANNELS];
} r1_iqs7211e_ati_audit_summary;

/* Transparent product record used by the six factory-marker tail targets at
 * 0x0004FA8C...0x0004FB24. The reserved bytes preserve the recovered target
 * offsets without exposing a controller-register command surface. */
typedef struct {
    uint8_t marker;
    uint8_t marker_3_value;
    uint8_t marker_5_value;
    uint8_t reserved_03_05[3];
    uint16_t marker_4_value;
    uint32_t marker_6_value;
} r1_iqs7211e_factory_record;

typedef struct {
    uint32_t (*record_begin)(void *context);
    int32_t (*communication_end)(void *context);
    uint32_t (*record_commit)(void *context);
} r1_iqs7211e_factory_record_ops;

typedef enum {
    R1_TOUCH_LIFECYCLE_SLOT_08 = 0x08,
    R1_TOUCH_LIFECYCLE_SLOT_0C = 0x0c,
    R1_TOUCH_LIFECYCLE_SLOT_18 = 0x18
} r1_touch_lifecycle_slot;

typedef struct {
    r1_touch_lifecycle_slot slot;
    uint8_t argument_0;
    uint8_t argument_1;
} r1_touch_lifecycle_operation;

typedef struct {
    bool accepted;
    uint8_t client_index;
    uint8_t operation_count;
    r1_touch_lifecycle_operation operations[2];
} r1_touch_lifecycle_plan;

void r1_iqs7211e_adapter_initialize(r1_iqs7211e_adapter *adapter);
r1_error r1_iqs7211e_adapter_bind(r1_iqs7211e_adapter *adapter,
                                  const r1_iqs7211e_provider_ops *provider,
                                  void *provider_context,
                                  const r1_iqs7211e_board_ops *board,
                                  void *board_context);
void r1_iqs7211e_set_sample_callback(r1_iqs7211e_adapter *adapter,
                                     r1_iqs7211e_sample_callback callback,
                                     void *context);
const r1_iqs7211e_calibration *r1_iqs7211e_calibration_for(
    r1_iqs7211e_layout layout, uint8_t ring_size);
r1_error r1_iqs7211e_configure(r1_iqs7211e_adapter *adapter,
                               r1_iqs7211e_layout layout, uint8_t ring_size);
r1_error r1_iqs7211e_suspend(r1_iqs7211e_adapter *adapter);
r1_error r1_iqs7211e_deactivate(r1_iqs7211e_adapter *adapter);
r1_error r1_iqs7211e_process_irq(r1_iqs7211e_adapter *adapter,
                                 uint8_t factory_marker);
r1_error r1_iqs7211e_resume_scheduled_restart(r1_iqs7211e_adapter *adapter);
r1_error r1_touch_recovery_timer_plan_build(
    r1_touch_recovery_timer_plan *plan);
bool r1_iqs7211e_provider_available(const r1_iqs7211e_adapter *adapter);
bool r1_iqs7211e_ati_audit_begin(
    r1_iqs7211e_ati_audit_state state, uint32_t now_tick,
    r1_iqs7211e_layout layout, r1_iqs7211e_ati_audit_request *request);
bool r1_iqs7211e_ati_audit_summarize(
    const uint16_t *samples, size_t sample_count,
    const uint8_t *channel_map, r1_iqs7211e_ati_audit_summary *summary);
uint32_t r1_iqs7211e_factory_marker_1(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context);
uint32_t r1_iqs7211e_factory_marker_2(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context);
uint32_t r1_iqs7211e_factory_marker_3(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint8_t value);
uint32_t r1_iqs7211e_factory_marker_4(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint16_t value);
uint32_t r1_iqs7211e_factory_marker_5(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint8_t value);
uint32_t r1_iqs7211e_factory_marker_6(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint32_t value);
r1_error r1_touch_lifecycle_disable_plan(
    uint8_t client_index, r1_touch_lifecycle_plan *plan);
r1_error r1_touch_lifecycle_enable_plan(
    uint8_t client_index, r1_touch_lifecycle_plan *plan);

#endif
