#include "openr1/r1_st25dvxxkc.h"

static void clear_bytes(void *memory, size_t length) {
    uint8_t *bytes = memory;
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

uint32_t r1_st25dvxxkc_bus_tick_get(const r1_st25dvxxkc_bus_io_ops *ops,
                                    void *context) {
    return ops != NULL && ops->tick_get != NULL ? ops->tick_get(context) : 0u;
}

int32_t r1_st25dvxxkc_bus_initialize(const r1_st25dvxxkc_bus_io_ops *ops,
                                     void *context) {
    if (ops == NULL || ops->acquire == NULL) {
        return -1;
    }
    ops->acquire(context);
    return 0;
}

int32_t r1_st25dvxxkc_bus_deinitialize(const r1_st25dvxxkc_bus_io_ops *ops,
                                       void *context) {
    if (ops == NULL || ops->release == NULL) {
        return -1;
    }
    ops->release(context);
    return 0;
}

int32_t r1_st25dvxxkc_bus_is_ready(const r1_st25dvxxkc_bus_io_ops *ops,
                                   void *context, uint16_t device_address,
                                   uint32_t trials) {
    (void)device_address;
    (void)trials;
    if (ops == NULL || ops->delay == NULL) {
        return -1;
    }
    ops->delay(context, R1_ST25DVXXKC_BUS_READY_DELAY_TICKS);
    return 0;
}

int32_t r1_st25dvxxkc_bus_read(const r1_st25dvxxkc_bus_io_ops *ops,
                               void *context, uint16_t device_address,
                               uint16_t register_address, uint8_t *bytes,
                               uint16_t length) {
    if (ops == NULL || ops->read == NULL) {
        return -1;
    }
    return ops->read(context, (uint8_t)device_address, register_address, bytes,
                     length);
}

int32_t r1_st25dvxxkc_bus_write(const r1_st25dvxxkc_bus_io_ops *ops,
                                void *context, uint16_t device_address,
                                uint16_t register_address,
                                const uint8_t *bytes, uint16_t length) {
    if (ops == NULL || ops->write == NULL) {
        return -1;
    }
    return ops->write(context, (uint8_t)device_address, register_address,
                      bytes, length);
}

static uint16_t read_big_endian_u16(const uint8_t *bytes) {
    return (uint16_t)(((uint16_t)bytes[0] << 8u) | (uint16_t)bytes[1]);
}

static void format_dock_version(char output[R1_ST25DVXXKC_DOCK_VERSION_SIZE],
                                uint16_t release, uint16_t build) {
    output[0] = (char)('0' + (char)((release / 100u) % 10u));
    output[1] = '.';
    output[2] = (char)('0' + (char)((release / 10u) % 10u));
    output[3] = '.';
    output[4] = (char)('0' + (char)(release % 10u));
    output[5] = '.';

    /* snprintf(..., 11, "%d.%d.%d.%04d") keeps the first four build
     * digits when a five-digit uint16_t build is truncated. */
    uint16_t divisor = UINT16_C(1000);
    if (build >= UINT16_C(10000)) {
        divisor = UINT16_C(10000);
    }
    for (size_t index = 0u; index < 4u; ++index) {
        output[6u + index] =
            (char)('0' + (char)((build / divisor) % UINT16_C(10)));
        divisor = (uint16_t)(divisor / UINT16_C(10));
    }
    output[10] = '\0';
}

static bool provider_complete(const r1_st25dvxxkc_provider_ops *provider) {
    return provider != NULL && provider->initialize != NULL &&
           provider->deinitialize != NULL && provider->read_id != NULL &&
           provider->read_security_session != NULL &&
           provider->present_password != NULL &&
           provider->read_mailbox_mode != NULL &&
           provider->read_mailbox_status != NULL &&
           provider->set_mailbox_enabled != NULL &&
           provider->reset_energy_harvesting != NULL &&
           provider->set_gpo1 != NULL && provider->read_gpo2 != NULL &&
           provider->set_gpo2 != NULL &&
           provider->read_mailbox_length != NULL &&
           provider->read_mailbox != NULL && provider->delay != NULL;
}

static r1_error set_security_session(r1_st25dvxxkc_adapter *adapter,
                                     bool should_be_open) {
    bool open = false;
    if (adapter->provider->read_security_session(adapter->provider_context,
                                                 &open) != 0) {
        return R1_ERROR_STATE;
    }
    if (open != should_be_open) {
        const uint32_t most_significant =
            should_be_open ? UINT32_C(0) : R1_ST25DVXXKC_SESSION_CLOSE_MSB;
        const uint32_t least_significant =
            should_be_open ? UINT32_C(0) : R1_ST25DVXXKC_SESSION_CLOSE_LSB;
        if (adapter->provider->present_password(adapter->provider_context,
                                                most_significant,
                                                least_significant) != 0) {
            return R1_ERROR_STATE;
        }
        if (adapter->provider->read_security_session(adapter->provider_context,
                                                     &open) != 0 ||
            open != should_be_open) {
            return R1_ERROR_UNAUTHORIZED;
        }
    }
    return R1_OK;
}

static void close_security_session_best_effort(
    r1_st25dvxxkc_adapter *adapter) {
    (void)adapter->provider->present_password(
        adapter->provider_context, R1_ST25DVXXKC_SESSION_CLOSE_MSB,
        R1_ST25DVXXKC_SESSION_CLOSE_LSB);
}

static r1_error configure_gpo(r1_st25dvxxkc_adapter *adapter) {
    int32_t status = -1;
    for (size_t attempt = 0u; attempt < R1_ST25DVXXKC_GPO_RETRIES;
         ++attempt) {
        status = adapter->provider->set_gpo1(
            adapter->provider_context, R1_ST25DVXXKC_GPO1_CONFIGURATION);
        if (status == 0) {
            break;
        }
    }
    if (status != 0) {
        return R1_ERROR_STATE;
    }

    uint8_t gpo2 = 0u;
    if (adapter->provider->read_gpo2(adapter->provider_context, &gpo2) != 0) {
        return R1_ERROR_STATE;
    }
    gpo2 = (uint8_t)(gpo2 & (uint8_t)~R1_ST25DVXXKC_GPO2_CLEAR_MASK);
    for (size_t attempt = 0u; attempt < R1_ST25DVXXKC_GPO_RETRIES;
         ++attempt) {
        status = adapter->provider->set_gpo2(adapter->provider_context, gpo2);
        if (status == 0) {
            return R1_OK;
        }
    }
    return R1_ERROR_STATE;
}

void r1_st25dvxxkc_adapter_initialize(r1_st25dvxxkc_adapter *adapter) {
    if (adapter != NULL) {
        clear_bytes(adapter, sizeof *adapter);
    }
}

r1_error r1_st25dvxxkc_adapter_bind(
    r1_st25dvxxkc_adapter *adapter,
    const r1_st25dvxxkc_provider_ops *provider, void *provider_context) {
    if (adapter == NULL || !provider_complete(provider)) {
        return R1_ERROR_ARGUMENT;
    }
    if (adapter->initialized) {
        return R1_ERROR_STATE;
    }
    adapter->provider = provider;
    adapter->provider_context = provider_context;
    return R1_OK;
}

void r1_st25dvxxkc_set_frame_callback(r1_st25dvxxkc_adapter *adapter,
                                      r1_st25dvxxkc_frame_callback callback,
                                      void *context) {
    if (adapter != NULL) {
        adapter->frame_callback = callback;
        adapter->frame_context = context;
    }
}

bool r1_st25dvxxkc_provider_available(const r1_st25dvxxkc_adapter *adapter) {
    return adapter != NULL && provider_complete(adapter->provider);
}

bool r1_st25dvxxkc_mailbox_length_allowed(size_t length) {
    return length <= R1_ST25DVXXKC_MAILBOX_CAPACITY;
}

void r1_st25dvxxkc_dock_state_initialize(r1_st25dvxxkc_dock_state *state) {
    if (state != NULL) {
        clear_bytes(state, sizeof *state);
    }
}

void r1_st25dvxxkc_dock_hardware_clear(r1_st25dvxxkc_dock_state *state) {
    if (state != NULL) {
        state->dock_hardware_revision = 0u;
    }
}

uint8_t r1_st25dvxxkc_dock_hardware_get(
    const r1_st25dvxxkc_dock_state *state) {
    return state != NULL ? state->dock_hardware_revision : 0u;
}

void r1_st25dvxxkc_dock_version_clear(r1_st25dvxxkc_dock_state *state) {
    if (state != NULL) {
        clear_bytes(state->dock_version, sizeof state->dock_version);
    }
}

const char *r1_st25dvxxkc_dock_version_get(
    const r1_st25dvxxkc_dock_state *state, uint8_t *length) {
    if (state == NULL || length == NULL) {
        return NULL;
    }
    size_t measured = 0u;
    while (measured < sizeof state->dock_version &&
           state->dock_version[measured] != '\0') {
        ++measured;
    }
    *length = (uint8_t)measured;
    return state->dock_version;
}

void r1_st25dvxxkc_charge_temperature_set(
    r1_st25dvxxkc_dock_state *state, uint8_t temperature) {
    if (state != NULL) {
        state->charge_temperature = temperature;
    }
}

void r1_st25dvxxkc_dock_advertising_set(
    r1_st25dvxxkc_dock_state *state, uint8_t enabled) {
    if (state != NULL) {
        state->dock_advertising_enabled = enabled;
    }
}

bool r1_st25dvxxkc_is_dock_identity_frame(const uint8_t *frame,
                                           size_t length) {
    return frame != NULL && length >= R1_ST25DVXXKC_DOCK_HEADER_SIZE &&
           frame[0] == UINT8_C(1) && frame[1] == UINT8_C(2) &&
           frame[2] == UINT8_C(3) && frame[3] == UINT8_C(4);
}

r1_error r1_st25dvxxkc_plan_dock_frame(
    r1_st25dvxxkc_dock_state *state, const uint8_t *frame,
    size_t frame_length, uint8_t mailbox_control, uint8_t *control_packet,
    size_t control_packet_length, r1_st25dvxxkc_dock_action *action) {
    if (state == NULL || frame == NULL || action == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *action = R1_ST25DVXXKC_DOCK_ACTION_NONE;

    if (!r1_st25dvxxkc_is_dock_identity_frame(frame, frame_length)) {
        if (frame_length >= 2u && frame[0] == UINT8_C(0x55) &&
            frame[1] == UINT8_C(4)) {
            *action = R1_ST25DVXXKC_DOCK_ACTION_SCHEDULE_CHARGE_FIELD;
        }
        return R1_OK;
    }
    if (control_packet == NULL ||
        control_packet_length < R1_ST25DVXXKC_DOCK_CONTROL_PACKET_SIZE) {
        return R1_ERROR_LENGTH;
    }

    state->heartbeat_count = (uint8_t)(state->heartbeat_count + UINT8_C(1));
    format_dock_version(state->dock_version, read_big_endian_u16(&frame[4]),
                        read_big_endian_u16(&frame[6]));
    state->dock_accessory = frame[8];
    state->field_seen = true;

    if (mailbox_control != R1_ST25DVXXKC_DOCK_MAILBOX_READY) {
        return R1_OK;
    }

    if (state->advertisement_marker != R1_ST25DVXXKC_DOCK_ADVERTISED) {
        control_packet[1] = UINT8_C(0x55);
        control_packet[2] = UINT8_C(3);
        control_packet[3] = state->advertisement_marker;
        state->advertisement_marker = R1_ST25DVXXKC_DOCK_ADVERTISED;
        *action = R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET;
        return R1_OK;
    }

    if (state->heartbeat_count <= R1_ST25DVXXKC_DOCK_HEARTBEAT_LIMIT) {
        if (control_packet[6] < R1_ST25DVXXKC_DOCK_DELAY_THRESHOLD) {
            state->cached_field_delay = control_packet[6];
        } else {
            control_packet[6] = state->cached_field_delay;
        }
    } else {
        state->heartbeat_count = 0u;
        const uint8_t sampled_delay = (uint8_t)(control_packet[4] >> 2u);
        control_packet[1] = UINT8_C(0x55);
        control_packet[2] = UINT8_C(4);
        control_packet[3] = UINT8_C(0);
        control_packet[4] = state->adc_reference < sampled_delay
                                ? R1_ST25DVXXKC_DOCK_DELAY_LONG
                                : R1_ST25DVXXKC_DOCK_DELAY_SHORT;
    }
    *action = R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET;
    return R1_OK;
}

r1_error r1_st25dvxxkc_activate(r1_st25dvxxkc_adapter *adapter) {
    if (!r1_st25dvxxkc_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (adapter->initialized) {
        return R1_OK;
    }

    int32_t status = -1;
    for (size_t attempt = 0u; attempt < R1_ST25DVXXKC_INITIALIZE_RETRIES;
         ++attempt) {
        status = adapter->provider->initialize(adapter->provider_context);
        if (status == 0) {
            break;
        }
    }
    if (status != 0) {
        adapter->provider->deinitialize(adapter->provider_context);
        return R1_ERROR_STATE;
    }

    uint8_t ic_reference = 0u;
    if (adapter->provider->read_id(adapter->provider_context,
                                  &ic_reference) != 0 ||
        (ic_reference != R1_ST25DVXXKC_ICREF_04KC &&
         ic_reference != R1_ST25DVXXKC_ICREF_64KC)) {
        adapter->provider->deinitialize(adapter->provider_context);
        return R1_ERROR_UNSUPPORTED;
    }

    r1_error result = set_security_session(adapter, true);
    if (result != R1_OK) {
        close_security_session_best_effort(adapter);
        adapter->provider->deinitialize(adapter->provider_context);
        return result;
    }

    r1_st25dvxxkc_mailbox_status mailbox_status;
    clear_bytes(&mailbox_status, sizeof mailbox_status);
    if (adapter->provider->read_mailbox_status(adapter->provider_context,
                                               &mailbox_status) != 0) {
        result = R1_ERROR_STATE;
        goto close_session;
    }
    if (!mailbox_status.mailbox_enabled) {
        adapter->provider->delay(adapter->provider_context,
                                 R1_ST25DVXXKC_SETTLE_TICKS);
        if (adapter->provider->set_mailbox_enabled(
                adapter->provider_context) != 0) {
            result = R1_ERROR_STATE;
            goto close_session;
        }
        adapter->provider->delay(adapter->provider_context,
                                 R1_ST25DVXXKC_SETTLE_TICKS);
        clear_bytes(&mailbox_status, sizeof mailbox_status);
        if (adapter->provider->read_mailbox_status(adapter->provider_context,
                                                   &mailbox_status) != 0 ||
            !mailbox_status.mailbox_enabled) {
            result = R1_ERROR_STATE;
            goto close_session;
        }
    }
    if (adapter->provider->reset_energy_harvesting(
            adapter->provider_context) != 0) {
        result = R1_ERROR_STATE;
        goto close_session;
    }
    adapter->provider->delay(adapter->provider_context,
                             R1_ST25DVXXKC_SETTLE_TICKS);
    if (adapter->provider->set_mailbox_enabled(adapter->provider_context) != 0) {
        result = R1_ERROR_STATE;
        goto close_session;
    }
    adapter->provider->delay(adapter->provider_context,
                             R1_ST25DVXXKC_SETTLE_TICKS);
    clear_bytes(&mailbox_status, sizeof mailbox_status);
    if (adapter->provider->read_mailbox_status(adapter->provider_context,
                                               &mailbox_status) != 0 ||
        !mailbox_status.mailbox_enabled) {
        result = R1_ERROR_STATE;
        goto close_session;
    }
    adapter->provider->delay(adapter->provider_context,
                             R1_ST25DVXXKC_SETTLE_TICKS);
    result = configure_gpo(adapter);
    adapter->provider->delay(adapter->provider_context,
                             R1_ST25DVXXKC_SETTLE_TICKS);

close_session:
    {
        const r1_error close_result = set_security_session(adapter, false);
        if (result == R1_OK && close_result != R1_OK) {
            result = close_result;
        }
    }
    if (result != R1_OK) {
        close_security_session_best_effort(adapter);
        adapter->provider->deinitialize(adapter->provider_context);
        return result;
    }

    adapter->ic_reference = ic_reference;
    adapter->initialized = true;
    return R1_OK;
}

void r1_st25dvxxkc_deactivate(r1_st25dvxxkc_adapter *adapter) {
    if (adapter != NULL && adapter->provider != NULL) {
        adapter->provider->deinitialize(adapter->provider_context);
        adapter->initialized = false;
        adapter->ic_reference = 0u;
        clear_bytes(adapter->mailbox, sizeof adapter->mailbox);
    }
}

r1_error r1_st25dvxxkc_poll(r1_st25dvxxkc_adapter *adapter, bool *received) {
    if (adapter == NULL || received == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *received = false;
    if (!adapter->initialized || !r1_st25dvxxkc_provider_available(adapter)) {
        return R1_ERROR_STATE;
    }

    bool mailbox_mode = false;
    if (adapter->provider->read_mailbox_mode(adapter->provider_context,
                                             &mailbox_mode) != 0) {
        return R1_ERROR_STATE;
    }
    if (!mailbox_mode) {
        return R1_OK;
    }

    r1_st25dvxxkc_mailbox_status status;
    clear_bytes(&status, sizeof status);
    if (adapter->provider->read_mailbox_status(adapter->provider_context,
                                               &status) != 0) {
        return R1_ERROR_STATE;
    }
    if (!status.mailbox_enabled || !status.rf_put_message ||
        status.current_message != R1_ST25DVXXKC_MESSAGE_RF) {
        return R1_OK;
    }

    uint8_t encoded_length = 0u;
    if (adapter->provider->read_mailbox_length(adapter->provider_context,
                                               &encoded_length) != 0) {
        return R1_ERROR_STATE;
    }
    const size_t frame_length = (size_t)encoded_length + 1u;
    if (!r1_st25dvxxkc_mailbox_length_allowed(frame_length)) {
        ++adapter->rejected_lengths;
        return R1_ERROR_LENGTH;
    }

    clear_bytes(adapter->mailbox, sizeof adapter->mailbox);
    if (adapter->provider->read_mailbox(adapter->provider_context, 0u,
                                       adapter->mailbox, frame_length) != 0) {
        return R1_ERROR_STATE;
    }
    ++adapter->accepted_frames;
    *received = true;
    if (adapter->frame_callback != NULL) {
        adapter->frame_callback(adapter->frame_context, adapter->mailbox,
                                frame_length);
    }
    return R1_OK;
}
