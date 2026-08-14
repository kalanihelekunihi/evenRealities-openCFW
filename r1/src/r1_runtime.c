#include "openr1/r1_runtime.h"

static r1_runtime_link *find_link(r1_runtime *runtime, uint16_t connection) {
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        if (runtime->links[index].active &&
            runtime->links[index].connection == connection) {
            return &runtime->links[index];
        }
    }
    return NULL;
}

r1_bae8_event_plan r1_runtime_plan_bae8_event(uint8_t event_type) {
    r1_bae8_event_plan plan = {R1_BAE8_EVENT_IGNORE, false, false};
    switch (event_type) {
        case 2u:
            plan.route = R1_BAE8_EVENT_BC_RX;
            break;
        case 3u:
            plan.route = R1_BAE8_EVENT_EUS_RX;
            break;
        case 6u:
        case 7u:
            plan.route = R1_BAE8_EVENT_LINK_GROUP_A;
            plan.assign_glasses_role = true;
            plan.requires_link_context = true;
            break;
        case 8u:
        case 9u:
            plan.route = R1_BAE8_EVENT_LINK_GROUP_B;
            plan.requires_link_context = true;
            break;
        default:
            break;
    }
    return plan;
}

r1_error r1_bae8_plan_hvx_result(
    bool serialized_path, bool credit_acquired, r1_tx_status status,
    uint8_t completed_retries, r1_bae8_hvx_retry_plan *plan) {
    if (plan == NULL || status > R1_TX_DROP) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_bae8_hvx_retry_plan){0};
    plan->release_credit = credit_acquired && status != R1_TX_SENT;
    plan->retry_once = serialized_path && credit_acquired &&
        status == R1_TX_RESOURCES && completed_retries == 0u;
    plan->retry_delay_ticks = plan->retry_once
        ? R1_EUS_RESOURCE_RETRY_TICKS : 0u;
    return R1_OK;
}

static void runtime_write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static r1_error runtime_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    if (output == NULL || allocation_bytes == NULL ||
        (payload_length != 0u && payload == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length > SIZE_MAX - 15u || payload_length > UINT32_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t required = (payload_length + 15u) & ~(size_t)3u;
    if (output_capacity < required) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t index = 0u; index < required; ++index) {
        output[index] = 0u;
    }
    runtime_write_u32(output, message_type);
    runtime_write_u32(output + 4u, context);
    runtime_write_u32(output + 8u, (uint32_t)payload_length);
    for (size_t index = 0u; index < payload_length; ++index) {
        output[R1_BLE_THREAD_MESSAGE_HEADER_BYTES + index] = payload[index];
    }
    *allocation_bytes = required;
    return R1_OK;
}

r1_error r1_ble_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    return runtime_thread_message_encode(
        message_type, context, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_factory_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    return runtime_thread_message_encode(
        message_type, context, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_peripheral_watchdog_plan_step(
    uint8_t previous_counter, uint32_t peripheral_connection_count,
    bool right_handle_valid, bool left_handle_valid,
    int advertising_stop_result, int advertising_start_result,
    r1_peripheral_watchdog_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_peripheral_watchdog_plan){
        .next_counter = previous_counter == UINT8_C(0xfe)
                            ? 0u
                            : (uint8_t)(previous_counter + 1u),
        .report_link_count =
            (previous_counter % R1_PERIPHERAL_WATCHDOG_LOG_PERIOD) == 0u,
        .schedule_next_check = true,
        .advertising_mode = R1_ADVERTISING_MODE_DIRECTED_OR_FAST,
        .next_delay_ticks = R1_PERIPHERAL_WATCHDOG_DELAY_TICKS,
    };
    if (peripheral_connection_count > 1u) {
        return R1_OK;
    }
    if (right_handle_valid && left_handle_valid) {
        plan->connection_invariant_violation = true;
        plan->schedule_next_check = false;
        return R1_OK;
    }
    if (advertising_stop_result == 0) {
        plan->cancel_pending_restart = true;
        plan->start_advertising = true;
        plan->report_advertising_start_failure =
            advertising_start_result != 0;
    }
    return R1_OK;
}

r1_error r1_glasses_status_plan_command(
    bool command_valid, uint8_t status_bits, bool previous_worn,
    bool previous_secondary_mode, bool dcdc_policy_enabled,
    r1_glasses_status_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_glasses_status_plan){.response_length = 7u};
    if (!command_valid) {
        return R1_OK;
    }
    const bool worn = (status_bits & UINT8_C(0x80)) != 0u;
    const bool secondary = (status_bits & UINT8_C(0x40)) != 0u;
    plan->wear_changed = worn != previous_worn;
    plan->secondary_mode_changed = secondary != previous_secondary_mode;
    if (plan->wear_changed) {
        plan->cancel_slow_event = true;
        if (worn) {
            plan->open_touch = true;
            if (!dcdc_policy_enabled) {
                plan->cancel_dcdc_event = true;
                plan->disable_dcdc_now = true;
            }
        } else {
            plan->schedule_slow_event = true;
            plan->slow_delay_ticks = R1_GLASSES_SLOW_DELAY_TICKS;
            if (!dcdc_policy_enabled) {
                plan->cancel_dcdc_event = true;
                plan->schedule_dcdc_enable = true;
                plan->dcdc_delay_ticks = R1_GLASSES_DCDC_DELAY_TICKS;
            }
        }
    }
    if (plan->secondary_mode_changed) {
        plan->set_touch_fast_mode = secondary;
        plan->set_ble_slow_mode = !secondary;
    }
    return R1_OK;
}

void r1_runtime_initialize(r1_runtime *runtime,
                           r1_runtime_transmit_fn transmit,
                           void *transmit_context) {
    if (runtime == NULL) {
        return;
    }
    r1_state_initialize(&runtime->device);
    r1_battery_controller_initialize(
        &runtime->battery, 0u, runtime->device.battery_percent,
        runtime->device.charge);
    r1_event_plane_initialize(&runtime->events);
    runtime->transmit = transmit;
    runtime->transmit_context = transmit_context;
    runtime->enqueue = NULL;
    runtime->enqueue_context = NULL;
    runtime->role_handler = NULL;
    runtime->role_context = NULL;
    runtime->touch_handler = NULL;
    runtime->touch_context = NULL;
    runtime->settings_handler = NULL;
    runtime->settings_context = NULL;
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        runtime->links[index].active = false;
        runtime->links[index].connection = R1_INVALID_CONNECTION;
        runtime->links[index].session.encrypted = false;
        runtime->links[index].session.bonded = false;
        runtime->links[index].session.authorized = false;
        runtime->links[index].session.role = R1_ROLE_UNASSIGNED;
        r1_reassembler_reset(&runtime->links[index].reassembler);
    }
}

void r1_runtime_configure_battery(r1_runtime *runtime, uint8_t battery_type) {
    if (runtime != NULL) {
        r1_battery_controller_set_type(&runtime->battery, battery_type);
    }
}

bool r1_runtime_update_battery(
    r1_runtime *runtime, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds) {
    if (runtime == NULL || !r1_battery_controller_update(
            &runtime->battery, charge, millivolts, elapsed_seconds)) {
        return false;
    }
    runtime->device.battery_percent = runtime->battery.percent;
    runtime->device.charge = runtime->battery.charge;
    return true;
}

r1_health_auto_sync_result r1_runtime_run_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context) {
    bool phone_connected = false;
    if (runtime != NULL) {
        for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
            if (runtime->links[index].active &&
                runtime->links[index].session.role == R1_ROLE_PHONE) {
                phone_connected = true;
                break;
            }
        }
        return r1_health_run_automatic_sync(
            &runtime->device.health, phone_connected, now_seconds,
            emit, emit_context);
    }
    return r1_health_run_automatic_sync(
        NULL, false, now_seconds, emit, emit_context);
}

void r1_runtime_set_role_handler(r1_runtime *runtime,
                                 r1_runtime_role_fn role_handler,
                                 void *role_context) {
    if (runtime != NULL) {
        runtime->role_handler = role_handler;
        runtime->role_context = role_context;
    }
}

void r1_runtime_set_touch_handler(r1_runtime *runtime,
                                  r1_runtime_touch_fn touch_handler,
                                  void *touch_context) {
    if (runtime != NULL) {
        runtime->touch_handler = touch_handler;
        runtime->touch_context = touch_context;
    }
}

void r1_runtime_set_settings_handler(r1_runtime *runtime,
                                     r1_runtime_settings_fn settings_handler,
                                     void *settings_context) {
    if (runtime != NULL) {
        runtime->settings_handler = settings_handler;
        runtime->settings_context = settings_context;
    }
}

void r1_runtime_set_transmit(r1_runtime *runtime,
                             r1_runtime_transmit_fn transmit,
                             void *transmit_context) {
    if (runtime != NULL) {
        runtime->transmit = transmit;
        runtime->transmit_context = transmit_context;
    }
}

void r1_runtime_set_enqueue(r1_runtime *runtime,
                            r1_runtime_enqueue_fn enqueue,
                            void *enqueue_context) {
    if (runtime != NULL) {
        runtime->enqueue = enqueue;
        runtime->enqueue_context = enqueue_context;
    }
}

r1_error r1_runtime_connect(r1_runtime *runtime, uint16_t connection) {
    if (runtime == NULL || connection == R1_INVALID_CONNECTION) {
        return R1_ERROR_ARGUMENT;
    }
    if (find_link(runtime, connection) != NULL) {
        return R1_OK;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        r1_runtime_link *link = &runtime->links[index];
        if (!link->active) {
            link->active = true;
            link->connection = connection;
            link->session.encrypted = false;
            link->session.bonded = false;
            link->session.authorized = false;
            link->session.role = R1_ROLE_UNASSIGNED;
            r1_reassembler_reset(&link->reassembler);
            return R1_OK;
        }
    }
    return R1_ERROR_CAPACITY;
}

void r1_runtime_disconnect(r1_runtime *runtime, uint16_t connection) {
    if (runtime == NULL) {
        return;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link != NULL) {
        link->active = false;
        link->connection = R1_INVALID_CONNECTION;
        link->session.encrypted = false;
        link->session.bonded = false;
        link->session.authorized = false;
        link->session.role = R1_ROLE_UNASSIGNED;
        r1_reassembler_reset(&link->reassembler);
    }
    r1_event_remove_connection(&runtime->events, connection);
}

r1_error r1_runtime_set_security(r1_runtime *runtime, uint16_t connection,
                                 bool encrypted, bool bonded, bool authorized) {
    if (runtime == NULL || (authorized && (!encrypted || !bonded))) {
        return R1_ERROR_ARGUMENT;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link == NULL) {
        return R1_ERROR_STATE;
    }
    link->session.encrypted = encrypted;
    link->session.bonded = bonded;
    link->session.authorized = authorized;
    return R1_OK;
}

r1_peer_role r1_runtime_connection_role(const r1_runtime *runtime,
                                        uint16_t connection) {
    if (runtime == NULL) {
        return R1_ROLE_UNASSIGNED;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        if (runtime->links[index].active &&
            runtime->links[index].connection == connection) {
            return runtime->links[index].session.role;
        }
    }
    return R1_ROLE_UNASSIGNED;
}

void r1_runtime_role_occupancy(const r1_runtime *runtime,
                               bool *phone_occupied, bool *glasses_occupied) {
    if (phone_occupied != NULL) {
        *phone_occupied = false;
    }
    if (glasses_occupied != NULL) {
        *glasses_occupied = false;
    }
    if (runtime == NULL) {
        return;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        const r1_runtime_link *link = &runtime->links[index];
        if (!link->active) {
            continue;
        }
        if (link->session.role == R1_ROLE_PHONE && phone_occupied != NULL) {
            *phone_occupied = true;
        }
        if (link->session.role == R1_ROLE_GLASSES && glasses_occupied != NULL) {
            *glasses_occupied = true;
        }
    }
}

static size_t fragment_count(size_t logical_length) {
    return logical_length / R1_FRAGMENT_PAYLOAD_MAX + 1u;
}

static r1_error commit_role_change(r1_runtime *runtime, r1_runtime_link *link,
                                   r1_peer_role previous_role) {
    if (link->session.role == previous_role) {
        return R1_OK;
    }
    if (previous_role != R1_ROLE_UNASSIGNED ||
        link->session.role == R1_ROLE_UNASSIGNED) {
        link->session.role = previous_role;
        return R1_ERROR_STATE;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        const r1_runtime_link *other = &runtime->links[index];
        if (other != link && other->active &&
            other->session.role == link->session.role) {
            link->session.role = previous_role;
            return R1_ERROR_STATE;
        }
    }
    if (runtime->role_handler != NULL) {
        const r1_error error = runtime->role_handler(
            runtime->role_context, link->connection, link->session.role);
        if (error != R1_OK) {
            link->session.role = previous_role;
            return error;
        }
    }
    return R1_OK;
}

static r1_error enqueue_dispatch(r1_runtime *runtime, uint16_t connection) {
    size_t required = 0u;
    for (size_t index = 0u; index < runtime->dispatch_scratch.count; ++index) {
        required += fragment_count(runtime->dispatch_scratch.lengths[index]);
    }
    if (required > runtime->events.eus.capacity - runtime->events.eus.count) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t response = 0u; response < runtime->dispatch_scratch.count; ++response) {
        r1_error error = r1_fragment_message(
            runtime->dispatch_scratch.models[response],
            runtime->dispatch_scratch.lengths[response],
            &runtime->fragment_scratch);
        if (error != R1_OK) {
            return error;
        }
        for (size_t index = 0u; index < runtime->fragment_scratch.count; ++index) {
            const r1_fragment *fragment = &runtime->fragment_scratch.fragments[index];
            r1_tx_event event = {0};
            event.connection = connection;
            event.channel = 2u;
            event.length = fragment->length;
            for (size_t byte = 0u; byte < fragment->length; ++byte) {
                event.bytes[byte] = fragment->bytes[byte];
            }
            error = runtime->enqueue == NULL
                ? r1_event_enqueue(&runtime->events, true, &event)
                : runtime->enqueue(runtime->enqueue_context, true, &event,
                                   R1_TX_ENQUEUE_WAIT_TICKS);
            if (error != R1_OK) {
                return error;
            }
        }
    }
    return R1_OK;
}

r1_error r1_runtime_receive_eus(r1_runtime *runtime, uint16_t connection,
                                const uint8_t *value, size_t length) {
    if (runtime == NULL || value == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link == NULL) {
        return R1_ERROR_STATE;
    }
    r1_error error = R1_OK;
    const r1_reassembly_status status = r1_reassembler_feed(
        &link->reassembler, value, length, &error);
    if (status == R1_REASSEMBLY_WAITING) {
        return R1_OK;
    }
    if (status == R1_REASSEMBLY_REJECTED) {
        return error;
    }

    r1_model request;
    error = r1_model_decode(link->reassembler.bytes, link->reassembler.length,
                            R1_CHECKSUM_PHONE_COMPACT_CCITT, &request);
    if (error != R1_OK) {
        return error;
    }
    const r1_peer_role previous_role = link->session.role;
    const bool previous_touch_enabled = runtime->device.touch_enabled;
    uint8_t previous_settings[R1_SYSTEM_SETTINGS_BYTES];
    for (size_t index = 0u; index < R1_SYSTEM_SETTINGS_BYTES; ++index) {
        previous_settings[index] = runtime->device.system_settings[index];
    }
    const r1_error dispatch_error = r1_dispatch(
        &runtime->device, &link->session, &request, &runtime->dispatch_scratch);
    const r1_error role_error = commit_role_change(runtime, link, previous_role);
    if (runtime->touch_handler != NULL &&
        runtime->device.touch_enabled != previous_touch_enabled) {
        runtime->touch_handler(
            runtime->touch_context, runtime->device.touch_enabled);
    }
    if (runtime->settings_handler != NULL) {
        bool settings_changed = false;
        for (size_t index = 0u; index < R1_SYSTEM_SETTINGS_BYTES; ++index) {
            settings_changed = settings_changed ||
                runtime->device.system_settings[index] !=
                    previous_settings[index];
        }
        if (settings_changed) {
            runtime->settings_handler(
                runtime->settings_context, runtime->device.system_settings);
        }
    }
    error = enqueue_dispatch(runtime, connection);
    if (error != R1_OK) {
        return error;
    }
    return role_error != R1_OK ? role_error : dispatch_error;
}

void r1_runtime_hvn_complete(r1_runtime *runtime, uint8_t completed) {
    if (runtime != NULL) {
        r1_event_complete(&runtime->events, completed);
    }
}

static bool tick_reached(uint32_t now_tick, uint32_t deadline_tick) {
    return now_tick - deadline_tick < UINT32_C(0x80000000);
}

static uint32_t ticks_until(uint32_t now_tick, uint32_t deadline_tick) {
    return tick_reached(now_tick, deadline_tick) ? 0u : deadline_tick - now_tick;
}

uint32_t r1_runtime_poll(r1_runtime *runtime, uint32_t now_tick) {
    if (runtime == NULL || runtime->transmit == NULL) {
        return R1_RUNTIME_WAIT_FOREVER;
    }
    r1_tx_event *event;
    while ((event = r1_event_front(&runtime->events, true)) != NULL) {
        if (event->resource_retry_pending) {
            const uint32_t remaining = ticks_until(now_tick, event->deadline_tick);
            if (remaining != 0u) {
                return remaining;
            }
            event->resource_retry_pending = false;
        }
        if (runtime->events.hvn_credits == 0u) {
            if (!event->credit_wait_started) {
                event->credit_wait_started = true;
                event->deadline_tick = now_tick + R1_EUS_CREDIT_WAIT_TICKS;
            }
            const uint32_t remaining = ticks_until(now_tick, event->deadline_tick);
            if (remaining != 0u) {
                return remaining;
            }
            (void)r1_event_drop(&runtime->events, true);
            continue;
        }
        event->credit_wait_started = false;
        const r1_tx_status status = runtime->transmit(runtime->transmit_context, event);
        if (status == R1_TX_RESOURCES) {
            if (event->resource_retries == 0u) {
                event->resource_retries = 1u;
                event->resource_retry_pending = true;
                event->deadline_tick = now_tick + R1_EUS_RESOURCE_RETRY_TICKS;
                return R1_EUS_RESOURCE_RETRY_TICKS;
            }
            (void)r1_event_drop(&runtime->events, true);
            continue;
        }
        (void)r1_event_drop(&runtime->events, true);
        if (status == R1_TX_SENT) {
            (void)r1_event_consume_credit(&runtime->events);
        }
    }
    return R1_RUNTIME_WAIT_FOREVER;
}
