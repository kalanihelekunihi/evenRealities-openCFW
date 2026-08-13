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

r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result) {
    if (peer_id == UINT16_MAX) {
        return R1_BOND_DIAGNOSTIC_INVALID_PEER;
    }
    return provider_load_result == 0
        ? R1_BOND_DIAGNOSTIC_REDACTED : R1_BOND_DIAGNOSTIC_LOAD_FAILED;
}
