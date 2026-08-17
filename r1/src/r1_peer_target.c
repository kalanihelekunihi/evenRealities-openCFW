#include "openr1/r1_peer_target.h"

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

r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result) {
    if (peer_id == UINT16_MAX) {
        return R1_BOND_DIAGNOSTIC_INVALID_PEER;
    }
    return provider_load_result == 0
        ? R1_BOND_DIAGNOSTIC_REDACTED : R1_BOND_DIAGNOSTIC_LOAD_FAILED;
}
