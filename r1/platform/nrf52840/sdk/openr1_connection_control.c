#include "openr1_connection_control.h"

#include <stdbool.h>
#include <stddef.h>

#include "cmsis_os2.h"
#include "nrf_error.h"

#include "openr1/r1_event.h"
#include "openr1/r1_kv_store.h"
#include "openr1/r1_runtime.h"
#include "openr1_advertising.h"
#include "openr1_bae8.h"
#include "openr1_databases.h"

/* Local delayed-event tag for the scheduled glasses-peer disconnect.  The
 * recovered event id is not pinned, so this module owns a nonzero tag; the
 * connection handle travels as the event context.  No timer-step driver is
 * bound yet, so the entry is recorded state, not a live timer. */
#define OPENR1_CONNECTION_CONTROL_EVENT_DISCONNECT UINT32_C(0x01)

extern r1_runtime *openr1_platform_runtime(void);

static uint32_t last_error;
static r1_delayed_event_state delayed_events;

static uint32_t persist_targets(
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]) {
    r1_kv_store *kv = openr1_databases_kv_store();
    if (kv == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t length = 0u;
    if (r1_kv_store_get(
            kv, R1_KV_DEV_INFO, dev_info, sizeof dev_info, &length) != R1_OK ||
        r1_peer_target_persist(dev_info, length, first_target,
                               second_target) != R1_OK ||
        r1_kv_store_set(kv, R1_KV_DEV_INFO, dev_info, length) != R1_OK ||
        r1_kv_store_commit(kv) != R1_OK) {
        return NRF_ERROR_INTERNAL;
    }
    return NRF_SUCCESS;
}

uint32_t openr1_connection_control_adv_start(
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]) {
    if (first_target == NULL || second_target == NULL) {
        last_error = NRF_ERROR_NULL;
        return last_error;
    }
    r1_runtime *runtime = openr1_platform_runtime();
    if (runtime == NULL) {
        last_error = NRF_ERROR_INVALID_STATE;
        return last_error;
    }

    bool glasses_connected = false;
    uint16_t glasses_connection = R1_INVALID_CONNECTION;
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        const r1_runtime_link *link = &runtime->links[index];
        if (link->active &&
            r1_runtime_connection_role(runtime, link->connection) ==
                R1_ROLE_GLASSES) {
            glasses_connected = true;
            glasses_connection = link->connection;
            break;
        }
    }
    uint8_t peer[R1_PEER_ADDRESS_SIZE] = {0u};
    /* The recovered policy accepts an unavailable lookup as a match. */
    const bool peer_available = glasses_connected &&
        openr1_bae8_peer_address(glasses_connection, peer);
    bool phone_occupied = false;
    bool glasses_occupied = false;
    r1_runtime_role_occupancy(runtime, &phone_occupied, &glasses_occupied);

    r1_connection_control_plan plan;
    if (r1_connection_control_plan_adv_start(
            glasses_connected, glasses_connection, peer_available, peer,
            first_target, second_target, phone_occupied, glasses_occupied,
            &plan) != R1_OK) {
        last_error = NRF_ERROR_INTERNAL;
        return last_error;
    }

    /* Both targets persist even after a peer mismatch (recovered order:
     * the store is unconditional once the command is accepted).  A
     * durability failure is fail-closed: no disconnect or advertising
     * action follows. */
    uint32_t error = persist_targets(first_target, second_target);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return error;
    }

    if (plan.schedule_disconnect) {
        /* The raw 0x5000 delay is passed through in the scheduler's
         * tick-derived unit; physical timing stays an owned-hardware gate.
         * A full table is recorded but tolerated, matching the stock
         * response-before-effect ordering. */
        r1_delayed_event_schedule_result schedule;
        if (r1_delayed_event_schedule(
                &delayed_events, OPENR1_CONNECTION_CONTROL_EVENT_DISCONNECT,
                plan.disconnect_connection, plan.disconnect_delay,
                (uint32_t)osKernelGetTickCount(), &schedule) != R1_OK) {
            last_error = NRF_ERROR_NO_MEM;
        }
    }

    if (plan.start_fast_advertising) {
        error = openr1_advertising_start();
    } else if (plan.stop_advertising) {
        error = openr1_advertising_stop();
    } else {
        error = NRF_SUCCESS;
    }
    if (error != NRF_SUCCESS) {
        last_error = error;
    }
    return error;
}

uint32_t openr1_connection_control_last_error(void) {
    return last_error;
}
