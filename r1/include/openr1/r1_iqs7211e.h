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
bool r1_iqs7211e_provider_available(const r1_iqs7211e_adapter *adapter);
bool r1_iqs7211e_ati_audit_begin(
    r1_iqs7211e_ati_audit_state state, uint32_t now_tick,
    r1_iqs7211e_layout layout, r1_iqs7211e_ati_audit_request *request);
bool r1_iqs7211e_ati_audit_summarize(
    const uint16_t *samples, size_t sample_count,
    const uint8_t *channel_map, r1_iqs7211e_ati_audit_summary *summary);

#endif
