#ifndef OPENR1_R1_PEER_TARGET_H
#define OPENR1_R1_PEER_TARGET_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define R1_PEER_ADDRESS_SIZE 6u
#define R1_PEER_SLOT_SIZE 7u
#define R1_PEER_SLOT_COUNT 3u

typedef enum {
    R1_BOND_DIAGNOSTIC_INVALID_PEER = 0,
    R1_BOND_DIAGNOSTIC_LOAD_FAILED,
    R1_BOND_DIAGNOSTIC_REDACTED
} r1_bond_diagnostic_result;

bool r1_peer_target_address_valid(
    const uint8_t address[R1_PEER_ADDRESS_SIZE]);
bool r1_peer_address_from_slots(
    const uint8_t *slots, size_t slot_count, uint16_t connection,
    uint8_t address[R1_PEER_ADDRESS_SIZE]);
bool r1_peer_is_target_glasses(
    bool peer_available, const uint8_t peer[R1_PEER_ADDRESS_SIZE],
    const uint8_t right_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t left_target[R1_PEER_ADDRESS_SIZE]);
r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result);

#endif
