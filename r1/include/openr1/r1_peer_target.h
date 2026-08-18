#ifndef OPENR1_R1_PEER_TARGET_H
#define OPENR1_R1_PEER_TARGET_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_kv_store.h"
#include "openr1/r1_protocol.h"

#define R1_PEER_ADDRESS_SIZE 6u
#define R1_PEER_SLOT_SIZE 7u
#define R1_PEER_SLOT_COUNT 3u
#define R1_OWNER_AUTH_RECORD_BYTES 12u
#define R1_OWNER_AUTH_ADDRESS_OFFSET 4u
#define R1_OWNER_AUTH_CRC_OFFSET 10u
#define R1_OWNER_AUTH_MAGIC UINT8_C(0xa1)
#define R1_OWNER_AUTH_VERSION UINT8_C(1)

typedef struct {
    uint8_t record[R1_OWNER_AUTH_RECORD_BYTES];
    bool loaded;
    bool corrupt;
} r1_owner_authorization_state;

/* Recovered persistence site of the two advStart target addresses in the
 * kv.bin `dev_info` payload (R1-191, CONNECTION-CONTROL-CORRELATION.md):
 * the first target at offset 8 and the second at offset 14. */
#define R1_DEV_INFO_TARGET_FIRST_OFFSET 8u
#define R1_DEV_INFO_TARGET_SECOND_OFFSET 14u
#define R1_DEV_INFO_PEER_MARKER_OFFSET 20u
#define R1_DEV_INFO_CONNECTION_FLAGS_OFFSET 24u
#define R1_DEV_INFO_GLASSES_CONNECTED_FLAG UINT8_C(0x04)
#define R1_DEV_INFO_RECORD_BYTES 52u
/* Recovered raw delayed-disconnect delay for a connected glasses peer that
 * matches neither target.  The delayed-event runtime treats the value as
 * raw 1024 Hz ticks, not milliseconds. */
#define R1_CONNECTION_CONTROL_DISCONNECT_DELAY UINT32_C(0x5000)
#define R1_CONNECTION_CONTROL_ROLE_SYNC_THREAD_FLAG UINT32_C(0x100)
#define R1_CONNECTION_CONTROL_EVENT_SELECTOR_MASK UINT32_C(0xff)
#define R1_CONNECTION_CONTROL_EVENT_TYPE_ZERO UINT32_C(0x40)
#define R1_CONNECTION_CONTROL_EVENT_TYPE_ONE UINT32_C(0x10)
#define R1_CONNECTION_CONTROL_EVENT_TYPE_TWO UINT32_C(0x20)
#define R1_CONNECTION_CONTROL_ADV_START_EVENT_TYPE UINT32_C(0x200)
#define R1_CONNECTION_CONTROL_ADV_START_PAYLOAD_SIZE \
    (2u * R1_PEER_ADDRESS_SIZE)

/* Side-effect-free, hardened form of the recovered advStart handler at
 * 0x00083D04.  The stock handler replies on the incoming session before it
 * attempts to enqueue event 0x200 on the current EUS session. */
typedef struct {
    bool send_empty_success_response;
    bool enqueue_event;
    uint16_t response_session;
    uint16_t event_session;
    uint32_t event_type;
    uint8_t first_target[R1_PEER_ADDRESS_SIZE];
    uint8_t second_target[R1_PEER_ADDRESS_SIZE];
} r1_connection_control_adv_start_handler_plan;

/* Composition of the recovered advStart event-0x200 consumer policy.  The
 * normal dispatcher exposes it only to an encrypted, bonded,
 * owner-authorized phone role with an exact 12-byte SET payload. */
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
    R1_CONNECTION_CONTROL_DELAYED_IGNORE = 0,
    R1_CONNECTION_CONTROL_DELAYED_ENQUEUE,
    R1_CONNECTION_CONTROL_DELAYED_FATAL
} r1_connection_control_delayed_action;

typedef struct {
    r1_connection_control_delayed_action action;
    uint16_t connection_context;
    uint32_t event_type;
} r1_connection_control_delayed_plan;

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
/* Accepts exactly the legitimate 12-byte payload.  It deliberately rejects
 * the stock unsigned-wrap malformed declarations and trailing ambiguity;
 * no response, allocation, queue, BLE, or persistence effect is performed. */
r1_error r1_connection_control_adv_start_handler_plan_decode(
    uint16_t incoming_session, uint16_t current_eus_session,
    const uint8_t *payload, size_t payload_length,
    r1_connection_control_adv_start_handler_plan *plan);
/* Delayed role-sync callback 0x0004E008 logs both role handles and sets this
 * one worker flag.  Logging is deliberately outside the pure contract. */
uint32_t r1_connection_control_role_sync_thread_flags(void);
/* Pure form of recovered delayed callback 0x000882AC. The callback argument
 * packs a 16-bit connection/context in the high half and an 8-bit selector in
 * the low byte. A 0xFFFF context is a cancelled/no-link sentinel. */
r1_connection_control_delayed_plan r1_connection_control_delayed_event_plan(
    uint32_t callback_argument);
/* Writes both targets into a kv.bin `dev_info` payload image at the
 * recovered offsets 8 and 14 without touching any other byte. */
r1_error r1_peer_target_persist(
    uint8_t *dev_info, size_t length,
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]);
/* Exact two-stage removeRingNotify state changes. The caller persists the
 * first image before applying and persisting the second image. */
r1_error r1_remove_ring_clear_connected_flag(
    uint8_t *dev_info, size_t length);
r1_error r1_remove_ring_clear_peer_slots(
    uint8_t *dev_info, size_t length);
/* Executes the recovered removeRingNotify persistence order against the
 * transparent snapshot store: clear flag 0x04 and commit, then erase both
 * peer slots, restore marker CAMH, and commit again. A failure after the
 * first commit intentionally leaves that valid intermediate generation;
 * retrying this idempotent operation completes the final generation. */
r1_error r1_remove_ring_metadata_commit(r1_kv_store *store);
r1_bond_diagnostic_result r1_peer_bond_diagnostic_plan(
    uint16_t peer_id, int provider_load_result);

/* Transparent owner-authorization record used by source-built targets. The
 * first successfully persisted bonded identity becomes the owner; pairAuth
 * remains role metadata and cannot create or replace this record. */
r1_error r1_owner_authorization_encode(
    uint8_t address_type, const uint8_t address[R1_PEER_ADDRESS_SIZE],
    uint8_t record[R1_OWNER_AUTH_RECORD_BYTES]);
bool r1_owner_authorization_decode(
    const uint8_t *record, size_t length, uint8_t *address_type,
    uint8_t address[R1_PEER_ADDRESS_SIZE]);
bool r1_owner_authorization_matches(
    const uint8_t *record, size_t length, uint8_t address_type,
    const uint8_t address[R1_PEER_ADDRESS_SIZE]);
/* Stateful fail-closed wrapper used by persistent target settings. A malformed
 * reload clears any previously active RAM identity before setting `corrupt`,
 * so stale authorization cannot survive a failed settings replay. Reset is
 * reserved for a confirmed-empty fresh store or successful local revocation. */
void r1_owner_authorization_state_reset(
    r1_owner_authorization_state *state);
bool r1_owner_authorization_state_load(
    r1_owner_authorization_state *state,
    const uint8_t *record, size_t length);
bool r1_owner_authorization_state_matches(
    const r1_owner_authorization_state *state, uint8_t address_type,
    const uint8_t address[R1_PEER_ADDRESS_SIZE]);

#endif
