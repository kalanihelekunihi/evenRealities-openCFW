/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the twenty linked G2 pair-manager protobuf
 * service entries. Diagnostic-only EasyLogger/assertion work is omitted. The
 * service-0x80 envelopes, nanopb status contract, deferred security-auth
 * policy, Ring connection policy, Cordio notification queue, BLE parameter
 * switching, disconnect, and unpair effects are preserved.
 */

#include <stdint.h>

typedef struct {
    uint32_t (*write)(void *, const void *, uint32_t);
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_pair_mgr_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_pair_mgr_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR
#define OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR \
    ((const void *)(uintptr_t)0x007766DCU)
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_AUTH_FLAG
#define OPEN_CFW_PB_PAIR_MGR_AUTH_FLAG \
    ((volatile uint8_t *)(uintptr_t)0x20074FFCU)
#endif

#ifndef OPEN_CFW_PB_PAIR_MGR_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_PAIR_MGR_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_PAIR_MGR_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_PAIR_MGR_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_ALLOCATE
void *open_cfw_tlsf_malloc(uint32_t bytes);
#define OPEN_CFW_PB_PAIR_MGR_ALLOCATE(bytes) open_cfw_tlsf_malloc((bytes))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_FREE
void open_cfw_tlsf_free(void *pointer);
#define OPEN_CFW_PB_PAIR_MGR_FREE(pointer) open_cfw_tlsf_free((pointer))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_SEQUENCE
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_PAIR_MGR_SEQUENCE() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif

#ifndef OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE
void open_cfw_event_loop_remove_delayed(const void *callback);
#define OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH
void open_cfw_event_loop_push_delayed(
    const void *callback, uint32_t argument, uint32_t milliseconds);
#define OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(callback, argument, milliseconds) \
    open_cfw_event_loop_push_delayed( \
        (callback), (argument), (milliseconds))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_SLAVE_UNPAIR_CALLBACK
#define OPEN_CFW_PB_PAIR_MGR_SLAVE_UNPAIR_CALLBACK \
    ((const void *)(uintptr_t)0x0046EFFDU)
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK
#define OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK \
    ((const void *)(uintptr_t)0x0046F099U)
#endif

#ifndef OPEN_CFW_PB_PAIR_MGR_CONNECTION_STATE_SET
void open_cfw_pair_mgr_connection_state_set(uint32_t state);
#define OPEN_CFW_PB_PAIR_MGR_CONNECTION_STATE_SET(state) \
    open_cfw_pair_mgr_connection_state_set((state))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_SLAVE_ROLE_SET
void open_cfw_pair_mgr_slave_role_set(uint32_t role);
#define OPEN_CFW_PB_PAIR_MGR_SLAVE_ROLE_SET(role) \
    open_cfw_pair_mgr_slave_role_set((role))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_TARGET_SET
void open_cfw_pair_mgr_target_set(
    const uint8_t *address, const uint8_t *name, uint32_t name_length);
#define OPEN_CFW_PB_PAIR_MGR_TARGET_SET(address, name, name_length) \
    open_cfw_pair_mgr_target_set((address), (name), (name_length))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET
uint32_t open_cfw_pair_mgr_auth_mode_set(uint32_t mode);
#define OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET(mode) \
    open_cfw_pair_mgr_auth_mode_set((mode))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_TARGET_COPY
void open_cfw_pair_mgr_target_copy(uint8_t *address, uint8_t *name);
#define OPEN_CFW_PB_PAIR_MGR_TARGET_COPY(address, name) \
    open_cfw_pair_mgr_target_copy((address), (name))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_LINK_MATCHES_TARGET
int open_cfw_pair_mgr_link_matches_target(const uint8_t *address);
#define OPEN_CFW_PB_PAIR_MGR_LINK_MATCHES_TARGET(address) \
    open_cfw_pair_mgr_link_matches_target((address))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_OWNER_SIDE
int open_cfw_pair_mgr_owner_side(void);
#define OPEN_CFW_PB_PAIR_MGR_OWNER_SIDE() open_cfw_pair_mgr_owner_side()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_RETRY_RESET
void open_cfw_pair_mgr_retry_reset(void);
#define OPEN_CFW_PB_PAIR_MGR_RETRY_RESET() open_cfw_pair_mgr_retry_reset()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR
void open_cfw_pair_mgr_failure_clear(void);
#define OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR() open_cfw_pair_mgr_failure_clear()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_FAILURE_BEGIN
void open_cfw_pair_mgr_failure_begin(void);
#define OPEN_CFW_PB_PAIR_MGR_FAILURE_BEGIN() open_cfw_pair_mgr_failure_begin()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_POLICY_MARK
void open_cfw_pair_mgr_policy_mark(uint32_t connected);
#define OPEN_CFW_PB_PAIR_MGR_POLICY_MARK(connected) \
    open_cfw_pair_mgr_policy_mark((connected))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_POLICY_BLOCKED
int open_cfw_pair_mgr_policy_blocked(uint32_t connected);
#define OPEN_CFW_PB_PAIR_MGR_POLICY_BLOCKED(connected) \
    open_cfw_pair_mgr_policy_blocked((connected))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT
void open_cfw_pair_mgr_connect_timeout(void);
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT() \
    open_cfw_pair_mgr_connect_timeout()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT_CANCEL
void open_cfw_pair_mgr_connect_timeout_cancel(void);
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT_CANCEL() \
    open_cfw_pair_mgr_connect_timeout_cancel()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_CONNECT_SUCCESS
void open_cfw_pair_mgr_connect_success(void);
#define OPEN_CFW_PB_PAIR_MGR_CONNECT_SUCCESS() \
    open_cfw_pair_mgr_connect_success()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_POLICY_RESET
void open_cfw_pair_mgr_policy_reset(void);
#define OPEN_CFW_PB_PAIR_MGR_POLICY_RESET() open_cfw_pair_mgr_policy_reset()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_THROTTLE_RESET
void open_cfw_pair_mgr_throttle_reset(void);
#define OPEN_CFW_PB_PAIR_MGR_THROTTLE_RESET() \
    open_cfw_pair_mgr_throttle_reset()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_PEER_EVENT
void open_cfw_pair_mgr_peer_event(uint32_t event);
#define OPEN_CFW_PB_PAIR_MGR_PEER_EVENT(event) \
    open_cfw_pair_mgr_peer_event((event))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_BLE_MODE_ZERO
void open_cfw_pair_mgr_ble_mode_zero(uint32_t argument);
#define OPEN_CFW_PB_PAIR_MGR_BLE_MODE_ZERO(argument) \
    open_cfw_pair_mgr_ble_mode_zero((argument))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_BLE_MODE_NONZERO
void open_cfw_pair_mgr_ble_mode_nonzero(uint32_t argument);
#define OPEN_CFW_PB_PAIR_MGR_BLE_MODE_NONZERO(argument) \
    open_cfw_pair_mgr_ble_mode_nonzero((argument))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_RING_CLEANUP
void open_cfw_pair_mgr_ring_cleanup(const uint8_t *address);
#define OPEN_CFW_PB_PAIR_MGR_RING_CLEANUP(address) \
    open_cfw_pair_mgr_ring_cleanup((address))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_OTA_MODE_SET
void open_cfw_pair_mgr_ota_mode_set(uint32_t enabled);
#define OPEN_CFW_PB_PAIR_MGR_OTA_MODE_SET(enabled) \
    open_cfw_pair_mgr_ota_mode_set((enabled))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_DEVICE_STATE
uint32_t open_cfw_pair_mgr_device_state(void);
#define OPEN_CFW_PB_PAIR_MGR_DEVICE_STATE() open_cfw_pair_mgr_device_state()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_SLAVE_DISCONNECT
void open_cfw_pair_mgr_slave_disconnect(uint32_t reason);
#define OPEN_CFW_PB_PAIR_MGR_SLAVE_DISCONNECT(reason) \
    open_cfw_pair_mgr_slave_disconnect((reason))
#endif

#ifndef OPEN_CFW_PB_PAIR_MGR_CONTROLLER
void *open_cfw_pair_mgr_controller(void);
#define OPEN_CFW_PB_PAIR_MGR_CONTROLLER() open_cfw_pair_mgr_controller()
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_WSF_ALLOCATE
void *open_cfw_cordio_wsf_message_allocate_candidate(uint32_t bytes);
#define OPEN_CFW_PB_PAIR_MGR_WSF_ALLOCATE(bytes) \
    open_cfw_cordio_wsf_message_allocate_candidate((bytes))
#endif
#ifndef OPEN_CFW_PB_PAIR_MGR_WSF_SEND
void open_cfw_cordio_wsf_message_send_candidate(uint32_t handler, void *message);
#define OPEN_CFW_PB_PAIR_MGR_WSF_SEND(handler, message) \
    open_cfw_cordio_wsf_message_send_candidate((handler), (message))
#endif

uint32_t open_cfw_pb_service_pair_mgr_buffer_write(
    void *output, const void *data, uint32_t length);
int PB_RxSecAuth(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeSecAuth(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);
int PB_TxEncodeNotifySecAuthImpl(uint32_t authenticated);
void pairMgrSecAuthFlagSet(uint8_t value);
uint8_t pairMgrSecAuthFlagGet(void);
int PB_RxPipeRoleChange(uint8_t magic, const uint8_t *payload);
int PB_TxEncodePipeRoleChange(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);
int _PB_RxRingConnectInfoOwnerExecute(uint8_t magic, const uint8_t *payload);
int _PB_RxRingConnectInfoCommon(
    uint8_t magic, const uint8_t *payload, uint8_t force);
int PB_RxRingConnectInfo(uint8_t magic, const uint8_t *payload);
void PB_LastTxEncodeRingConnectInfoTimeSet(uint32_t active);
int PB_TxEncodeRingConnectInfo(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);
int PB_TxEncodeNotifyRingConnectInfoImpl(uint8_t event);
int PB_TxEncodeNotifyRingConnectInfo(uint16_t event);
int PB_RxBleConnectParams(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeBleConnectParams(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);
int PB_RxDisconnectInfo(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeDisconnectInfo(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);
int PB_RxUnpairInfo(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeUnpairInfo(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload);

#if defined(OPEN_CFW_PB_PAIR_MGR_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_SEC_AUTH_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_SEC_AUTH 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_SEC_AUTH_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_SEC_AUTH 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_NOTIFY_SEC_AUTH_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_SEC_AUTH 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_FLAG_SET_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_SET 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_FLAG_GET_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_GET 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_PIPE_ROLE_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_PIPE_ROLE 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_PIPE_ROLE_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_PIPE_ROLE 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RING_OWNER_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_OWNER 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RING_COMMON_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_COMMON 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_RING_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_RING 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RING_TIME_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_TIME 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_RING_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_RING 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_NOTIFY_RING_IMPL_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING_IMPL 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_NOTIFY_RING_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_BLE_PARAMS_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_BLE_PARAMS 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_BLE_PARAMS_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_BLE_PARAMS 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_DISCONNECT_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_DISCONNECT 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_DISCONNECT_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_DISCONNECT 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_RX_UNPAIR_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_UNPAIR 1
#elif defined(OPEN_CFW_PB_PAIR_MGR_TX_UNPAIR_ONLY)
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_UNPAIR 1
#else
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_SEC_AUTH 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_SEC_AUTH 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_SEC_AUTH 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_SET 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_GET 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_PIPE_ROLE 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_PIPE_ROLE 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_OWNER 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_COMMON 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_RING 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_TIME 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_RING 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING_IMPL 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_BLE_PARAMS 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_BLE_PARAMS 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_DISCONNECT 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_DISCONNECT 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_UNPAIR 1
#define OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_UNPAIR 1
#endif

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_pb_pair_mgr_load16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_pair_mgr_store16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_pair_mgr_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

static __attribute__((always_inline, unused)) inline int
open_cfw_pb_pair_mgr_transmit(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload, uint8_t command, uint16_t tag,
    uint32_t trailing_offset)
{
    open_cfw_pb_pair_mgr_output output;
    if (buffer == (void *)0 || message == (uint8_t *)0 ||
            payload == (const uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_pair_mgr_zero(buffer, capacity);
    output.write = open_cfw_pb_service_pair_mgr_buffer_write;
    output.context = buffer;
    output.capacity = capacity;
    output.length = 0U;
    output.error = (const char *)0;
    message[0] = command;
    open_cfw_pb_pair_mgr_store16(message + 2U, magic);
    open_cfw_pb_pair_mgr_store16(message + 4U, tag);
    message[trailing_offset] = 0U;
    if (OPEN_CFW_PB_PAIR_MGR_ENCODE(
            &output, OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR, message) == 0U) {
        return 0x2B;
    }
    (void)OPEN_CFW_PB_PAIR_MGR_SEND(
        1U, 0x80U, buffer, output.length & 0xFFFFU);
    return 0;
}

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_pair_mgr_buffer_write(
    void *raw_output, const void *raw_data, uint32_t length)
{
    open_cfw_pb_pair_mgr_output *output = raw_output;
    const uint8_t *data = raw_data;
    uint8_t *destination = output->context;
    uint32_t index;
    if (output->length > output->capacity ||
            length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = data[index];
    }
    output->length += length;
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_SEC_AUTH)
__attribute__((used, noinline))
int PB_RxSecAuth(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    if (payload[0] != 0U) {
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            OPEN_CFW_PB_PAIR_MGR_SLAVE_UNPAIR_CALLBACK);
        OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
            OPEN_CFW_PB_PAIR_MGR_SLAVE_UNPAIR_CALLBACK, 1U, 500U);
    }
    OPEN_CFW_PB_PAIR_MGR_CONNECTION_STATE_SET(payload[1]);
    OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
        OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK);
    if (pairMgrSecAuthFlagGet() == 0U) {
        pairMgrSecAuthFlagSet(1U);
    } else {
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK);
        OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
            OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK, 1U, 100U);
        OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
            OPEN_CFW_PB_PAIR_MGR_ADV_RESTART_CALLBACK, 1U, 2000U);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_SEC_AUTH)
__attribute__((used, noinline))
int PB_TxEncodeSecAuth(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 4U, 3U, 10U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_SEC_AUTH)
__attribute__((used, noinline))
int PB_TxEncodeNotifySecAuthImpl(uint32_t authenticated)
{
    uint8_t *workspace;
    uint8_t *message;
    open_cfw_pb_pair_mgr_output output;
    int result;
    if (pairMgrSecAuthFlagGet() == 0U) {
        return 0;
    }
    workspace = OPEN_CFW_PB_PAIR_MGR_ALLOCATE(0x1A8U);
    if (workspace == (uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_pair_mgr_zero(workspace, 0x1A8U);
    message = workspace + 0xD4U;
    output.write = open_cfw_pb_service_pair_mgr_buffer_write;
    output.context = workspace;
    output.capacity = 0xD4U;
    output.length = 0U;
    output.error = (const char *)0;
    message[0] = 4U;
    open_cfw_pb_pair_mgr_store16(
        message + 2U, (uint16_t)(OPEN_CFW_PB_PAIR_MGR_SEQUENCE() & 0xFFU));
    open_cfw_pb_pair_mgr_store16(message + 4U, 3U);
    message[8] = authenticated != 0U ? 1U : 0U;
    message[10] = 0U;
    if (OPEN_CFW_PB_PAIR_MGR_ENCODE(
            &output, OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR, message) == 0U) {
        OPEN_CFW_PB_PAIR_MGR_FREE(workspace);
        return 0x2B;
    }
    result = OPEN_CFW_PB_PAIR_MGR_NOTIFY(
        1U, 0x80U, workspace, output.length & 0xFFFFU);
    OPEN_CFW_PB_PAIR_MGR_FREE(workspace);
    return result == 0 ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_SET)
__attribute__((used, noinline))
void pairMgrSecAuthFlagSet(uint8_t value)
{
    *OPEN_CFW_PB_PAIR_MGR_AUTH_FLAG = value;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_FLAG_GET)
__attribute__((used, noinline))
uint8_t pairMgrSecAuthFlagGet(void)
{
    return *OPEN_CFW_PB_PAIR_MGR_AUTH_FLAG;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_PIPE_ROLE)
__attribute__((used, noinline))
int PB_RxPipeRoleChange(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    OPEN_CFW_PB_PAIR_MGR_SLAVE_ROLE_SET(payload[0]);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_PIPE_ROLE)
__attribute__((used, noinline))
int PB_TxEncodePipeRoleChange(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 5U, 4U, 10U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_OWNER)
__attribute__((used, noinline))
int _PB_RxRingConnectInfoOwnerExecute(
    uint8_t magic, const uint8_t *payload)
{
    uint32_t connected;
    (void)magic;
    connected = payload[0] != 0U ? 1U : 0U;
    OPEN_CFW_PB_PAIR_MGR_TARGET_SET(
        payload + 4U, payload + 12U, open_cfw_pb_pair_mgr_load16(payload + 10U));
    (void)OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET(payload[0]);
    if (connected == 0U ||
            OPEN_CFW_PB_PAIR_MGR_LINK_MATCHES_TARGET(payload + 4U) == 0) {
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            (const void *)(uintptr_t)0x004A1B61U);
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            (const void *)(uintptr_t)0x004A23ADU);
        OPEN_CFW_PB_PAIR_MGR_RETRY_RESET();
        if (connected == 0U) {
            OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR();
            OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
                (const void *)(uintptr_t)0x004A1B61U, 0x102U, 0U);
        } else {
            OPEN_CFW_PB_PAIR_MGR_FAILURE_BEGIN();
            OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
                (const void *)(uintptr_t)0x004A1B61U, 1U, 0U);
        }
        OPEN_CFW_PB_PAIR_MGR_POLICY_MARK(connected);
        if (connected == 0U) {
            OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT_CANCEL();
        } else {
            OPEN_CFW_PB_PAIR_MGR_CONNECT_TIMEOUT();
        }
    } else {
        OPEN_CFW_PB_PAIR_MGR_POLICY_MARK(connected);
        OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR();
        OPEN_CFW_PB_PAIR_MGR_CONNECT_SUCCESS();
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            (const void *)(uintptr_t)0x004A1B61U);
        OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
            (const void *)(uintptr_t)0x004A23ADU);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_COMMON)
__attribute__((used, noinline))
int _PB_RxRingConnectInfoCommon(
    uint8_t magic, const uint8_t *payload, uint8_t force)
{
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    if (force == 0U && OPEN_CFW_PB_PAIR_MGR_POLICY_BLOCKED(payload[0]) != 0) {
        return 0;
    }
    if (payload[0] == 0U || OPEN_CFW_PB_PAIR_MGR_OWNER_SIDE() != 0) {
        return _PB_RxRingConnectInfoOwnerExecute(magic, payload);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_RING)
__attribute__((used, noinline))
int PB_RxRingConnectInfo(uint8_t magic, const uint8_t *payload)
{
    return _PB_RxRingConnectInfoCommon(magic, payload, 0U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RING_TIME)
__attribute__((used, noinline))
void PB_LastTxEncodeRingConnectInfoTimeSet(uint32_t active)
{
    if (active == 0U) {
        OPEN_CFW_PB_PAIR_MGR_POLICY_RESET();
    }
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_RING)
__attribute__((used, noinline))
int PB_TxEncodeRingConnectInfo(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 6U, 5U, 37U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING_IMPL)
__attribute__((used, noinline))
int PB_TxEncodeNotifyRingConnectInfoImpl(uint8_t event)
{
    uint8_t *workspace = OPEN_CFW_PB_PAIR_MGR_ALLOCATE(0x1A8U);
    uint8_t *message;
    open_cfw_pb_pair_mgr_output output;
    int result;
    if (workspace == (uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_pair_mgr_zero(workspace, 0x1A8U);
    message = workspace + 0xD4U;
    output.write = open_cfw_pb_service_pair_mgr_buffer_write;
    output.context = workspace;
    output.capacity = 0xD4U;
    output.length = 0U;
    output.error = (const char *)0;
    message[0] = 6U;
    open_cfw_pb_pair_mgr_store16(
        message + 2U, (uint16_t)(OPEN_CFW_PB_PAIR_MGR_SEQUENCE() & 0xFFU));
    open_cfw_pb_pair_mgr_store16(message + 4U, 5U);
    OPEN_CFW_PB_PAIR_MGR_TARGET_COPY(message + 12U, message + 20U);
    message[8] = (uint8_t)OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET(0x5AU);
    (void)OPEN_CFW_PB_PAIR_MGR_AUTH_MODE_SET(0U);
    message[36] = event;
    if (event == 0U) {
        OPEN_CFW_PB_PAIR_MGR_FAILURE_CLEAR();
    } else {
        OPEN_CFW_PB_PAIR_MGR_PEER_EVENT(2U);
    }
    message[37] = 0U;
    if (OPEN_CFW_PB_PAIR_MGR_ENCODE(
            &output, OPEN_CFW_PB_PAIR_MGR_DESCRIPTOR, message) == 0U) {
        OPEN_CFW_PB_PAIR_MGR_FREE(workspace);
        return 0x2B;
    }
    result = OPEN_CFW_PB_PAIR_MGR_NOTIFY(
        1U, 0x80U, workspace, output.length & 0xFFFFU);
    OPEN_CFW_PB_PAIR_MGR_FREE(workspace);
    return result == 0 ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_NOTIFY_RING)
__attribute__((used, noinline))
int PB_TxEncodeNotifyRingConnectInfo(uint16_t event)
{
    uint8_t *controller = OPEN_CFW_PB_PAIR_MGR_CONTROLLER();
    uint8_t *message;
    if (controller == (uint8_t *)0 || controller[0x56] == 0U) {
        return -1;
    }
    message = OPEN_CFW_PB_PAIR_MGR_WSF_ALLOCATE(12U);
    if (message == (uint8_t *)0) {
        return -1;
    }
    message[2] = 0xBBU;
    open_cfw_pb_pair_mgr_store16(message, 0U);
    open_cfw_pb_pair_mgr_store16(message + 8U, (uint16_t)(event & 0xFFU));
    OPEN_CFW_PB_PAIR_MGR_WSF_SEND(controller[0x56], message);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_BLE_PARAMS)
__attribute__((used, noinline))
int PB_RxBleConnectParams(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    if (payload[4] == 0U) {
        OPEN_CFW_PB_PAIR_MGR_BLE_MODE_ZERO(0U);
    } else {
        OPEN_CFW_PB_PAIR_MGR_BLE_MODE_NONZERO(0U);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_BLE_PARAMS)
__attribute__((used, noinline))
int PB_TxEncodeBleConnectParams(uint8_t magic, void *buffer,
    uint16_t capacity, uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 7U, 6U, 14U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_DISCONNECT)
__attribute__((used, noinline))
int PB_RxDisconnectInfo(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    OPEN_CFW_PB_PAIR_MGR_THROTTLE_RESET();
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    OPEN_CFW_PB_PAIR_MGR_RETRY_RESET();
    OPEN_CFW_PB_PAIR_MGR_EVENT_REMOVE(
        (const void *)(uintptr_t)0x004A1B61U);
    OPEN_CFW_PB_PAIR_MGR_EVENT_PUSH(
        (const void *)(uintptr_t)0x004A1B61U, 0x102U, 0U);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_DISCONNECT)
__attribute__((used, noinline))
int PB_TxEncodeDisconnectInfo(uint8_t magic, void *buffer,
    uint16_t capacity, uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 8U, 7U, 18U);
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_RX_UNPAIR)
__attribute__((used, noinline))
int PB_RxUnpairInfo(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    if (payload[0] == 0U || payload[0] == 2U) {
        OPEN_CFW_PB_PAIR_MGR_RING_CLEANUP(
            open_cfw_pb_pair_mgr_load16(payload + 2U) == 6U
                ? payload + 4U : (const uint8_t *)0);
    }
    if (payload[0] == 2U) {
        OPEN_CFW_PB_PAIR_MGR_OTA_MODE_SET(1U);
        if (OPEN_CFW_PB_PAIR_MGR_DEVICE_STATE() == 3U) {
            OPEN_CFW_PB_PAIR_MGR_SLAVE_DISCONNECT(0U);
        }
        OPEN_CFW_PB_PAIR_MGR_POLICY_RESET();
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_PAIR_MGR_INCLUDE_TX_UNPAIR)
__attribute__((used, noinline))
int PB_TxEncodeUnpairInfo(uint8_t magic, void *buffer, uint16_t capacity,
    uint8_t *message, const uint8_t *payload)
{
    return open_cfw_pb_pair_mgr_transmit(
        magic, buffer, capacity, message, payload, 9U, 8U, 18U);
}
#endif
