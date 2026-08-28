/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room production reconstruction of the G2 EUS, ESS, EFS, and NUS
 * Cordio application-profile adapters.  The implementation preserves the
 * recovered four-byte control blocks, WSF message ABI, CCC indices, provider
 * handles, OTA exclusion policy, write callbacks, and TX-completion semaphore
 * behavior.  Stock EasyLogger calls are diagnostic-only and are omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_BLE_PROFILE_EVENT_CONNECTION_OPEN 0x12u
#define OPEN_CFW_BLE_PROFILE_EVENT_CCC_STATE 0x14u
#define OPEN_CFW_BLE_PROFILE_EVENT_VALUE_CONFIRM 0x27u
#define OPEN_CFW_BLE_PROFILE_EVENT_CONNECTION_CLOSE 0x28u
#define OPEN_CFW_BLE_PROFILE_EVENT_EUS_SEND 0xa8u
#define OPEN_CFW_BLE_PROFILE_EVENT_ESS_SEND 0xa9u
#define OPEN_CFW_BLE_PROFILE_EVENT_EFS_SEND 0xaau
#define OPEN_CFW_BLE_PROFILE_EVENT_NUS_SEND 0xabu
#define OPEN_CFW_BLE_PROFILE_CCC_EUS 2u
#define OPEN_CFW_BLE_PROFILE_CCC_ESS 3u
#define OPEN_CFW_BLE_PROFILE_CCC_EFS 4u
#define OPEN_CFW_BLE_PROFILE_CCC_NUS 5u
#define OPEN_CFW_BLE_PROFILE_CCC_ENABLED 1u
#define OPEN_CFW_BLE_PROFILE_EUS_HANDLE 0x0844u
#define OPEN_CFW_BLE_PROFILE_ESS_HANDLE 0x0864u
#define OPEN_CFW_BLE_PROFILE_EFS_HANDLE 0x0884u
#define OPEN_CFW_BLE_PROFILE_NUS_HANDLE 0x08a4u
#define OPEN_CFW_BLE_PROFILE_MESSAGE_BYTES 12u

struct open_cfw_ble_profile_control {
    uint8_t connection_id;
    uint8_t handler_id;
    uint8_t notifications_enabled;
    uint8_t connection_ready;
};

struct open_cfw_ble_profile_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    const uint8_t *data;
    uint16_t length;
    uint16_t reserved;
};

struct open_cfw_ble_profile_ccc_message {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    uint16_t handle;
    uint16_t value;
    uint8_t index;
};

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(sizeof(struct open_cfw_ble_profile_message) == 12u,
    "G2 BLE profile WSF message ABI changed");
_Static_assert(offsetof(struct open_cfw_ble_profile_message, data) == 4u,
    "G2 BLE profile data-pointer ABI changed");
_Static_assert(offsetof(struct open_cfw_ble_profile_message, length) == 8u,
    "G2 BLE profile length ABI changed");
#endif

#ifndef OPEN_CFW_BLE_EUS_CONTROL
#define OPEN_CFW_BLE_EUS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(uintptr_t)0x200748acu)
#endif
#ifndef OPEN_CFW_BLE_ESS_CONTROL
#define OPEN_CFW_BLE_ESS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(uintptr_t)0x200748a8u)
#endif
#ifndef OPEN_CFW_BLE_EFS_CONTROL
#define OPEN_CFW_BLE_EFS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(uintptr_t)0x200748a4u)
#endif
#ifndef OPEN_CFW_BLE_NUS_CONTROL
#define OPEN_CFW_BLE_NUS_CONTROL ((volatile struct open_cfw_ble_profile_control *)(uintptr_t)0x200748b0u)
#endif

#ifndef OPEN_CFW_BLE_PROFILE_CONNECTION_ROLE
uint8_t open_cfw_retained_ble_profile_connection_role(uint8_t);
#define OPEN_CFW_BLE_PROFILE_CONNECTION_ROLE(id) open_cfw_retained_ble_profile_connection_role(id)
#endif
#ifndef OPEN_CFW_BLE_PROFILE_OTA_ACTIVE
uint8_t open_cfw_retained_ble_profile_ota_active(void);
#define OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() open_cfw_retained_ble_profile_ota_active()
#endif
#ifndef OPEN_CFW_BLE_PROFILE_MESSAGE_ALLOC
void *open_cfw_retained_ble_profile_message_alloc(uint16_t);
#define OPEN_CFW_BLE_PROFILE_MESSAGE_ALLOC(size) open_cfw_retained_ble_profile_message_alloc(size)
#endif
#ifndef OPEN_CFW_BLE_PROFILE_MESSAGE_SEND
void open_cfw_retained_ble_profile_message_send(uint8_t, void *);
#define OPEN_CFW_BLE_PROFILE_MESSAGE_SEND(handler, message) open_cfw_retained_ble_profile_message_send((handler), (message))
#endif
#ifndef OPEN_CFW_BLE_PROFILE_NOTIFY
void open_cfw_retained_ble_profile_notify(uint8_t, uint16_t, uint16_t, const uint8_t *);
#define OPEN_CFW_BLE_PROFILE_NOTIFY(...) open_cfw_retained_ble_profile_notify(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_BLE_PROFILE_WAIT_TX_READY
void open_cfw_retained_ble_profile_wait_tx_ready(void);
#define OPEN_CFW_BLE_PROFILE_WAIT_TX_READY() open_cfw_retained_ble_profile_wait_tx_ready()
#endif
#ifndef OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY
void open_cfw_retained_ble_profile_tx_complete_notify(void);
#define OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY() open_cfw_retained_ble_profile_tx_complete_notify()
#endif
#ifndef OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED
uint8_t open_cfw_retained_ble_profile_remove_delayed(void (*)(void *));
#define OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED(callback) open_cfw_retained_ble_profile_remove_delayed(callback)
#endif
#ifndef OPEN_CFW_BLE_PROFILE_EUS_RECEIVE
uint8_t open_cfw_retained_ble_profile_eus_receive(uint8_t, const uint8_t *, uint16_t);
#define OPEN_CFW_BLE_PROFILE_EUS_RECEIVE(direction, data, length) open_cfw_retained_ble_profile_eus_receive((direction), (data), (length))
#endif
#ifndef OPEN_CFW_BLE_PROFILE_EFS_RECEIVE
uint8_t open_cfw_retained_ble_profile_efs_receive(const uint8_t *, uint16_t);
#define OPEN_CFW_BLE_PROFILE_EFS_RECEIVE(data, length) open_cfw_retained_ble_profile_efs_receive((data), (length))
#endif
#ifndef OPEN_CFW_BLE_PROFILE_NUS_RECEIVE
void open_cfw_retained_ble_profile_nus_receive(const uint8_t *, uint16_t);
#define OPEN_CFW_BLE_PROFILE_NUS_RECEIVE(data, length) open_cfw_retained_ble_profile_nus_receive((data), (length))
#endif
#ifndef OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK
#define OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK ((void (*)(void *))(uintptr_t)0x004b81b9u)
#endif

#define OPEN_CFW_DECLARE_PROFILE(prefix) \
    void open_cfw_ble_##prefix##_process_ccc(struct open_cfw_ble_profile_message *); \
    void open_cfw_ble_##prefix##_process_message(struct open_cfw_ble_profile_message *); \
    uint8_t open_cfw_ble_##prefix##_write_callback(uint8_t, uint16_t, uint8_t, uint16_t, uint16_t, uint8_t *, const void *); \
    void open_cfw_ble_##prefix##_handler_init(uint8_t); \
    void open_cfw_ble_##prefix##_public_process_message(uint32_t, struct open_cfw_ble_profile_message *); \
    uint8_t open_cfw_ble_##prefix##_send_data(const uint8_t *, uint16_t)

OPEN_CFW_DECLARE_PROFILE(eus);
OPEN_CFW_DECLARE_PROFILE(ess);
OPEN_CFW_DECLARE_PROFILE(efs);
OPEN_CFW_DECLARE_PROFILE(nus);
uint8_t open_cfw_ble_eus_direct_send_data(const uint8_t *, uint16_t);

#if !defined(OPEN_CFW_BLE_EUS_CCC_ONLY) && !defined(OPEN_CFW_BLE_EUS_PROCESS_ONLY) && !defined(OPEN_CFW_BLE_EUS_WRITE_ONLY) && !defined(OPEN_CFW_BLE_EUS_INIT_ONLY) && !defined(OPEN_CFW_BLE_EUS_PUBLIC_ONLY) && !defined(OPEN_CFW_BLE_EUS_SEND_ONLY) && !defined(OPEN_CFW_BLE_EUS_DIRECT_SEND_ONLY) && !defined(OPEN_CFW_BLE_ESS_CCC_ONLY) && !defined(OPEN_CFW_BLE_ESS_PROCESS_ONLY) && !defined(OPEN_CFW_BLE_ESS_WRITE_ONLY) && !defined(OPEN_CFW_BLE_ESS_INIT_ONLY) && !defined(OPEN_CFW_BLE_ESS_PUBLIC_ONLY) && !defined(OPEN_CFW_BLE_ESS_SEND_ONLY) && !defined(OPEN_CFW_BLE_EFS_CCC_ONLY) && !defined(OPEN_CFW_BLE_EFS_PROCESS_ONLY) && !defined(OPEN_CFW_BLE_EFS_WRITE_ONLY) && !defined(OPEN_CFW_BLE_EFS_INIT_ONLY) && !defined(OPEN_CFW_BLE_EFS_PUBLIC_ONLY) && !defined(OPEN_CFW_BLE_EFS_SEND_ONLY) && !defined(OPEN_CFW_BLE_NUS_CCC_ONLY) && !defined(OPEN_CFW_BLE_NUS_PROCESS_ONLY) && !defined(OPEN_CFW_BLE_NUS_WRITE_ONLY) && !defined(OPEN_CFW_BLE_NUS_INIT_ONLY) && !defined(OPEN_CFW_BLE_NUS_PUBLIC_ONLY) && !defined(OPEN_CFW_BLE_NUS_SEND_ONLY)
#define OPEN_CFW_BLE_PROFILES_BUILD_ALL 1
#endif

#define OPEN_CFW_DEFINE_CCC(prefix, upper, ccc_index) \
void open_cfw_ble_##prefix##_process_ccc(struct open_cfw_ble_profile_message *message) \
{ \
    struct open_cfw_ble_profile_ccc_message *ccc = (struct open_cfw_ble_profile_ccc_message *)(void *)message; \
    if (ccc == NULL || ccc->event != OPEN_CFW_BLE_PROFILE_EVENT_CCC_STATE || ccc->index != (ccc_index)) return; \
    if (ccc->value == OPEN_CFW_BLE_PROFILE_CCC_ENABLED) { \
        OPEN_CFW_BLE_##upper##_CONTROL->connection_id = (uint8_t)ccc->parameter; \
        OPEN_CFW_BLE_##upper##_CONTROL->notifications_enabled = 1u; \
    } else { \
        OPEN_CFW_BLE_##upper##_CONTROL->connection_id = 0u; \
        OPEN_CFW_BLE_##upper##_CONTROL->notifications_enabled = 0u; \
    } \
}

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_CCC_ONLY)
OPEN_CFW_DEFINE_CCC(eus, EUS, OPEN_CFW_BLE_PROFILE_CCC_EUS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_CCC_ONLY)
OPEN_CFW_DEFINE_CCC(ess, ESS, OPEN_CFW_BLE_PROFILE_CCC_ESS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_CCC_ONLY)
OPEN_CFW_DEFINE_CCC(efs, EFS, OPEN_CFW_BLE_PROFILE_CCC_EFS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_CCC_ONLY)
OPEN_CFW_DEFINE_CCC(nus, NUS, OPEN_CFW_BLE_PROFILE_CCC_NUS)
#endif

#define OPEN_CFW_DEFINE_PROCESS(prefix, upper, send_event, provider_handle) \
void open_cfw_ble_##prefix##_process_message(struct open_cfw_ble_profile_message *message) \
{ \
    if (message == NULL) return; \
    switch (message->event) { \
    case OPEN_CFW_BLE_PROFILE_EVENT_CONNECTION_OPEN: \
        OPEN_CFW_BLE_##upper##_CONTROL->connection_ready = message->status == 0u; \
        break; \
    case OPEN_CFW_BLE_PROFILE_EVENT_CCC_STATE: \
        open_cfw_ble_##prefix##_process_ccc(message); \
        break; \
    case OPEN_CFW_BLE_PROFILE_EVENT_VALUE_CONFIRM: \
        break; \
    case OPEN_CFW_BLE_PROFILE_EVENT_CONNECTION_CLOSE: \
        if (OPEN_CFW_BLE_PROFILE_CONNECTION_ROLE((uint8_t)message->parameter) == 1u) \
            OPEN_CFW_BLE_##upper##_CONTROL->connection_id = 0u; \
        break; \
    case (send_event): \
        OPEN_CFW_BLE_##upper##_CONTROL->connection_ready = 0u; \
        OPEN_CFW_BLE_PROFILE_NOTIFY((uint8_t)message->parameter, (provider_handle), message->length, message->data); \
        break; \
    default: \
        break; \
    } \
}

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_PROCESS_ONLY)
OPEN_CFW_DEFINE_PROCESS(eus, EUS, OPEN_CFW_BLE_PROFILE_EVENT_EUS_SEND, OPEN_CFW_BLE_PROFILE_EUS_HANDLE)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_PROCESS_ONLY)
OPEN_CFW_DEFINE_PROCESS(ess, ESS, OPEN_CFW_BLE_PROFILE_EVENT_ESS_SEND, OPEN_CFW_BLE_PROFILE_ESS_HANDLE)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_PROCESS_ONLY)
OPEN_CFW_DEFINE_PROCESS(efs, EFS, OPEN_CFW_BLE_PROFILE_EVENT_EFS_SEND, OPEN_CFW_BLE_PROFILE_EFS_HANDLE)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_PROCESS_ONLY)
OPEN_CFW_DEFINE_PROCESS(nus, NUS, OPEN_CFW_BLE_PROFILE_EVENT_NUS_SEND, OPEN_CFW_BLE_PROFILE_NUS_HANDLE)
#endif

#define OPEN_CFW_UNUSED_WRITE_ARGS() do { (void)connection_id; (void)handle; (void)operation; (void)offset; (void)attribute; } while (0)

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_WRITE_ONLY)
uint8_t open_cfw_ble_eus_write_callback(uint8_t connection_id, uint16_t handle, uint8_t operation, uint16_t offset, uint16_t length, uint8_t *value, const void *attribute)
{
    OPEN_CFW_UNUSED_WRITE_ARGS();
    (void)OPEN_CFW_BLE_PROFILE_EUS_RECEIVE(0u, value, length);
    (void)OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED(OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK);
    return 0u;
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_WRITE_ONLY)
uint8_t open_cfw_ble_ess_write_callback(uint8_t connection_id, uint16_t handle, uint8_t operation, uint16_t offset, uint16_t length, uint8_t *value, const void *attribute)
{
    OPEN_CFW_UNUSED_WRITE_ARGS();
    (void)open_cfw_ble_ess_send_data(value, length);
    return 0u;
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_WRITE_ONLY)
uint8_t open_cfw_ble_efs_write_callback(uint8_t connection_id, uint16_t handle, uint8_t operation, uint16_t offset, uint16_t length, uint8_t *value, const void *attribute)
{
    OPEN_CFW_UNUSED_WRITE_ARGS();
    if (OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() != 0u) return 0u;
    (void)OPEN_CFW_BLE_PROFILE_EFS_RECEIVE(value, length);
    (void)OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED(OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK);
    return 0u;
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_WRITE_ONLY)
uint8_t open_cfw_ble_nus_write_callback(uint8_t connection_id, uint16_t handle, uint8_t operation, uint16_t offset, uint16_t length, uint8_t *value, const void *attribute)
{
    OPEN_CFW_UNUSED_WRITE_ARGS();
    OPEN_CFW_BLE_PROFILE_NUS_RECEIVE(value, length);
    (void)OPEN_CFW_BLE_PROFILE_REMOVE_DELAYED(OPEN_CFW_BLE_PROFILE_RX_TIMEOUT_CALLBACK);
    return 0u;
}
#endif

#define OPEN_CFW_DEFINE_INIT(prefix, upper) \
void open_cfw_ble_##prefix##_handler_init(uint8_t handler_id) \
{ \
    OPEN_CFW_BLE_##upper##_CONTROL->handler_id = handler_id; \
    OPEN_CFW_BLE_##upper##_CONTROL->connection_id = 0u; \
    OPEN_CFW_BLE_##upper##_CONTROL->notifications_enabled = 0u; \
    OPEN_CFW_BLE_##upper##_CONTROL->connection_ready = 0u; \
}

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_INIT_ONLY)
OPEN_CFW_DEFINE_INIT(eus, EUS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_INIT_ONLY)
OPEN_CFW_DEFINE_INIT(ess, ESS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_INIT_ONLY)
OPEN_CFW_DEFINE_INIT(efs, EFS)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_INIT_ONLY)
OPEN_CFW_DEFINE_INIT(nus, NUS)
#endif

#define OPEN_CFW_DEFINE_PUBLIC(prefix) \
void open_cfw_ble_##prefix##_public_process_message(uint32_t event_mask, struct open_cfw_ble_profile_message *message) \
{ \
    (void)event_mask; \
    if (message != NULL) open_cfw_ble_##prefix##_process_message(message); \
}

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_PUBLIC_ONLY)
OPEN_CFW_DEFINE_PUBLIC(eus)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_PUBLIC_ONLY)
OPEN_CFW_DEFINE_PUBLIC(ess)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_PUBLIC_ONLY)
OPEN_CFW_DEFINE_PUBLIC(efs)
#endif
#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_PUBLIC_ONLY)
OPEN_CFW_DEFINE_PUBLIC(nus)
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || \
    defined(OPEN_CFW_BLE_EUS_SEND_ONLY) || \
    defined(OPEN_CFW_BLE_EUS_DIRECT_SEND_ONLY) || \
    defined(OPEN_CFW_BLE_ESS_SEND_ONLY) || \
    defined(OPEN_CFW_BLE_EFS_SEND_ONLY) || \
    defined(OPEN_CFW_BLE_NUS_SEND_ONLY)
static inline __attribute__((always_inline)) uint8_t open_cfw_ble_profile_enqueue(volatile struct open_cfw_ble_profile_control *control, uint8_t event, const uint8_t *data, uint16_t length, uint8_t wait_before_send, uint8_t release_on_failure)
{
    struct open_cfw_ble_profile_message *message;
    if (control->connection_id == 0u || control->notifications_enabled != 1u) {
        if (release_on_failure != 0u) OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY();
        return 0u;
    }
    if (wait_before_send != 0u) OPEN_CFW_BLE_PROFILE_WAIT_TX_READY();
    message = OPEN_CFW_BLE_PROFILE_MESSAGE_ALLOC(OPEN_CFW_BLE_PROFILE_MESSAGE_BYTES);
    if (message == NULL) {
        if (release_on_failure != 0u) OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY();
        return 0u;
    }
    message->event = event;
    message->parameter = control->connection_id;
    message->data = data;
    message->length = length;
    OPEN_CFW_BLE_PROFILE_MESSAGE_SEND(control->handler_id, message);
    return 0u;
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_SEND_ONLY)
uint8_t open_cfw_ble_eus_send_data(const uint8_t *data, uint16_t length)
{
    if (OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() != 0u) return 0u;
    return open_cfw_ble_profile_enqueue(OPEN_CFW_BLE_EUS_CONTROL, OPEN_CFW_BLE_PROFILE_EVENT_EUS_SEND, data, length, 1u, 1u);
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EUS_DIRECT_SEND_ONLY)
uint8_t open_cfw_ble_eus_direct_send_data(const uint8_t *data, uint16_t length)
{
    if (OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() != 0u) return 0u;
    return open_cfw_ble_profile_enqueue(OPEN_CFW_BLE_EUS_CONTROL, OPEN_CFW_BLE_PROFILE_EVENT_EUS_SEND, data, length, 0u, 0u);
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_ESS_SEND_ONLY)
uint8_t open_cfw_ble_ess_send_data(const uint8_t *data, uint16_t length)
{
    if (OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() != 0u) {
        OPEN_CFW_BLE_PROFILE_TX_COMPLETE_NOTIFY();
        return 0u;
    }
    return open_cfw_ble_profile_enqueue(OPEN_CFW_BLE_ESS_CONTROL, OPEN_CFW_BLE_PROFILE_EVENT_ESS_SEND, data, length, 0u, 1u);
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_EFS_SEND_ONLY)
uint8_t open_cfw_ble_efs_send_data(const uint8_t *data, uint16_t length)
{
    return open_cfw_ble_profile_enqueue(OPEN_CFW_BLE_EFS_CONTROL, OPEN_CFW_BLE_PROFILE_EVENT_EFS_SEND, data, length, 1u, 1u);
}
#endif

#if defined(OPEN_CFW_BLE_PROFILES_BUILD_ALL) || defined(OPEN_CFW_BLE_NUS_SEND_ONLY)
uint8_t open_cfw_ble_nus_send_data(const uint8_t *data, uint16_t length)
{
    if (OPEN_CFW_BLE_PROFILE_OTA_ACTIVE() != 0u) return 0u;
    return open_cfw_ble_profile_enqueue(OPEN_CFW_BLE_NUS_CONTROL, OPEN_CFW_BLE_PROFILE_EVENT_NUS_SEND, data, length, 1u, 1u);
}
#endif
