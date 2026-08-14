#ifndef OPENR1_R1_PEER_TARGET_H
#define OPENR1_R1_PEER_TARGET_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_PEER_ADDRESS_SIZE 6u
#define R1_PEER_SLOT_SIZE 7u
#define R1_PEER_SLOT_COUNT 3u

/* Recovered persistence site of the two advStart target addresses in the
 * kv.bin `dev_info` payload (R1-191, CONNECTION-CONTROL-CORRELATION.md):
 * the first target at offset 8 and the second at offset 14. */
#define R1_DEV_INFO_TARGET_FIRST_OFFSET 8u
#define R1_DEV_INFO_TARGET_SECOND_OFFSET 14u
/* Recovered raw delayed-disconnect delay for a connected glasses peer that
 * matches neither target.  The delayed-event runtime treats the value as
 * raw 1024 Hz ticks, not milliseconds. */
#define R1_CONNECTION_CONTROL_DISCONNECT_DELAY UINT32_C(0x5000)

/* Composition of the recovered advStart event-0x200 consumer policy.  The
 * externally callable advStart command stays refused in the normal
 * dispatcher; this plan exists so the composition behind that refusal is
 * bound and host-tested. */
typedef struct {
    /* Both targets are always stored, even after a peer mismatch. */
    bool store_targets;
    /* A connected glasses peer matching neither valid target is
     * disconnected after R1_CONNECTION_CONTROL_DISCONNECT_DELAY. */
    bool schedule_disconnect;
    uint16_t disconnect_connection;
    uint32_t disconnect_delay;
    /* Fast advertising while either the phone or glasses role is
     * unoccupied; stop once both roles are occupied and the connected
     * glasses peer matched.  A both-occupied mismatch requests neither:
     * the scheduled disconnect frees the role first. */
    bool start_fast_advertising;
    bool stop_advertising;
} r1_connection_control_plan;

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
/* Composes the recovered advStart consumer policy over the existing target
 * validity and match helpers: store both targets, schedule the delayed
 * disconnect for a mismatching connected glasses peer, and choose the
 * role-aware advertising action.  peer_address may be NULL when
 * peer_available is false; an unavailable lookup is accepted as a match,
 * mirroring the recovered behavior. */
r1_error r1_connection_control_plan_adv_start(
    bool glasses_connected, uint16_t glasses_connection,
    bool peer_available, const uint8_t peer_address[R1_PEER_ADDRESS_SIZE],
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE],
    bool phone_occupied, bool glasses_occupied,
    r1_connection_control_plan *plan);
/* Writes both targets into a kv.bin `dev_info` payload image at the
 * recovered offsets 8 and 14 without touching any other byte. */
r1_error r1_peer_target_persist(
    uint8_t *dev_info, size_t length,
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]);
r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result);

#endif
