#include "openr1/r1_peer_target.h"

#include "openr1/r1_crc.h"

static bool address_equals(const uint8_t left[R1_PEER_ADDRESS_SIZE],
                           const uint8_t right[R1_PEER_ADDRESS_SIZE]) {
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        if (left[index] != right[index]) {
            return false;
        }
    }
    return true;
}

bool r1_peer_target_address_valid(
    const uint8_t address[R1_PEER_ADDRESS_SIZE]) {
    if (address == NULL) {
        return false;
    }
    bool all_zero = true;
    bool all_erased = true;
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        all_zero = all_zero && address[index] == UINT8_C(0);
        all_erased = all_erased && address[index] == UINT8_MAX;
    }
    return !all_zero && !all_erased;
}

bool r1_peer_address_from_slots(
    const uint8_t *slots, size_t slot_count, uint16_t connection,
    uint8_t address[R1_PEER_ADDRESS_SIZE]) {
    if (slots == NULL || address == NULL ||
        connection >= R1_PEER_SLOT_COUNT || (size_t)connection >= slot_count) {
        return false;
    }
    const size_t base = (size_t)connection * R1_PEER_SLOT_SIZE + 1u;
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        address[index] = slots[base + index];
    }
    return true;
}

bool r1_peer_is_target_glasses(
    bool peer_available, const uint8_t peer[R1_PEER_ADDRESS_SIZE],
    const uint8_t right_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t left_target[R1_PEER_ADDRESS_SIZE]) {
    const bool right_valid = r1_peer_target_address_valid(right_target);
    const bool left_valid = r1_peer_target_address_valid(left_target);
    if (!right_valid && !left_valid) {
        return true;
    }
    if (!peer_available || peer == NULL) {
        return true;
    }
    return (right_valid && address_equals(peer, right_target)) ||
           (left_valid && address_equals(peer, left_target));
}

r1_error r1_connection_control_plan_adv_start(
    bool glasses_connected, uint16_t glasses_connection,
    bool peer_available, const uint8_t peer_address[R1_PEER_ADDRESS_SIZE],
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE],
    bool phone_occupied, bool glasses_occupied,
    r1_connection_control_plan *plan) {
    if (first_target == NULL || second_target == NULL || plan == NULL ||
        (peer_available && peer_address == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_connection_control_plan){0};
    plan->store_targets = true;
    const bool matched = r1_peer_is_target_glasses(
        peer_available, peer_address, first_target, second_target);
    if (glasses_connected && !matched) {
        plan->schedule_disconnect = true;
        plan->disconnect_connection = glasses_connection;
        plan->disconnect_delay = R1_CONNECTION_CONTROL_DISCONNECT_DELAY;
    }
    if (!phone_occupied || !glasses_occupied) {
        plan->start_fast_advertising = true;
    } else if (matched) {
        plan->stop_advertising = true;
    }
    return R1_OK;
}

r1_error r1_connection_control_adv_start_handler_plan_decode(
    uint16_t incoming_session, uint16_t current_eus_session,
    const uint8_t *payload, size_t payload_length,
    r1_connection_control_adv_start_handler_plan *plan) {
    if (payload == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length != R1_CONNECTION_CONTROL_ADV_START_PAYLOAD_SIZE) {
        return R1_ERROR_LENGTH;
    }

    *plan = (r1_connection_control_adv_start_handler_plan){
        .send_empty_success_response = true,
        .enqueue_event = true,
        .response_session = incoming_session,
        .event_session = current_eus_session,
        .event_type = R1_CONNECTION_CONTROL_ADV_START_EVENT_TYPE,
    };
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        plan->first_target[index] = payload[index];
        plan->second_target[index] = payload[R1_PEER_ADDRESS_SIZE + index];
    }
    return R1_OK;
}

uint32_t r1_connection_control_role_sync_thread_flags(void) {
    return R1_CONNECTION_CONTROL_ROLE_SYNC_THREAD_FLAG;
}

r1_connection_control_delayed_plan r1_connection_control_delayed_event_plan(
    uint32_t callback_argument) {
    r1_connection_control_delayed_plan plan = {
        .action = R1_CONNECTION_CONTROL_DELAYED_IGNORE,
        .connection_context = (uint16_t)(callback_argument >> 16u),
        .event_type = 0u,
    };
    if (plan.connection_context == UINT16_MAX) {
        return plan;
    }

    plan.action = R1_CONNECTION_CONTROL_DELAYED_ENQUEUE;
    switch (callback_argument & R1_CONNECTION_CONTROL_EVENT_SELECTOR_MASK) {
        case 0u:
            plan.event_type = R1_CONNECTION_CONTROL_EVENT_TYPE_ZERO;
            break;
        case 1u:
            plan.event_type = R1_CONNECTION_CONTROL_EVENT_TYPE_ONE;
            break;
        case 2u:
            plan.event_type = R1_CONNECTION_CONTROL_EVENT_TYPE_TWO;
            break;
        default:
            plan.action = R1_CONNECTION_CONTROL_DELAYED_FATAL;
            break;
    }
    return plan;
}

r1_error r1_peer_target_persist(
    uint8_t *dev_info, size_t length,
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]) {
    if (dev_info == NULL || first_target == NULL || second_target == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length < R1_DEV_INFO_TARGET_SECOND_OFFSET + R1_PEER_ADDRESS_SIZE) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        dev_info[R1_DEV_INFO_TARGET_FIRST_OFFSET + index] =
            first_target[index];
        dev_info[R1_DEV_INFO_TARGET_SECOND_OFFSET + index] =
            second_target[index];
    }
    return R1_OK;
}

r1_error r1_remove_ring_clear_connected_flag(
    uint8_t *dev_info, size_t length) {
    if (dev_info == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_DEV_INFO_RECORD_BYTES) {
        return R1_ERROR_LENGTH;
    }
    dev_info[R1_DEV_INFO_CONNECTION_FLAGS_OFFSET] &=
        (uint8_t)~R1_DEV_INFO_GLASSES_CONNECTED_FLAG;
    return R1_OK;
}

r1_error r1_remove_ring_clear_peer_slots(
    uint8_t *dev_info, size_t length) {
    if (dev_info == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_DEV_INFO_RECORD_BYTES) {
        return R1_ERROR_LENGTH;
    }
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        dev_info[R1_DEV_INFO_TARGET_FIRST_OFFSET + index] = UINT8_MAX;
        dev_info[R1_DEV_INFO_TARGET_SECOND_OFFSET + index] = UINT8_MAX;
    }
    dev_info[R1_DEV_INFO_PEER_MARKER_OFFSET] = (uint8_t)'C';
    dev_info[R1_DEV_INFO_PEER_MARKER_OFFSET + 1u] = (uint8_t)'A';
    dev_info[R1_DEV_INFO_PEER_MARKER_OFFSET + 2u] = (uint8_t)'M';
    dev_info[R1_DEV_INFO_PEER_MARKER_OFFSET + 3u] = (uint8_t)'H';
    return R1_OK;
}

r1_error r1_remove_ring_metadata_commit(r1_kv_store *store) {
    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t length = 0u;
    r1_error error = r1_kv_store_get(
        store, R1_KV_DEV_INFO, dev_info, sizeof dev_info, &length);
    if (error == R1_OK) {
        error = r1_remove_ring_clear_connected_flag(dev_info, length);
    }
    if (error == R1_OK) {
        error = r1_kv_store_set(
            store, R1_KV_DEV_INFO, dev_info, length);
    }
    if (error == R1_OK) {
        error = r1_kv_store_commit(store);
    }
    if (error == R1_OK) {
        error = r1_remove_ring_clear_peer_slots(dev_info, length);
    }
    if (error == R1_OK) {
        error = r1_kv_store_set(
            store, R1_KV_DEV_INFO, dev_info, length);
    }
    if (error == R1_OK) {
        error = r1_kv_store_commit(store);
    }
    return error;
}

r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result) {
    if (peer_id == UINT16_MAX) {
        return R1_BOND_DIAGNOSTIC_INVALID_PEER;
    }
    return provider_load_result == 0
        ? R1_BOND_DIAGNOSTIC_REDACTED : R1_BOND_DIAGNOSTIC_LOAD_FAILED;
}

static void owner_store_crc(uint8_t record[R1_OWNER_AUTH_RECORD_BYTES]) {
    const uint16_t crc = r1_crc16_modbus(record, R1_OWNER_AUTH_CRC_OFFSET);
    record[R1_OWNER_AUTH_CRC_OFFSET] = (uint8_t)crc;
    record[R1_OWNER_AUTH_CRC_OFFSET + 1u] = (uint8_t)(crc >> 8u);
}

r1_error r1_owner_authorization_encode(
    uint8_t address_type, const uint8_t address[R1_PEER_ADDRESS_SIZE],
    uint8_t record[R1_OWNER_AUTH_RECORD_BYTES]) {
    if (address == NULL || record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (address_type > 1u || !r1_peer_target_address_valid(address)) {
        return R1_ERROR_STATE;
    }
    for (size_t index = 0u; index < R1_OWNER_AUTH_RECORD_BYTES; ++index) {
        record[index] = 0u;
    }
    record[0] = R1_OWNER_AUTH_MAGIC;
    record[1] = R1_OWNER_AUTH_VERSION;
    record[2] = address_type;
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        record[R1_OWNER_AUTH_ADDRESS_OFFSET + index] = address[index];
    }
    owner_store_crc(record);
    return R1_OK;
}

bool r1_owner_authorization_decode(
    const uint8_t *record, size_t length, uint8_t *address_type,
    uint8_t address[R1_PEER_ADDRESS_SIZE]) {
    if (record == NULL || address_type == NULL || address == NULL ||
        length != R1_OWNER_AUTH_RECORD_BYTES ||
        record[0] != R1_OWNER_AUTH_MAGIC ||
        record[1] != R1_OWNER_AUTH_VERSION || record[2] > 1u ||
        record[3] != 0u) {
        return false;
    }
    const uint16_t stored = (uint16_t)(
        (uint16_t)record[R1_OWNER_AUTH_CRC_OFFSET] |
        ((uint16_t)record[R1_OWNER_AUTH_CRC_OFFSET + 1u] << 8u));
    if (stored != r1_crc16_modbus(record, R1_OWNER_AUTH_CRC_OFFSET) ||
        !r1_peer_target_address_valid(
            &record[R1_OWNER_AUTH_ADDRESS_OFFSET])) {
        return false;
    }
    *address_type = record[2];
    for (size_t index = 0u; index < R1_PEER_ADDRESS_SIZE; ++index) {
        address[index] = record[R1_OWNER_AUTH_ADDRESS_OFFSET + index];
    }
    return true;
}

bool r1_owner_authorization_matches(
    const uint8_t *record, size_t length, uint8_t address_type,
    const uint8_t address[R1_PEER_ADDRESS_SIZE]) {
    uint8_t stored_type = 0u;
    uint8_t stored_address[R1_PEER_ADDRESS_SIZE];
    return address != NULL &&
        r1_owner_authorization_decode(
            record, length, &stored_type, stored_address) &&
        stored_type == address_type && address_equals(stored_address, address);
}

void r1_owner_authorization_state_reset(
    r1_owner_authorization_state *state) {
    if (state == NULL) {
        return;
    }
    for (size_t index = 0u; index < sizeof state->record; ++index) {
        state->record[index] = 0u;
    }
    state->loaded = false;
    state->corrupt = false;
}

bool r1_owner_authorization_state_load(
    r1_owner_authorization_state *state,
    const uint8_t *record, size_t length) {
    if (state == NULL) {
        return false;
    }
    r1_owner_authorization_state_reset(state);
    uint8_t address_type = 0u;
    uint8_t address[R1_PEER_ADDRESS_SIZE];
    if (!r1_owner_authorization_decode(
            record, length, &address_type, address)) {
        state->corrupt = true;
        return false;
    }
    for (size_t index = 0u; index < sizeof state->record; ++index) {
        state->record[index] = record[index];
    }
    state->loaded = true;
    return true;
}

bool r1_owner_authorization_state_matches(
    const r1_owner_authorization_state *state, uint8_t address_type,
    const uint8_t address[R1_PEER_ADDRESS_SIZE]) {
    return state != NULL && state->loaded && !state->corrupt &&
        r1_owner_authorization_matches(
            state->record, sizeof state->record, address_type, address);
}
