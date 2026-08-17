#include "openr1/r1_iqs7211e.h"

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(r1_iqs7211e_factory_record, marker_4_value) == 6u,
               "factory marker-4 value offset");
_Static_assert(offsetof(r1_iqs7211e_factory_record, marker_6_value) == 8u,
               "factory marker-6 value offset");
_Static_assert(sizeof(r1_iqs7211e_factory_record) == 12u,
               "factory record size");
#endif

static uint32_t factory_record_transaction(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context,
    uint8_t marker) {
    if (record == NULL || ops == NULL || ops->record_begin == NULL ||
        ops->communication_end == NULL || ops->record_commit == NULL) {
        return 0u;
    }
    record->marker = marker;
    (void)ops->record_begin(context);
    (void)ops->communication_end(context);
    return ops->record_commit(context);
}

uint32_t r1_iqs7211e_factory_marker_1(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context) {
    return factory_record_transaction(record, ops, context, UINT8_C(1));
}

uint32_t r1_iqs7211e_factory_marker_2(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context) {
    return factory_record_transaction(record, ops, context, UINT8_C(2));
}

uint32_t r1_iqs7211e_factory_marker_3(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint8_t value) {
    const uint32_t status =
        factory_record_transaction(record, ops, context, UINT8_C(3));
    if (record != NULL && ops != NULL && ops->record_begin != NULL &&
        ops->communication_end != NULL && ops->record_commit != NULL) {
        record->marker_3_value = value;
    }
    return status;
}

uint32_t r1_iqs7211e_factory_marker_4(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint16_t value) {
    const uint32_t status =
        factory_record_transaction(record, ops, context, UINT8_C(4));
    if (record != NULL && ops != NULL && ops->record_begin != NULL &&
        ops->communication_end != NULL && ops->record_commit != NULL) {
        record->marker_4_value = value;
    }
    return status;
}

uint32_t r1_iqs7211e_factory_marker_5(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint8_t value) {
    const uint32_t status =
        factory_record_transaction(record, ops, context, UINT8_C(5));
    if (record != NULL && ops != NULL && ops->record_begin != NULL &&
        ops->communication_end != NULL && ops->record_commit != NULL) {
        record->marker_5_value = value;
    }
    return status;
}

uint32_t r1_iqs7211e_factory_marker_6(
    r1_iqs7211e_factory_record *record,
    const r1_iqs7211e_factory_record_ops *ops, void *context, uint32_t value) {
    const uint32_t status =
        factory_record_transaction(record, ops, context, UINT8_C(6));
    if (record != NULL && ops != NULL && ops->record_begin != NULL &&
        ops->communication_end != NULL && ops->record_commit != NULL) {
        record->marker_6_value = value;
    }
    return status;
}

static r1_error touch_lifecycle_plan_initialize(
    uint8_t client_index, r1_touch_lifecycle_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_touch_lifecycle_plan){0};
    if (client_index > 1u) {
        return R1_ERROR_UNSUPPORTED;
    }
    plan->accepted = true;
    plan->client_index = client_index;
    plan->operation_count = 2u;
    return R1_OK;
}

r1_error r1_touch_lifecycle_disable_plan(
    uint8_t client_index, r1_touch_lifecycle_plan *plan) {
    const r1_error error = touch_lifecycle_plan_initialize(client_index, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->operations[0].slot = R1_TOUCH_LIFECYCLE_SLOT_18;
    plan->operations[0].argument_0 = 0u;
    plan->operations[0].argument_1 = 0u;
    plan->operations[1].slot = R1_TOUCH_LIFECYCLE_SLOT_0C;
    return R1_OK;
}

r1_error r1_touch_lifecycle_enable_plan(
    uint8_t client_index, r1_touch_lifecycle_plan *plan) {
    const r1_error error = touch_lifecycle_plan_initialize(client_index, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->operations[0].slot = R1_TOUCH_LIFECYCLE_SLOT_08;
    plan->operations[1].slot = R1_TOUCH_LIFECYCLE_SLOT_18;
    plan->operations[1].argument_0 = 1u;
    plan->operations[1].argument_1 = 0u;
    return R1_OK;
}

#include <limits.h>

#define IQS_CAL(divider, fine, minimum, maximum, ...) \
    { (divider), (fine), (minimum), (maximum), { __VA_ARGS__ } }

/*
 * Exact 30-byte R1 calibration records are decoded by
 * scripts/firmware/summarize_r1_touch_calibration.py.  The two padding bytes
 * are represented structurally rather than copied into this table.
 */
static const r1_iqs7211e_calibration calibrations[2][10] = {
    {
        IQS_CAL(0x0a, 0x08, 0x03, 0x07, 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0a, 0x08, 0x03, 0x07, 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0c, 0x09, 0x02, 0x07, 0xff,0xff,0xff,0xff,0xff,0xff,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0c, 0x09, 0x02, 0x07, 0xff,0xff,0xff,0xff,0xff,0xff,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0c, 0x09, 0x01, 0x07, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0b, 0x09, 0x01, 0x07, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0b, 0x07, 0x01, 0x07, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0a, 0x07, 0x00, 0x07, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0a, 0x07, 0x00, 0x07, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
        IQS_CAL(0x0a, 0x07, 0x00, 0x07, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17),
    },
    {
        IQS_CAL(0x0a, 0x08, 0x03, 0x06, 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0xff,0xff,0xff),
        IQS_CAL(0x0a, 0x08, 0x03, 0x06, 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0xff,0xff,0xff),
        IQS_CAL(0x0c, 0x09, 0x02, 0x06, 0xff,0xff,0xff,0xff,0xff,0xff,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0xff,0xff,0xff),
        IQS_CAL(0x0c, 0x09, 0x02, 0x06, 0xff,0xff,0xff,0xff,0xff,0xff,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0xff,0xff,0xff),
        IQS_CAL(0x0c, 0x09, 0x01, 0x05, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
        IQS_CAL(0x0b, 0x09, 0x01, 0x05, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
        IQS_CAL(0x0b, 0x07, 0x01, 0x05, 0xff,0xff,0xff,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
        IQS_CAL(0x0a, 0x07, 0x00, 0x05, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
        IQS_CAL(0x0a, 0x07, 0x00, 0x05, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
        IQS_CAL(0x0a, 0x07, 0x00, 0x05, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0xff,0xff,0xff,0xff,0xff,0xff),
    },
};

#undef IQS_CAL

static bool provider_complete(const r1_iqs7211e_provider_ops *provider) {
    return provider != NULL && provider->read != NULL && provider->write != NULL;
}

static bool board_complete(const r1_iqs7211e_board_ops *board) {
    return board != NULL && board->open != NULL && board->close != NULL &&
           board->schedule_open != NULL;
}

void r1_iqs7211e_adapter_initialize(r1_iqs7211e_adapter *adapter) {
    if (adapter == NULL) {
        return;
    }
    adapter->provider = NULL;
    adapter->provider_context = NULL;
    adapter->board = NULL;
    adapter->board_context = NULL;
    adapter->sample_callback = NULL;
    adapter->sample_context = NULL;
    adapter->layout = R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX;
    adapter->ring_size = R1_IQS7211E_RING_SIZE_MIN;
    adapter->consecutive_ati_errors = 0u;
    adapter->hardware_restart_attempts = 0u;
    adapter->configured = false;
    adapter->restart_pending = false;
}

r1_error r1_iqs7211e_adapter_bind(r1_iqs7211e_adapter *adapter,
                                  const r1_iqs7211e_provider_ops *provider,
                                  void *provider_context,
                                  const r1_iqs7211e_board_ops *board,
                                  void *board_context) {
    if (adapter == NULL || !provider_complete(provider) || !board_complete(board)) {
        return R1_ERROR_ARGUMENT;
    }
    if (adapter->configured || adapter->restart_pending) {
        return R1_ERROR_STATE;
    }
    adapter->provider = provider;
    adapter->provider_context = provider_context;
    adapter->board = board;
    adapter->board_context = board_context;
    return R1_OK;
}

void r1_iqs7211e_set_sample_callback(r1_iqs7211e_adapter *adapter,
                                     r1_iqs7211e_sample_callback callback,
                                     void *context) {
    if (adapter != NULL) {
        adapter->sample_callback = callback;
        adapter->sample_context = context;
    }
}

bool r1_iqs7211e_provider_available(const r1_iqs7211e_adapter *adapter) {
    return adapter != NULL && provider_complete(adapter->provider) &&
           board_complete(adapter->board);
}

bool r1_iqs7211e_ati_audit_begin(
    r1_iqs7211e_ati_audit_state state, uint32_t now_tick,
    r1_iqs7211e_layout layout, r1_iqs7211e_ati_audit_request *request) {
    if (request == NULL ||
        (layout != R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX &&
         layout != R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX)) {
        return false;
    }
    state.sequence += UINT32_C(1);
    request->state = state;
    request->audit_due = state.sequence == UINT32_C(1) ||
        now_tick - state.last_tick >= R1_IQS7211E_ATI_AUDIT_INTERVAL_TICKS;
    request->device_address = R1_IQS7211E_ADDRESS;
    request->register_address = R1_IQS7211E_REGISTER_ATI_COMPENSATION;
    request->channel_count = layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX
        ? UINT8_C(24) : UINT8_C(21);
    request->read_length_bytes = (uint8_t)(request->channel_count * UINT8_C(2));
    if (request->audit_due) {
        request->state.last_tick = now_tick;
    }
    return true;
}

bool r1_iqs7211e_ati_audit_summarize(
    const uint16_t *samples, size_t sample_count,
    const uint8_t *channel_map, r1_iqs7211e_ati_audit_summary *summary) {
    if (samples == NULL || summary == NULL ||
        (sample_count != 21u && sample_count != 24u)) {
        return false;
    }
    summary->active_count = 0u;
    summary->minimum = UINT16_MAX;
    summary->maximum = 0u;
    for (size_t index = 0u; index < R1_IQS7211E_ATI_AUDIT_MAX_CHANNELS;
         ++index) {
        summary->active_values[index] = 0u;
    }
    for (size_t index = 0u; index < sample_count; ++index) {
        if (channel_map != NULL && channel_map[index] == UINT8_MAX) {
            continue;
        }
        const uint16_t value = samples[index];
        if (value < summary->minimum) {
            summary->minimum = value;
        }
        if (value > summary->maximum) {
            summary->maximum = value;
        }
        summary->active_values[summary->active_count] = value;
        ++summary->active_count;
    }
    if (summary->active_count == 0u) {
        summary->minimum = 0u;
    }
    return true;
}

const r1_iqs7211e_calibration *r1_iqs7211e_calibration_for(
    r1_iqs7211e_layout layout, uint8_t ring_size) {
    if ((layout != R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX &&
         layout != R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX) ||
        ring_size < R1_IQS7211E_RING_SIZE_MIN ||
        ring_size > R1_IQS7211E_RING_SIZE_MAX) {
        return NULL;
    }
    return &calibrations[(size_t)layout]
                        [(size_t)(ring_size - R1_IQS7211E_RING_SIZE_MIN)];
}

static r1_error write_block(r1_iqs7211e_adapter *adapter, uint8_t reg,
                            const uint8_t *bytes, size_t length) {
    if (adapter->provider->write(adapter->provider_context, R1_IQS7211E_ADDRESS,
                                 reg, bytes, length) != 0) {
        return R1_ERROR_STATE;
    }
    return R1_OK;
}

static r1_error read_block(r1_iqs7211e_adapter *adapter, uint8_t reg,
                           uint8_t *bytes, size_t length) {
    if (adapter->provider->read(adapter->provider_context, R1_IQS7211E_ADDRESS,
                                reg, bytes, length) != 0) {
        return R1_ERROR_STATE;
    }
    return R1_OK;
}

static r1_error write_word(r1_iqs7211e_adapter *adapter, uint8_t reg,
                           uint16_t value) {
    const uint8_t bytes[2] = {(uint8_t)value, (uint8_t)(value >> 8u)};
    return write_block(adapter, reg, bytes, sizeof bytes);
}

static r1_error end_communication(r1_iqs7211e_adapter *adapter) {
    return write_block(adapter, R1_IQS7211E_REGISTER_COMMUNICATION_END, NULL, 0u);
}

static void make_cycle_payload(const r1_iqs7211e_calibration *calibration,
                               uint8_t transmit_count, uint8_t *payload) {
    for (size_t cycle = 0u; cycle < 21u; ++cycle) {
        const size_t output = cycle * 3u;
        payload[output] = 5u;
        payload[output + 1u] = UINT8_MAX;
        payload[output + 2u] = UINT8_MAX;
        if (cycle < (size_t)transmit_count * 2u) {
            const size_t input = (cycle / 2u) * 3u;
            if ((cycle & 1u) == 0u) {
                payload[output + 1u] = calibration->channel_slots[input];
                payload[output + 2u] = calibration->channel_slots[input + 1u];
            } else {
                payload[output + 1u] = calibration->channel_slots[input + 2u];
            }
        }
    }
}

static r1_error configure_blocks(r1_iqs7211e_adapter *adapter,
                                 r1_iqs7211e_layout layout,
                                 const r1_iqs7211e_calibration *calibration) {
    static const uint8_t alp_compensation[] = {0x11u, 0x02u, 0x1fu, 0x02u};
    static const uint8_t report_timing[] = {
        0x06u,0x00u,0x64u,0x00u,0x20u,0x00u,0x20u,0x00u,0x64u,0x00u,0x02u,
        0x00u,0x46u,0x00u,0x01u,0x00u,0x0au,0x00u,0x02u,0x08u,0x64u,0x00u,
    };
    static const uint8_t gestures[] = {
        0x0fu,0x0cu,0x90u,0x01u,0x2cu,0x01u,0x3cu,0x00u,0xe8u,0x03u,0x58u,
        0x02u,0xd0u,0x07u,0x4bu,0x00u,0xe8u,0x03u,0xe8u,0x03u,0x28u,0x1eu,
    };
    static const uint8_t final_control[] = {0xa0u,0x00u,0x6cu,0x47u,0x00u,0x00u};
    uint8_t ati[14] = {
        0xe1u,0u,0u,0x20u,0xf0u,0x00u,0x20u,0x00u,0x22u,0x02u,0x04u,0x14u,
        0xf0u,0x00u,
    };
    uint8_t hardware[22] = {
        0x44u,0x03u,0xa3u,0u,0x40u,0x3fu,0x06u,0x00u,0x01u,0x01u,0xdcu,
        0x08u,0xf0u,0x10u,0x02u,0x1au,0x02u,0x1au,0x03u,0x8cu,0x47u,0x9cu,
    };
    uint8_t trackpad[20] = {
        0x28u,0x03u,0u,0x01u,0x40u,0x00u,0x00u,0x05u,0x06u,0x00u,0x7cu,
        0x00u,0x07u,0x80u,0x94u,0x00u,0x04u,0x00u,0x28u,0x28u,
    };
    uint8_t mapping[14] = {
        0x02u,0x06u,0x03u,0x05u,0x08u,0x07u,0x0bu,0x00u,0x09u,0u,0u,0x0bu,
        0x0cu,0x00u,
    };
    uint8_t cycles[63];

    ati[1] = (uint8_t)((uint16_t)calibration->fine_fractional_divider * 2u + 1u);
    ati[2] = calibration->compensation_divider;
    hardware[3] = layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX ? 0x0bu : 0x1bu;
    trackpad[2] = layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX ? 0x07u : 0x08u;
    mapping[9] = layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX ? 0x0cu : 0x01u;
    mapping[10] = layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX ? 0x01u : 0x0au;
    make_cycle_payload(calibration,
                       layout == R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX ? 8u : 7u,
                       cycles);

    struct frame {
        uint8_t reg;
        const uint8_t *bytes;
        size_t length;
    };
    const struct frame frames[] = {
        {0x1fu, alp_compensation, sizeof alp_compensation},
        {0x21u, ati, sizeof ati},
        {0x28u, report_timing, sizeof report_timing},
        {0x36u, hardware, sizeof hardware},
        {0x41u, trackpad, sizeof trackpad},
        {0x4bu, gestures, sizeof gestures},
        {0x56u, mapping, sizeof mapping},
        {0x5du, cycles, 30u},
        {0x6cu, cycles + 30u, 33u},
        {0x33u, final_control, sizeof final_control},
    };
    for (size_t index = 0u; index < sizeof frames / sizeof frames[0]; ++index) {
        const r1_error error = write_block(adapter, frames[index].reg,
                                           frames[index].bytes,
                                           frames[index].length);
        if (error != R1_OK) {
            return error;
        }
    }
    return R1_OK;
}

r1_error r1_iqs7211e_configure(r1_iqs7211e_adapter *adapter,
                               r1_iqs7211e_layout layout, uint8_t ring_size) {
    if (!r1_iqs7211e_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    const r1_iqs7211e_calibration *calibration =
        r1_iqs7211e_calibration_for(layout, ring_size);
    if (calibration == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!adapter->board->open(adapter->board_context)) {
        return R1_ERROR_STATE;
    }
    const r1_error error = configure_blocks(adapter, layout, calibration);
    if (error != R1_OK) {
        adapter->board->close(adapter->board_context);
        adapter->configured = false;
        return error;
    }
    adapter->layout = layout;
    adapter->ring_size = ring_size;
    adapter->configured = true;
    return R1_OK;
}

r1_error r1_iqs7211e_suspend(r1_iqs7211e_adapter *adapter) {
    if (!r1_iqs7211e_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    uint8_t bytes[2];
    r1_error error = read_block(adapter, R1_IQS7211E_REGISTER_SYSTEM_CONTROL,
                                bytes, sizeof bytes);
    if (error == R1_OK) {
        const uint16_t value = (uint16_t)((uint16_t)bytes[0] |
                                         ((uint16_t)bytes[1] << 8u));
        error = write_word(adapter, R1_IQS7211E_REGISTER_SYSTEM_CONTROL,
                           (uint16_t)(value | R1_IQS7211E_SYSTEM_SUSPEND));
    }
    if (error == R1_OK) {
        error = end_communication(adapter);
    }
    return error;
}

r1_error r1_iqs7211e_deactivate(r1_iqs7211e_adapter *adapter) {
    if (!r1_iqs7211e_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    r1_error error = R1_OK;
    if (adapter->configured) {
        error = r1_iqs7211e_suspend(adapter);
    }
    adapter->board->close(adapter->board_context);
    adapter->configured = false;
    adapter->restart_pending = false;
    adapter->consecutive_ati_errors = 0u;
    adapter->hardware_restart_attempts = 0u;
    return error;
}

static r1_error ati_error(r1_iqs7211e_adapter *adapter) {
    if (adapter->consecutive_ati_errors != UINT8_MAX) {
        ++adapter->consecutive_ati_errors;
    }
    if (adapter->consecutive_ati_errors < R1_IQS7211E_ATI_RESTART_THRESHOLD &&
        adapter->hardware_restart_attempts < R1_IQS7211E_ATI_RESTART_LIMIT) {
        return write_word(adapter, R1_IQS7211E_REGISTER_SYSTEM_CONTROL,
                          R1_IQS7211E_SYSTEM_TP_RE_ATI);
    }
    if (adapter->hardware_restart_attempts < R1_IQS7211E_ATI_RESTART_LIMIT) {
        ++adapter->hardware_restart_attempts;
        adapter->consecutive_ati_errors = 0u;
        adapter->configured = false;
        adapter->restart_pending = true;
        adapter->board->close(adapter->board_context);
        if (!adapter->board->schedule_open(adapter->board_context,
                                           R1_IQS7211E_RESTART_DELAY_TICKS)) {
            adapter->restart_pending = false;
            return R1_ERROR_STATE;
        }
    }
    return R1_OK;
}

r1_error r1_iqs7211e_process_irq(r1_iqs7211e_adapter *adapter,
                                 uint8_t factory_marker) {
    if (!r1_iqs7211e_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (!adapter->configured || adapter->restart_pending) {
        return R1_ERROR_STATE;
    }
    const uint8_t config_low = 0x6cu;
    r1_error error = write_block(adapter, R1_IQS7211E_REGISTER_CONFIG,
                                 &config_low, 1u);
    uint8_t bytes[6];
    if (error == R1_OK) {
        error = read_block(adapter, R1_IQS7211E_REGISTER_INFO_FLAGS,
                           bytes, sizeof bytes);
    }
    if (error != R1_OK) {
        return error;
    }
    const r1_iqs7211e_irq_sample sample = {
        (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8u)),
        (uint16_t)((uint16_t)bytes[2] | ((uint16_t)bytes[3] << 8u)),
        (uint16_t)((uint16_t)bytes[4] | ((uint16_t)bytes[5] << 8u)),
    };
    if ((sample.info_flags & R1_IQS7211E_INFO_SHOW_RESET) != 0u) {
        error = configure_blocks(adapter, adapter->layout,
                                 r1_iqs7211e_calibration_for(adapter->layout,
                                                             adapter->ring_size));
    } else if ((sample.info_flags & R1_IQS7211E_INFO_ATI_ERROR) != 0u &&
               factory_marker != 0x55u) {
        error = ati_error(adapter);
    } else {
        if (factory_marker != 0x55u) {
            adapter->consecutive_ati_errors = 0u;
            adapter->hardware_restart_attempts = 0u;
        }
        if ((sample.info_flags & R1_IQS7211E_INFO_TOO_MANY_FINGERS) != 0u) {
            error = write_word(adapter, R1_IQS7211E_REGISTER_SYSTEM_CONTROL,
                               R1_IQS7211E_SYSTEM_TP_RESEED);
        } else if (adapter->sample_callback != NULL) {
            adapter->sample_callback(adapter->sample_context, &sample);
        }
    }
    if (error == R1_OK && !adapter->restart_pending) {
        error = end_communication(adapter);
    }
    return error;
}

r1_error r1_iqs7211e_resume_scheduled_restart(r1_iqs7211e_adapter *adapter) {
    if (!r1_iqs7211e_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (!adapter->restart_pending) {
        return R1_ERROR_STATE;
    }
    adapter->restart_pending = false;
    return r1_iqs7211e_configure(adapter, adapter->layout, adapter->ring_size);
}

r1_error r1_touch_recovery_timer_plan_build(
    r1_touch_recovery_timer_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_touch_recovery_timer_plan){
        .clear_recovery_pending_latch = true,
        .task_event_flags = R1_TOUCH_RECOVERY_OPEN_EVENT_FLAG,
    };
    return R1_OK;
}
