/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room production reconstruction of G2's seven-function BLE Ring
 * profile.  The implementation preserves the recovered Cordio message,
 * discovery-handle, connection-epoch, delayed-CCCD, RX, and TX ABIs.  Stock
 * EasyLogger calls are diagnostic-only and intentionally omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_RING_EVENT_ATT_READ_RESPONSE 0x05u
#define OPEN_CFW_RING_EVENT_ATT_NOTIFICATION 0x0du
#define OPEN_CFW_RING_EVENT_ATT_INDICATION 0x0eu
#define OPEN_CFW_RING_EVENT_CONNECTION_OPEN 0x27u
#define OPEN_CFW_RING_EVENT_CONNECTION_CLOSE 0x28u
#define OPEN_CFW_RING_EVENT_SEND_DATA 0xacu
#define OPEN_CFW_RING_ROLE_CENTRAL 0u
#define OPEN_CFW_RING_SERVICE_UUID_LENGTH 16u
#define OPEN_CFW_RING_HANDLE_COUNT 3u
#define OPEN_CFW_RING_TX_HANDLE_INDEX 0u
#define OPEN_CFW_RING_RX_HANDLE_INDEX 1u
#define OPEN_CFW_RING_CCC_HANDLE_INDEX 2u
#define OPEN_CFW_RING_DEFAULT_TX_HANDLE 0x10u
#define OPEN_CFW_RING_DEFAULT_RX_HANDLE 0x12u
#define OPEN_CFW_RING_DEFAULT_CCC_HANDLE 0x13u
#define OPEN_CFW_RING_CCC_ENABLE_VALUE 1u
#define OPEN_CFW_RING_MESSAGE_BYTES 12u
#define OPEN_CFW_RING_CCC_DELAY_FIRST 500u
#define OPEN_CFW_RING_CCC_DELAY_SECOND 700u
#define OPEN_CFW_RING_CCC_DELAY_FINAL 900u
#define OPEN_CFW_RING_THREAD_EVENT_CCC_READY 4u
#define OPEN_CFW_RING_THREAD_EVENT_DISCONNECTED 8u

struct open_cfw_ring_control {
    uint8_t connection_id;
    uint8_t handler_id;
    uint16_t reserved;
    uint16_t *handles;
    uint16_t connection_epoch;
};

struct open_cfw_ring_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    const uint8_t *data;
    uint16_t length;
    uint16_t handle;
};

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(struct open_cfw_ring_control) == 12u,
    "G2 Ring control-block ABI changed");
_Static_assert(offsetof(struct open_cfw_ring_control, handles) == 4u,
    "G2 Ring handle-list pointer ABI changed");
_Static_assert(offsetof(struct open_cfw_ring_control, connection_epoch) == 8u,
    "G2 Ring connection-epoch ABI changed");
_Static_assert(sizeof(struct open_cfw_ring_message) == 12u,
    "G2 Ring message ABI changed");
_Static_assert(offsetof(struct open_cfw_ring_message, data) == 4u,
    "G2 Ring message data-pointer ABI changed");
_Static_assert(offsetof(struct open_cfw_ring_message, length) == 8u,
    "G2 Ring message length ABI changed");
_Static_assert(offsetof(struct open_cfw_ring_message, handle) == 10u,
    "G2 Ring ATT handle ABI changed");
#endif

#ifndef OPEN_CFW_RING_CONTROL
#define OPEN_CFW_RING_CONTROL \
    ((volatile struct open_cfw_ring_control *)(uintptr_t)0x20074074u)
#endif
#ifndef OPEN_CFW_RING_SERVICE_UUID
#define OPEN_CFW_RING_SERVICE_UUID \
    ((const uint8_t *)(uintptr_t)0x007880b0u)
#endif
#ifndef OPEN_CFW_RING_DISCOVERY_CHARACTERISTICS
#define OPEN_CFW_RING_DISCOVERY_CHARACTERISTICS \
    ((const void *)(uintptr_t)0x200030d8u)
#endif
#ifndef OPEN_CFW_RING_CONNECTION_IN_USE
uint8_t open_cfw_retained_ring_connection_in_use(uint8_t);
#define OPEN_CFW_RING_CONNECTION_IN_USE(id) \
    open_cfw_retained_ring_connection_in_use(id)
#endif
#ifndef OPEN_CFW_RING_WRITE_REQUEST
void open_cfw_retained_ring_write_request(
    uint8_t, uint16_t, uint16_t, const uint8_t *
);
#define OPEN_CFW_RING_WRITE_REQUEST(...) \
    open_cfw_retained_ring_write_request(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_RING_DISCOVER_SERVICE
void open_cfw_retained_ring_discover_service(
    uint8_t, uint8_t, const uint8_t *, uint8_t, const void *, uint16_t *
);
#define OPEN_CFW_RING_DISCOVER_SERVICE(...) \
    open_cfw_retained_ring_discover_service(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_RING_CONNECTION_ROLE
uint8_t open_cfw_retained_ring_connection_role(uint8_t);
#define OPEN_CFW_RING_CONNECTION_ROLE(id) \
    open_cfw_retained_ring_connection_role(id)
#endif
#ifndef OPEN_CFW_RING_WRITE_COMMAND
void open_cfw_retained_ring_write_command(
    uint8_t, uint16_t, uint16_t, const uint8_t *
);
#define OPEN_CFW_RING_WRITE_COMMAND(...) \
    open_cfw_retained_ring_write_command(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_RING_REMOVE_DELAYED
uint8_t open_cfw_retained_ring_remove_delayed(void (*)(void *));
#define OPEN_CFW_RING_REMOVE_DELAYED(callback) \
    open_cfw_retained_ring_remove_delayed(callback)
#endif
#ifndef OPEN_CFW_RING_PUSH_DELAYED
void open_cfw_retained_ring_push_delayed(
    void (*)(void *), void *, uint32_t
);
#define OPEN_CFW_RING_PUSH_DELAYED(...) \
    open_cfw_retained_ring_push_delayed(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_RING_THREAD_EVENT
void open_cfw_retained_ring_thread_event(uint32_t);
#define OPEN_CFW_RING_THREAD_EVENT(event) \
    open_cfw_retained_ring_thread_event(event)
#endif
#ifndef OPEN_CFW_RING_THREAD_MESSAGE
void open_cfw_retained_ring_thread_message(const uint8_t *, uint16_t);
#define OPEN_CFW_RING_THREAD_MESSAGE(data, length) \
    open_cfw_retained_ring_thread_message((data), (length))
#endif
#ifndef OPEN_CFW_RING_WAIT_TX_READY
void open_cfw_retained_ring_wait_tx_ready(void);
#define OPEN_CFW_RING_WAIT_TX_READY() open_cfw_retained_ring_wait_tx_ready()
#endif
#ifndef OPEN_CFW_RING_TX_COMPLETE_NOTIFY
void open_cfw_retained_ring_tx_complete_notify(void);
#define OPEN_CFW_RING_TX_COMPLETE_NOTIFY() \
    open_cfw_retained_ring_tx_complete_notify()
#endif
#ifndef OPEN_CFW_RING_MESSAGE_ALLOC
void *open_cfw_retained_ring_message_alloc(uint16_t);
#define OPEN_CFW_RING_MESSAGE_ALLOC(size) \
    open_cfw_retained_ring_message_alloc(size)
#endif
#ifndef OPEN_CFW_RING_MESSAGE_SEND
void open_cfw_retained_ring_message_send(uint8_t, void *);
#define OPEN_CFW_RING_MESSAGE_SEND(handler, message) \
    open_cfw_retained_ring_message_send((handler), (message))
#endif

uint32_t open_cfw_ring_pack_ccc_epoch(
    uint8_t connection_id, uint8_t final_write, uint16_t connection_epoch
);
void open_cfw_ring_enable_ccc(void *packed_argument);
void open_cfw_ring_handler_init(uint8_t handler_id, uint16_t *handles);
void open_cfw_ring_service_discover(uint8_t connection_id, uint16_t *handles);
void open_cfw_ring_receive_data(struct open_cfw_ring_message *message);
void open_cfw_ring_process_message(
    uint32_t event_mask, struct open_cfw_ring_message *message
);
uint8_t open_cfw_ring_send_data(const uint8_t *data, uint16_t length);

#ifndef OPEN_CFW_RING_DELAY_CALLBACK
#define OPEN_CFW_RING_DELAY_CALLBACK \
    ((void (*)(void *))(uintptr_t)0x004c46d1u)
#endif

#if !defined(OPEN_CFW_RING_PACK_ONLY) && \
    !defined(OPEN_CFW_RING_ENABLE_CCC_ONLY) && \
    !defined(OPEN_CFW_RING_INIT_ONLY) && \
    !defined(OPEN_CFW_RING_DISCOVER_ONLY) && \
    !defined(OPEN_CFW_RING_RECEIVE_ONLY) && \
    !defined(OPEN_CFW_RING_PROCESS_ONLY) && \
    !defined(OPEN_CFW_RING_SEND_ONLY)
#define OPEN_CFW_RING_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_PACK_ONLY)
uint32_t open_cfw_ring_pack_ccc_epoch(
    uint8_t connection_id, uint8_t final_write, uint16_t connection_epoch
)
{
    return (uint32_t)connection_id |
        ((uint32_t)final_write << 8u) |
        ((uint32_t)connection_epoch << 16u);
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_ENABLE_CCC_ONLY)
void open_cfw_ring_enable_ccc(void *packed_argument)
{
    uint32_t packed = (uint32_t)(uintptr_t)packed_argument;
    uint8_t connection_id = (uint8_t)packed;
    uint8_t final_write = (uint8_t)(packed >> 8u);
    uint16_t connection_epoch = (uint16_t)(packed >> 16u);
    uint16_t value = OPEN_CFW_RING_CCC_ENABLE_VALUE;

    if (connection_id == 0u ||
        connection_id != OPEN_CFW_RING_CONTROL->connection_id ||
        connection_epoch != OPEN_CFW_RING_CONTROL->connection_epoch ||
        OPEN_CFW_RING_CONNECTION_IN_USE(connection_id) == 0u ||
        OPEN_CFW_RING_CONTROL->handles == NULL ||
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_CCC_HANDLE_INDEX] == 0u) {
        return;
    }

    OPEN_CFW_RING_WRITE_REQUEST(
        connection_id,
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_CCC_HANDLE_INDEX],
        (uint16_t)sizeof(value), (const uint8_t *)&value
    );
    if (final_write == 1u) {
        OPEN_CFW_RING_THREAD_EVENT(OPEN_CFW_RING_THREAD_EVENT_CCC_READY);
    }
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_INIT_ONLY)
void open_cfw_ring_handler_init(uint8_t handler_id, uint16_t *handles)
{
    OPEN_CFW_RING_CONTROL->handler_id = handler_id;
    OPEN_CFW_RING_CONTROL->connection_id = 0u;
    OPEN_CFW_RING_CONTROL->connection_epoch = 1u;
    OPEN_CFW_RING_CONTROL->handles = handles;
    handles[OPEN_CFW_RING_TX_HANDLE_INDEX] = OPEN_CFW_RING_DEFAULT_TX_HANDLE;
    handles[OPEN_CFW_RING_RX_HANDLE_INDEX] = OPEN_CFW_RING_DEFAULT_RX_HANDLE;
    handles[OPEN_CFW_RING_CCC_HANDLE_INDEX] = OPEN_CFW_RING_DEFAULT_CCC_HANDLE;
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_DISCOVER_ONLY)
void open_cfw_ring_service_discover(uint8_t connection_id, uint16_t *handles)
{
    OPEN_CFW_RING_DISCOVER_SERVICE(
        connection_id, OPEN_CFW_RING_SERVICE_UUID_LENGTH,
        OPEN_CFW_RING_SERVICE_UUID, OPEN_CFW_RING_HANDLE_COUNT,
        OPEN_CFW_RING_DISCOVERY_CHARACTERISTICS, handles
    );
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_RECEIVE_ONLY)
void open_cfw_ring_receive_data(struct open_cfw_ring_message *message)
{
    if (message->status == 0u &&
        message->handle ==
            OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_RX_HANDLE_INDEX]) {
        OPEN_CFW_RING_THREAD_MESSAGE(message->data, message->length);
    }
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_PROCESS_ONLY)
void open_cfw_ring_process_message(
    uint32_t event_mask, struct open_cfw_ring_message *message
)
{
    uint8_t connection_id;
    uint16_t tx_handle;
    uint32_t packed;
    (void)event_mask;

    if (message == NULL) return;
    switch (message->event) {
    case OPEN_CFW_RING_EVENT_ATT_READ_RESPONSE:
    case OPEN_CFW_RING_EVENT_ATT_NOTIFICATION:
    case OPEN_CFW_RING_EVENT_ATT_INDICATION:
        if (OPEN_CFW_RING_CONNECTION_ROLE(
                OPEN_CFW_RING_CONTROL->connection_id) ==
            OPEN_CFW_RING_ROLE_CENTRAL) {
            open_cfw_ring_receive_data(message);
        }
        break;

    case OPEN_CFW_RING_EVENT_CONNECTION_OPEN:
        connection_id = (uint8_t)message->parameter;
        if (OPEN_CFW_RING_CONNECTION_ROLE(connection_id) !=
            OPEN_CFW_RING_ROLE_CENTRAL) break;
        OPEN_CFW_RING_CONTROL->connection_id = connection_id;
        OPEN_CFW_RING_CONTROL->connection_epoch++;
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_TX_HANDLE_INDEX] =
            OPEN_CFW_RING_DEFAULT_TX_HANDLE;
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_RX_HANDLE_INDEX] =
            OPEN_CFW_RING_DEFAULT_RX_HANDLE;
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_CCC_HANDLE_INDEX] =
            OPEN_CFW_RING_DEFAULT_CCC_HANDLE;
        if (OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_CCC_HANDLE_INDEX] !=
            0u) {
            (void)OPEN_CFW_RING_REMOVE_DELAYED(OPEN_CFW_RING_DELAY_CALLBACK);
            packed = open_cfw_ring_pack_ccc_epoch(
                connection_id, 0u, OPEN_CFW_RING_CONTROL->connection_epoch
            );
            OPEN_CFW_RING_PUSH_DELAYED(
                OPEN_CFW_RING_DELAY_CALLBACK, (void *)(uintptr_t)packed,
                OPEN_CFW_RING_CCC_DELAY_FIRST
            );
            OPEN_CFW_RING_PUSH_DELAYED(
                OPEN_CFW_RING_DELAY_CALLBACK, (void *)(uintptr_t)packed,
                OPEN_CFW_RING_CCC_DELAY_SECOND
            );
            packed = open_cfw_ring_pack_ccc_epoch(
                connection_id, 1u, OPEN_CFW_RING_CONTROL->connection_epoch
            );
            OPEN_CFW_RING_PUSH_DELAYED(
                OPEN_CFW_RING_DELAY_CALLBACK, (void *)(uintptr_t)packed,
                OPEN_CFW_RING_CCC_DELAY_FINAL
            );
        }
        break;

    case OPEN_CFW_RING_EVENT_CONNECTION_CLOSE:
        connection_id = (uint8_t)message->parameter;
        if (OPEN_CFW_RING_CONNECTION_ROLE(connection_id) !=
            OPEN_CFW_RING_ROLE_CENTRAL) break;
        OPEN_CFW_RING_CONTROL->connection_id = 0u;
        OPEN_CFW_RING_CONTROL->connection_epoch++;
        if (OPEN_CFW_RING_CONTROL->handles != NULL) {
            OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_TX_HANDLE_INDEX] = 0u;
            OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_RX_HANDLE_INDEX] = 0u;
            OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_CCC_HANDLE_INDEX] = 0u;
        }
        (void)OPEN_CFW_RING_REMOVE_DELAYED(OPEN_CFW_RING_DELAY_CALLBACK);
        OPEN_CFW_RING_THREAD_EVENT(OPEN_CFW_RING_THREAD_EVENT_DISCONNECTED);
        break;

    case OPEN_CFW_RING_EVENT_SEND_DATA:
        connection_id = (uint8_t)message->parameter;
        tx_handle = OPEN_CFW_RING_CONTROL->handles == NULL ? 0u :
            OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_TX_HANDLE_INDEX];
        if (connection_id == 0u ||
            connection_id != OPEN_CFW_RING_CONTROL->connection_id ||
            tx_handle == 0u) {
            OPEN_CFW_RING_TX_COMPLETE_NOTIFY();
        } else {
            OPEN_CFW_RING_WRITE_COMMAND(
                connection_id, tx_handle, message->length, message->data
            );
        }
        break;

    default:
        break;
    }
}
#endif

#if defined(OPEN_CFW_RING_BUILD_ALL) || defined(OPEN_CFW_RING_SEND_ONLY)
uint8_t open_cfw_ring_send_data(const uint8_t *data, uint16_t length)
{
    struct open_cfw_ring_message *message;

    if (OPEN_CFW_RING_CONTROL->connection_id == 0u ||
        OPEN_CFW_RING_CONTROL->handles == NULL ||
        OPEN_CFW_RING_CONTROL->handles[OPEN_CFW_RING_TX_HANDLE_INDEX] == 0u) {
        return 0u;
    }

    OPEN_CFW_RING_WAIT_TX_READY();
    message = OPEN_CFW_RING_MESSAGE_ALLOC(OPEN_CFW_RING_MESSAGE_BYTES);
    if (message != NULL) {
        message->event = OPEN_CFW_RING_EVENT_SEND_DATA;
        message->parameter = OPEN_CFW_RING_CONTROL->connection_id;
        message->data = data;
        message->length = length;
        OPEN_CFW_RING_MESSAGE_SEND(OPEN_CFW_RING_CONTROL->handler_id, message);
    } else {
        OPEN_CFW_RING_TX_COMPLETE_NOTIFY();
    }
    return 0u;
}
#endif
