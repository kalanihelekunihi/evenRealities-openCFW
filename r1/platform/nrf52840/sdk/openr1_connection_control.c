#include "openr1_connection_control.h"

#include <stdbool.h>
#include <stddef.h>

#include "ble.h"
#include "ble_hci.h"
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
 * connection handle travels as the event context.  The timer driver below
 * steps the portable state from a CMSIS one-shot timer and fires the due
 * disconnect through sd_ble_gap_disconnect. */
#define OPENR1_CONNECTION_CONTROL_EVENT_DISCONNECT UINT32_C(0x01)

extern r1_runtime *openr1_platform_runtime(void);

static uint32_t last_error;
static r1_delayed_event_state delayed_events;
static osTimerId_t delayed_event_timer;
static osMutexId_t delayed_event_mutex;

/* Milliseconds to kernel ticks at the recovered 1,024-Hz tick rate
 * (osKernelGetTickFreq), rounding up and never returning zero so a short
 * delay still arms a real one-shot timer. */
static uint32_t delayed_event_ticks(uint32_t milliseconds) {
    const uint64_t ticks =
        ((uint64_t)milliseconds * osKernelGetTickFreq() + 999u) / 1000u;
    if (ticks == 0u) {
        return 1u;
    }
    return ticks > UINT32_MAX ? UINT32_MAX : (uint32_t)ticks;
}

static void delayed_event_fire_disconnect(uint16_t connection) {
    /* Bounded action for a fired disconnect event.  An already-closed link
     * is the desired end state and is tolerated; every other failure is
     * recorded. */
    const uint32_t error = sd_ble_gap_disconnect(
        connection, BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
    if (error != NRF_SUCCESS && error != BLE_ERROR_INVALID_CONN_HANDLE) {
        last_error = error;
    }
}

/* One-shot timer callback (timer daemon thread): steps the portable state
 * with callback argument zero so the elapsed time is the previously
 * programmed delay, fires due disconnect events, and rearms the timer for
 * the minimum remaining delay.  The stock empty-table reload of a
 * UINT32_MAX-millisecond timer is suppressed: it carries no event and only
 * suppresses one redundant callback, which this driver never needs. */
static void delayed_event_timeout(void *argument) {
    (void)argument;
    if (delayed_event_mutex == NULL ||
        osMutexAcquire(delayed_event_mutex, osWaitForever) != osOK) {
        last_error = NRF_ERROR_INVALID_STATE;
        return;
    }
    r1_delayed_event_step_result result;
    if (r1_delayed_event_timer_step(
            &delayed_events, 0u, (uint32_t)osKernelGetTickCount(),
            &result) != R1_OK) {
        last_error = NRF_ERROR_INTERNAL;
    } else {
        for (size_t index = 0u; index < result.due_count; ++index) {
            if (result.due[index].event ==
                OPENR1_CONNECTION_CONTROL_EVENT_DISCONNECT) {
                delayed_event_fire_disconnect(
                    (uint16_t)result.due[index].context);
            } else {
                /* This module owns the only scheduled event tag. */
                last_error = NRF_ERROR_NOT_FOUND;
            }
        }
        if (result.timer_start_requested &&
            !result.stock_empty_reload_quirk &&
            result.next_delay_milliseconds != 0u &&
            osTimerStart(
                delayed_event_timer,
                delayed_event_ticks(
                    result.next_delay_milliseconds)) != osOK) {
            last_error = NRF_ERROR_INTERNAL;
        }
    }
    (void)osMutexRelease(delayed_event_mutex);
}

static uint32_t delayed_event_ensure_driver(void) {
    if (delayed_event_timer != NULL && delayed_event_mutex != NULL) {
        return NRF_SUCCESS;
    }
    if (delayed_event_mutex == NULL) {
        delayed_event_mutex = osMutexNew(NULL);
    }
    if (delayed_event_timer == NULL) {
        delayed_event_timer = osTimerNew(
            delayed_event_timeout, osTimerOnce, NULL, NULL);
    }
    return delayed_event_timer != NULL && delayed_event_mutex != NULL
        ? NRF_SUCCESS : NRF_ERROR_NO_MEM;
}

/* Schedules the recovered raw 0x5000 delayed disconnect and arms the
 * one-shot timer.  The raw delay is passed through in the scheduler's
 * tick-derived millisecond unit; physical timing stays an owned-hardware
 * gate.  A full table or driver failure is recorded but tolerated,
 * matching the stock response-before-effect ordering. */
static void schedule_delayed_disconnect(
    uint16_t connection, uint32_t delay_milliseconds) {
    uint32_t error = delayed_event_ensure_driver();
    if (error == NRF_SUCCESS &&
        osMutexAcquire(delayed_event_mutex, osWaitForever) != osOK) {
        error = NRF_ERROR_INVALID_STATE;
    }
    if (error != NRF_SUCCESS) {
        last_error = error;
        return;
    }
    r1_delayed_event_schedule_result schedule;
    const r1_error scheduled = r1_delayed_event_schedule(
        &delayed_events, OPENR1_CONNECTION_CONTROL_EVENT_DISCONNECT,
        connection, delay_milliseconds,
        (uint32_t)osKernelGetTickCount(), &schedule);
    if (scheduled == R1_OK &&
        schedule.action == R1_DELAYED_EVENT_SCHEDULED &&
        schedule.timer_step.timer_start_requested &&
        osTimerStart(
            delayed_event_timer,
            delayed_event_ticks(
                schedule.timer_step.next_delay_milliseconds)) != osOK) {
        last_error = NRF_ERROR_INTERNAL;
    } else if (scheduled == R1_OK &&
               schedule.action == R1_DELAYED_EVENT_IMMEDIATE) {
        /* Sub-two-millisecond delays fire at once (the recovered raw
         * 0x5000 delay never takes this path). */
        delayed_event_fire_disconnect(connection);
    } else if (scheduled != R1_OK) {
        last_error = NRF_ERROR_NO_MEM;
    }
    (void)osMutexRelease(delayed_event_mutex);
}

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
        schedule_delayed_disconnect(
            plan.disconnect_connection, plan.disconnect_delay);
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
