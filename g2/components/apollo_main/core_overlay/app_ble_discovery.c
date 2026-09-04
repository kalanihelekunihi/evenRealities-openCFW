/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 Cordio application discovery policy.
 * Retained diagnostic logging is intentionally omitted. The connection-role
 * split, discovery attempt progression, service ordering, and product signal
 * are preserved.
 */
#include "app_ble_discovery.h"

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_CONTEXT
#define OPEN_CFW_APP_BLE_DISCOVERY_CONTEXT() \
    (*(volatile uint8_t **)(uintptr_t)0x20074310U)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_RING_CONFIG
#define OPEN_CFW_APP_BLE_DISCOVERY_RING_CONFIG() \
    (*(const void * volatile *)(uintptr_t)0x20074318U)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG
#define OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG() \
    (*(const void * volatile *)(uintptr_t)0x2007431CU)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_GATT_CONFIG
#define OPEN_CFW_APP_BLE_DISCOVERY_GATT_CONFIG() \
    (*(const void * volatile *)(uintptr_t)0x20074320U)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH_CONFIG
#define OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH_CONFIG() \
    (*(const void * volatile *)(uintptr_t)0x20074324U)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_TASK_ID
#define OPEN_CFW_APP_BLE_DISCOVERY_TASK_ID() \
    (*(volatile uint8_t *)(uintptr_t)0x20074F8AU)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_REMOVE_DELAYED
void open_cfw_retained_event_loop_remove_delayed(void *callback);
#define OPEN_CFW_APP_BLE_DISCOVERY_REMOVE_DELAYED(callback) \
    open_cfw_retained_event_loop_remove_delayed((callback))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_CONNECTION_RECORD
void *open_cfw_retained_app_ble_connection_record(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_DISCOVERY_CONNECTION_RECORD(connection_id) \
    open_cfw_retained_app_ble_connection_record((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_RECORD_STATE_SET
void open_cfw_retained_app_ble_record_state_set(void *record, uint8_t state);
#define OPEN_CFW_APP_BLE_DISCOVERY_RECORD_STATE_SET(record, state) \
    open_cfw_retained_app_ble_record_state_set((record), (state))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_RECORD_RESET
void open_cfw_retained_app_ble_record_reset(void *record, uint8_t state);
#define OPEN_CFW_APP_BLE_DISCOVERY_RECORD_RESET(record, state) \
    open_cfw_retained_app_ble_record_reset((record), (state))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_ALLOCATE
void *open_cfw_retained_app_ble_message_allocate(uint16_t size);
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_ALLOCATE(size) \
    open_cfw_retained_app_ble_message_allocate((size))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_SEND
void open_cfw_retained_app_ble_message_send(uint8_t task_id, void *message);
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_SEND(task_id, message) \
    open_cfw_retained_app_ble_message_send((task_id), (message))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_ROLE
uint8_t open_cfw_retained_dm_conn_role(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) \
    open_cfw_retained_dm_conn_role((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_BEGIN
void open_cfw_retained_app_disc_begin(
    uint8_t connection_id, uint8_t count, volatile uint8_t *handles
);
#define OPEN_CFW_APP_BLE_DISCOVERY_BEGIN(connection_id, count, handles) \
    open_cfw_retained_app_disc_begin((connection_id), (count), (handles))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_FAIL
void open_cfw_retained_app_disc_fail(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_DISCOVERY_FAIL(connection_id) \
    open_cfw_retained_app_disc_fail((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_PHONE_READY
void open_cfw_retained_app_disc_phone_ready(uint8_t connection_id);
#define OPEN_CFW_APP_BLE_DISCOVERY_PHONE_READY(connection_id) \
    open_cfw_retained_app_disc_phone_ready((connection_id))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_CONFIGURE
void open_cfw_retained_app_disc_configure(
    uint8_t connection_id, const void *configuration
);
#define OPEN_CFW_APP_BLE_DISCOVERY_CONFIGURE(connection_id, configuration) \
    open_cfw_retained_app_disc_configure((connection_id), (configuration))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET
void open_cfw_retained_app_disc_state_set(
    uint8_t connection_id, uint8_t state
);
#define OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET(connection_id, state) \
    open_cfw_retained_app_disc_state_set((connection_id), (state))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN
void open_cfw_retained_app_disc_service_begin(
    uint8_t connection_id,
    uint8_t state,
    uint8_t service,
    const void *uuid,
    uint8_t handle_count,
    volatile uint8_t *handles
);
#define OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN( \
    connection_id, state, service, uuid, handle_count, handles \
) \
    open_cfw_retained_app_disc_service_begin( \
        (connection_id), (state), (service), (uuid), (handle_count), (handles) \
    )
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH
void open_cfw_retained_app_disc_database_hash(
    uint8_t connection_id, const void *configuration
);
#define OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH( \
    connection_id, configuration \
) \
    open_cfw_retained_app_disc_database_hash( \
        (connection_id), (configuration) \
    )
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_ANCS
int open_cfw_retained_app_disc_ancs(
    uint8_t connection_id, const void *configuration
);
#define OPEN_CFW_APP_BLE_DISCOVERY_ANCS(connection_id, configuration) \
    open_cfw_retained_app_disc_ancs((connection_id), (configuration))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_PRODUCT_SIGNAL
void open_cfw_retained_app_product_signal(uint32_t signal);
#define OPEN_CFW_APP_BLE_DISCOVERY_PRODUCT_SIGNAL(signal) \
    open_cfw_retained_app_product_signal((signal))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_REPORT_HANDLES
#define OPEN_CFW_APP_BLE_DISCOVERY_REPORT_HANDLES(handles, count) \
    ((void)(handles), (void)(count))
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_GATT_UUID
#define OPEN_CFW_APP_BLE_DISCOVERY_GATT_UUID \
    ((const void *)(uintptr_t)0x00784DC0U)
#endif

#ifndef OPEN_CFW_APP_BLE_DISCOVERY_RING_UUID
#define OPEN_CFW_APP_BLE_DISCOVERY_RING_UUID \
    ((const void *)(uintptr_t)0x0075DAF0U)
#endif

#define OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET 0x57U
#define OPEN_CFW_APP_BLE_DISCOVERY_CONFIG_FLAG_OFFSET 0x5AU
#define OPEN_CFW_APP_BLE_DISCOVERY_RING_HANDLES_OFFSET 0x2AU
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_BYTES 12U
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_EVENT_OFFSET 2U
#define OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_EVENT 0xA5U
#define OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE 0U

#if defined(OPEN_CFW_APP_BLE_DISCOVERY_START_ONLY)
#define OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR 1
#elif defined(OPEN_CFW_APP_BLE_DISCOVERY_CALLBACK_ONLY)
#define OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR 2
#elif !defined(OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR)
#define OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR 0
#endif

#define OPEN_CFW_APP_BLE_DISCOVERY_BUILD(number) \
    (OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR == 0 || \
     OPEN_CFW_APP_BLE_DISCOVERY_SELECTOR == (number))

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_app_start_service_discovery,%function\n"
    ".type open_cfw_app_ble_server_disc_callback,%function\n"
);
#endif

#if OPEN_CFW_APP_BLE_DISCOVERY_BUILD(1)
__attribute__((used, noinline))
void open_cfw_app_start_service_discovery(uint8_t connection_id)
{
    void *record;
    uint8_t *message;

    OPEN_CFW_APP_BLE_DISCOVERY_REMOVE_DELAYED(
        (void *)(uintptr_t)&open_cfw_app_start_service_discovery
    );
    record = OPEN_CFW_APP_BLE_DISCOVERY_CONNECTION_RECORD(connection_id);
    if (record != NULL) {
        OPEN_CFW_APP_BLE_DISCOVERY_RECORD_STATE_SET(record, 0U);
        OPEN_CFW_APP_BLE_DISCOVERY_RECORD_RESET(record, 0U);
    }
    message = (uint8_t *)OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_ALLOCATE(
        OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_BYTES
    );
    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_EVENT_OFFSET] =
            OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_EVENT;
        OPEN_CFW_APP_BLE_DISCOVERY_MESSAGE_SEND(
            OPEN_CFW_APP_BLE_DISCOVERY_TASK_ID(), message
        );
    }
}
#endif

#if OPEN_CFW_APP_BLE_DISCOVERY_BUILD(2)
__attribute__((used, noinline))
void open_cfw_app_ble_server_disc_callback(
    uint8_t connection_id, uint8_t state
)
{
    volatile uint8_t *context = OPEN_CFW_APP_BLE_DISCOVERY_CONTEXT();
    volatile uint8_t *ring_handles;
    uint8_t role;

    if (context == NULL) {
        return;
    }
    ring_handles = context + OPEN_CFW_APP_BLE_DISCOVERY_RING_HANDLES_OFFSET;

    switch (state) {
    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_INITIALIZE:
        role = OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id);
        context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] = 0U;
        if (role == OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            OPEN_CFW_APP_BLE_DISCOVERY_BEGIN(connection_id, 5U, context);
        } else {
            OPEN_CFW_APP_BLE_DISCOVERY_BEGIN(
                connection_id, 8U, ring_handles
            );
        }
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_FAILED:
        OPEN_CFW_APP_BLE_DISCOVERY_FAIL(connection_id);
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_PHONE_READY:
        if (OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) ==
                OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            OPEN_CFW_APP_BLE_DISCOVERY_PHONE_READY(connection_id);
        }
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_CONFIGURE:
        context[OPEN_CFW_APP_BLE_DISCOVERY_CONFIG_FLAG_OFFSET] = 0U;
        context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] = 0U;
        if (OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) ==
                OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            OPEN_CFW_APP_BLE_DISCOVERY_CONFIGURE(
                connection_id, OPEN_CFW_APP_BLE_DISCOVERY_GATT_CONFIG()
            );
        } else {
            OPEN_CFW_APP_BLE_DISCOVERY_CONFIGURE(
                connection_id, OPEN_CFW_APP_BLE_DISCOVERY_RING_CONFIG()
            );
        }
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_PHASE_COMPLETE:
        role = OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id);
        if (role != OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE &&
                context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] == 1U) {
            context[OPEN_CFW_APP_BLE_DISCOVERY_CONFIG_FLAG_OFFSET] = 0U;
        }
        ++context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET];
        if (role == OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            if (context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] == 1U) {
                OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH(
                    connection_id,
                    OPEN_CFW_APP_BLE_DISCOVERY_DATABASE_HASH_CONFIG()
                );
            } else if (
                context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] == 2U
            ) {
                OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET(connection_id, 4U);
                OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN(
                    connection_id, 6U, 2U,
                    OPEN_CFW_APP_BLE_DISCOVERY_GATT_UUID,
                    5U, context
                );
            }
        } else {
            if (context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] == 1U &&
                    OPEN_CFW_APP_BLE_DISCOVERY_ANCS(
                        connection_id,
                        OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG()
                    ) == 0) {
                ++context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET];
            }
            if (context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] == 2U) {
                OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET(connection_id, 4U);
                OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN(
                    connection_id, 6U, 4U,
                    OPEN_CFW_APP_BLE_DISCOVERY_RING_UUID,
                    8U, ring_handles
                );
            }
        }
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_PHASE_FAILED:
        context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] =
            (uint8_t)(
                context[OPEN_CFW_APP_BLE_DISCOVERY_ATTEMPT_OFFSET] + 2U
            );
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_SERVICE:
        if (OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) ==
                OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN(
                connection_id, 6U, 2U,
                OPEN_CFW_APP_BLE_DISCOVERY_GATT_UUID,
                5U, context
            );
        } else {
            OPEN_CFW_APP_BLE_DISCOVERY_SERVICE_BEGIN(
                connection_id, 6U, 4U,
                OPEN_CFW_APP_BLE_DISCOVERY_RING_UUID,
                8U, ring_handles
            );
        }
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_DIAGNOSTIC:
        break;

    case OPEN_CFW_APP_BLE_DISCOVERY_STATE_COMPLETE:
        OPEN_CFW_APP_BLE_DISCOVERY_STATE_SET(connection_id, 8U);
        if (OPEN_CFW_APP_BLE_DISCOVERY_ROLE(connection_id) ==
                OPEN_CFW_APP_BLE_DISCOVERY_ROLE_PHONE) {
            OPEN_CFW_APP_BLE_DISCOVERY_PRODUCT_SIGNAL(4U);
        } else if (OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG() != NULL) {
            OPEN_CFW_APP_BLE_DISCOVERY_REPORT_HANDLES(
                OPEN_CFW_APP_BLE_DISCOVERY_ANCS_CONFIG(), 5U
            );
        }
        break;

    default:
        break;
    }
}
#endif
