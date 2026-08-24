/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production reconstruction of G2's seven-function BLE OTA profile adapter.
 * The event/CCC/handler skeleton follows AmbiqSuite 2.5.1 AMOTA; the compact
 * control block, provider calls, and A7 data-message path are recovered G2 ABI.
 * Stock EasyLogger calls are diagnostic-only and intentionally omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_OTA_EVENT_CONNECTION_OPEN 0x12u
#define OPEN_CFW_OTA_EVENT_CCC_STATE 0x14u
#define OPEN_CFW_OTA_EVENT_VALUE_CONFIRM 0x27u
#define OPEN_CFW_OTA_EVENT_CONNECTION_CLOSE 0x28u
#define OPEN_CFW_OTA_EVENT_RESET 0xa0u
#define OPEN_CFW_OTA_EVENT_DISCONNECT 0xa1u
#define OPEN_CFW_OTA_EVENT_SEND_DATA 0xa7u
#define OPEN_CFW_OTA_TX_CCC_INDEX 1u
#define OPEN_CFW_OTA_NOTIFY_ENABLED 1u
#define OPEN_CFW_OTA_PROVIDER_HANDLE 0x0824u
#define OPEN_CFW_OTA_MESSAGE_BYTES 12u
#define OPEN_CFW_OTA_DISCONNECT_DELAY 200u

struct open_cfw_ota_control {
    uint8_t connection_id;
    uint8_t handler_id;
    uint8_t notifications_enabled;
    uint8_t connection_ready;
};

struct open_cfw_ota_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    const uint8_t *data;
    uint16_t length;
    uint16_t reserved;
};

struct open_cfw_ota_ccc_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    uint16_t handle;
    uint16_t value;
    uint8_t index;
};

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(struct open_cfw_ota_message) == 12u,
    "G2 WSF OTA message ABI changed");
_Static_assert(offsetof(struct open_cfw_ota_message, data) == 4u,
    "G2 WSF OTA data-pointer ABI changed");
_Static_assert(offsetof(struct open_cfw_ota_message, length) == 8u,
    "G2 WSF OTA length ABI changed");
#endif

#ifndef OPEN_CFW_OTA_CONTROL
#define OPEN_CFW_OTA_CONTROL \
    ((volatile struct open_cfw_ota_control *)(uintptr_t)0x200748b4u)
#endif
#ifndef OPEN_CFW_OTA_WRITE
uint8_t open_cfw_retained_ota_write(const uint8_t *, uint16_t);
#define OPEN_CFW_OTA_WRITE(data, length) \
    open_cfw_retained_ota_write((data), (length))
#endif
#ifndef OPEN_CFW_OTA_RESET_REQUEST
void open_cfw_retained_ota_reset_request(uint32_t, uint32_t);
#define OPEN_CFW_OTA_RESET_REQUEST(a, b) \
    open_cfw_retained_ota_reset_request((a), (b))
#endif
#ifndef OPEN_CFW_OTA_CONNECTION_CLOSE
void open_cfw_retained_ota_connection_close(uint8_t);
#define OPEN_CFW_OTA_CONNECTION_CLOSE(id) \
    open_cfw_retained_ota_connection_close(id)
#endif
#ifndef OPEN_CFW_OTA_DELAY
void open_cfw_retained_ota_delay(void (*)(void *), void *, uint32_t);
#define OPEN_CFW_OTA_DELAY(callback, argument, delay) \
    open_cfw_retained_ota_delay((callback), (argument), (delay))
#endif
#ifndef OPEN_CFW_OTA_CONNECTION_ROLE
uint8_t open_cfw_retained_ota_connection_role(uint8_t);
#define OPEN_CFW_OTA_CONNECTION_ROLE(id) \
    open_cfw_retained_ota_connection_role(id)
#endif
#ifndef OPEN_CFW_OTA_CANCEL_EXPORT
void open_cfw_retained_ota_cancel_export(void);
#define OPEN_CFW_OTA_CANCEL_EXPORT() open_cfw_retained_ota_cancel_export()
#endif
#ifndef OPEN_CFW_OTA_SERVICE_INIT
void open_cfw_retained_ota_service_init(void);
#define OPEN_CFW_OTA_SERVICE_INIT() open_cfw_retained_ota_service_init()
#endif
#ifndef OPEN_CFW_OTA_CONNECTION_STATE
uint8_t open_cfw_retained_ota_connection_state(void);
#define OPEN_CFW_OTA_CONNECTION_STATE() open_cfw_retained_ota_connection_state()
#endif
#ifndef OPEN_CFW_OTA_WAIT_TX_READY
void open_cfw_retained_ota_wait_tx_ready(void);
#define OPEN_CFW_OTA_WAIT_TX_READY() open_cfw_retained_ota_wait_tx_ready()
#endif
#ifndef OPEN_CFW_OTA_TX_COMPLETE_NOTIFY
void open_cfw_retained_ota_tx_complete_notify(void);
#define OPEN_CFW_OTA_TX_COMPLETE_NOTIFY() \
    open_cfw_retained_ota_tx_complete_notify()
#endif
#ifndef OPEN_CFW_OTA_MESSAGE_ALLOC
void *open_cfw_retained_ota_message_alloc(uint16_t);
#define OPEN_CFW_OTA_MESSAGE_ALLOC(size) \
    open_cfw_retained_ota_message_alloc(size)
#endif
#ifndef OPEN_CFW_OTA_MESSAGE_SEND
void open_cfw_retained_ota_message_send(uint8_t, void *);
#define OPEN_CFW_OTA_MESSAGE_SEND(handler, message) \
    open_cfw_retained_ota_message_send((handler), (message))
#endif
#ifndef OPEN_CFW_OTA_NOTIFY
void open_cfw_retained_ota_notify(
    uint8_t, uint16_t, uint16_t, const uint8_t *
);
#define OPEN_CFW_OTA_NOTIFY(...) open_cfw_retained_ota_notify(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_OTA_DISCONNECT_CALLBACK
#define OPEN_CFW_OTA_DISCONNECT_CALLBACK \
    ((void (*)(void *))(uintptr_t)0x004bdb39u)
#endif

void open_cfw_ota_process_ccc(struct open_cfw_ota_message *message);
void open_cfw_ota_process_message(struct open_cfw_ota_message *message);
uint8_t open_cfw_ota_write_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, uint16_t length, uint8_t *value, const void *attribute
);
void open_cfw_ota_handler_init(uint8_t handler_id);
void open_cfw_ota_disconnect(void);
void open_cfw_ota_public_process_message(
    uint32_t event_mask, struct open_cfw_ota_message *message
);
uint8_t open_cfw_ota_send_data(const uint8_t *data, uint16_t length);

#if !defined(OPEN_CFW_OTA_CCC_ONLY) && \
    !defined(OPEN_CFW_OTA_PROCESS_ONLY) && \
    !defined(OPEN_CFW_OTA_WRITE_ONLY) && \
    !defined(OPEN_CFW_OTA_INIT_ONLY) && \
    !defined(OPEN_CFW_OTA_DISCONNECT_ONLY) && \
    !defined(OPEN_CFW_OTA_PUBLIC_PROCESS_ONLY) && \
    !defined(OPEN_CFW_OTA_SEND_ONLY)
#define OPEN_CFW_OTA_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_CCC_ONLY)
void open_cfw_ota_process_ccc(struct open_cfw_ota_message *message)
{
    struct open_cfw_ota_ccc_message *ccc =
        (struct open_cfw_ota_ccc_message *)(void *)message;
    if (ccc->event != OPEN_CFW_OTA_EVENT_CCC_STATE) return;
    if (ccc->index == OPEN_CFW_OTA_TX_CCC_INDEX) {
        if (ccc->value == OPEN_CFW_OTA_NOTIFY_ENABLED) {
            OPEN_CFW_OTA_CONTROL->connection_id = (uint8_t)ccc->parameter;
            OPEN_CFW_OTA_CONTROL->notifications_enabled = 1u;
        } else {
            OPEN_CFW_OTA_CONTROL->connection_id = 0u;
            OPEN_CFW_OTA_CONTROL->notifications_enabled = 0u;
        }
    }
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_PROCESS_ONLY)
void open_cfw_ota_process_message(struct open_cfw_ota_message *message)
{
    switch (message->event) {
    case OPEN_CFW_OTA_EVENT_CONNECTION_OPEN:
        OPEN_CFW_OTA_CONTROL->connection_ready = message->status == 0u;
        break;
    case OPEN_CFW_OTA_EVENT_CCC_STATE:
        open_cfw_ota_process_ccc(message);
        break;
    case OPEN_CFW_OTA_EVENT_VALUE_CONFIRM:
        break;
    case OPEN_CFW_OTA_EVENT_CONNECTION_CLOSE:
        if (OPEN_CFW_OTA_CONNECTION_ROLE((uint8_t)message->parameter) == 1u) {
            OPEN_CFW_OTA_CONTROL->connection_id = 0u;
            OPEN_CFW_OTA_CANCEL_EXPORT();
        }
        break;
    case OPEN_CFW_OTA_EVENT_RESET:
        OPEN_CFW_OTA_RESET_REQUEST(0u, 0u);
        break;
    case OPEN_CFW_OTA_EVENT_DISCONNECT:
        OPEN_CFW_OTA_CONNECTION_CLOSE(OPEN_CFW_OTA_CONTROL->connection_id);
        OPEN_CFW_OTA_DELAY(
            OPEN_CFW_OTA_DISCONNECT_CALLBACK, NULL,
            OPEN_CFW_OTA_DISCONNECT_DELAY
        );
        break;
    case OPEN_CFW_OTA_EVENT_SEND_DATA:
        OPEN_CFW_OTA_CONTROL->connection_ready = 0u;
        OPEN_CFW_OTA_NOTIFY(
            (uint8_t)message->parameter, OPEN_CFW_OTA_PROVIDER_HANDLE,
            message->length, message->data
        );
        break;
    default:
        break;
    }
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_WRITE_ONLY)
uint8_t open_cfw_ota_write_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, uint16_t length, uint8_t *value, const void *attribute
)
{
    (void)connection_id; (void)handle; (void)operation; (void)offset;
    (void)attribute;
    (void)OPEN_CFW_OTA_WRITE(value, length);
    return 0u;
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_INIT_ONLY)
void open_cfw_ota_handler_init(uint8_t handler_id)
{
    OPEN_CFW_OTA_CONTROL->handler_id = handler_id;
    OPEN_CFW_OTA_CONTROL->connection_id = 0u;
    OPEN_CFW_OTA_CONTROL->notifications_enabled = 0u;
    OPEN_CFW_OTA_CONTROL->connection_ready = 0u;
    OPEN_CFW_OTA_SERVICE_INIT();
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_DISCONNECT_ONLY)
void open_cfw_ota_disconnect(void)
{
    struct open_cfw_ota_message *message =
        OPEN_CFW_OTA_MESSAGE_ALLOC(OPEN_CFW_OTA_MESSAGE_BYTES);
    if (message != NULL) {
        message->event = OPEN_CFW_OTA_EVENT_DISCONNECT;
        message->parameter = OPEN_CFW_OTA_CONTROL->connection_id;
        OPEN_CFW_OTA_MESSAGE_SEND(OPEN_CFW_OTA_CONTROL->handler_id, message);
    }
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_PUBLIC_PROCESS_ONLY)
void open_cfw_ota_public_process_message(
    uint32_t event_mask, struct open_cfw_ota_message *message
)
{
    (void)event_mask;
    if (message != NULL) open_cfw_ota_process_message(message);
}
#endif

#if defined(OPEN_CFW_OTA_BUILD_ALL) || defined(OPEN_CFW_OTA_SEND_ONLY)
uint8_t open_cfw_ota_send_data(const uint8_t *data, uint16_t length)
{
    struct open_cfw_ota_message *message;
    (void)OPEN_CFW_OTA_CONNECTION_STATE();
    if (OPEN_CFW_OTA_CONTROL->connection_id == 0u ||
        OPEN_CFW_OTA_CONTROL->notifications_enabled != 1u) return 0u;
    OPEN_CFW_OTA_WAIT_TX_READY();
    message = OPEN_CFW_OTA_MESSAGE_ALLOC(OPEN_CFW_OTA_MESSAGE_BYTES);
    if (message != NULL) {
        message->event = OPEN_CFW_OTA_EVENT_SEND_DATA;
        message->parameter = OPEN_CFW_OTA_CONTROL->connection_id;
        message->data = data;
        message->length = length;
        OPEN_CFW_OTA_MESSAGE_SEND(OPEN_CFW_OTA_CONTROL->handler_id, message);
    } else {
        OPEN_CFW_OTA_TX_COMPLETE_NOTIFY();
    }
    return 0u;
}
#endif
