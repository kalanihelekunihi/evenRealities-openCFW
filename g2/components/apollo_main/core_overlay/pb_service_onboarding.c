/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the nine linked G2
 * pb_service_onboarding.c entries. Diagnostic-only EasyLogger calls are
 * omitted; nanopb framing, command dispatch, onboarding-state updates,
 * heartbeat/event normalization, notification sequencing, and BLE transport
 * behavior are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_onboarding_input;

struct open_cfw_pb_onboarding_output;
typedef uint32_t (*open_cfw_pb_onboarding_write_fn)(
    struct open_cfw_pb_onboarding_output *, const void *, uint32_t);
typedef struct open_cfw_pb_onboarding_output {
    open_cfw_pb_onboarding_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_onboarding_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_onboarding_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_onboarding_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_ONBOARDING_DECODED_MESSAGE
#define OPEN_CFW_PB_ONBOARDING_DECODED_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F622CU)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_MESSAGE
#define OPEN_CFW_PB_ONBOARDING_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F623CU)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER
#define OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x200F612CU)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_DESCRIPTOR
#define OPEN_CFW_PB_ONBOARDING_DESCRIPTOR \
    ((const void *)(uintptr_t)0x00779C94U)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE
#define OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE \
    ((uint8_t *)(uintptr_t)0x20074FFBU)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_DISPLAY_READY
#define OPEN_CFW_PB_ONBOARDING_DISPLAY_READY \
    ((const uint8_t *)(uintptr_t)0x20074F2CU)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_PRIMARY_MODE
#define OPEN_CFW_PB_ONBOARDING_PRIMARY_MODE \
    ((const uint32_t *)(uintptr_t)0x200744D8U)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_SECONDARY_MODE
#define OPEN_CFW_PB_ONBOARDING_SECONDARY_MODE \
    ((const uint32_t *)(uintptr_t)0x200744E0U)
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_WEAR_STATE
#define OPEN_CFW_PB_ONBOARDING_WEAR_STATE \
    ((const uint32_t *)(uintptr_t)0x20074EDCU)
#endif

#ifndef OPEN_CFW_PB_ONBOARDING_INPUT_FROM_BUFFER
open_cfw_pb_onboarding_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_ONBOARDING_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_onboarding_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_ONBOARDING_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_ONBOARDING_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_CONTROL_UPDATE
int open_cfw_onboarding_control_update(
    uint32_t command, const uint8_t *payload);
#define OPEN_CFW_PB_ONBOARDING_CONTROL_UPDATE(command, payload) \
    open_cfw_onboarding_control_update((command), (payload))
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_ONBOARDING_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_ONBOARDING_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_ONBOARDING_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_ONBOARDING_ZERO_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_ZERO 1
#elif defined(OPEN_CFW_PB_ONBOARDING_ENCODE_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_ENCODE 1
#elif defined(OPEN_CFW_PB_ONBOARDING_DISPATCH_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_DISPATCH 1
#elif defined(OPEN_CFW_PB_ONBOARDING_RX_CONFIG_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_CONFIG 1
#elif defined(OPEN_CFW_PB_ONBOARDING_TX_CONFIG_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_CONFIG 1
#elif defined(OPEN_CFW_PB_ONBOARDING_NOTIFY_CONFIG_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_CONFIG 1
#elif defined(OPEN_CFW_PB_ONBOARDING_RX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_ONBOARDING_TX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_ONBOARDING_RX_EVENT_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_EVENT 1
#elif defined(OPEN_CFW_PB_ONBOARDING_TX_EVENT_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_EVENT 1
#elif defined(OPEN_CFW_PB_ONBOARDING_NOTIFY_EVENT_ONLY)
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_EVENT 1
#else
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_ZERO 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_ENCODE 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_DISPATCH 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_CONFIG 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_CONFIG 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_CONFIG 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_HEARTBEAT 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_HEARTBEAT 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_EVENT 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_EVENT 1
#define OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_EVENT 1
#endif

uint32_t open_cfw_pb_service_onboarding_buffer_write(
    open_cfw_pb_onboarding_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_onboarding_zero(void *data, uint32_t length);
uint32_t open_cfw_pb_onboarding_encode_and_send(
    uint32_t command, uint32_t magic, const void *payload, uint32_t notify);
uint32_t PB_RxOnboardingConfig(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeOnboardingConfig(uint32_t magic, const void *payload);
uint32_t APP_PbNotifyEncodeOnboardingConfig(
    uint32_t ignored, const void *payload);
uint32_t PB_RxOnboardingHeartbeat(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeOnboardingHeartbeat(
    uint32_t magic, const void *payload);
uint32_t PB_RxOnboardingEvent(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeOnboardingEvent(uint32_t magic, const void *payload);
uint32_t APP_PbNotifyEncodeOnboardingEvent(
    uint32_t ignored, const void *payload);

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_onboarding_buffer_write(
    open_cfw_pb_onboarding_output *output, const void *raw_data,
    uint32_t length)
{
    const uint8_t *data = (const uint8_t *)raw_data;
    uint8_t *destination = (uint8_t *)output->context;
    uint32_t index;
    if (output->length > output->capacity ||
        length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = data[index];
    }
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_onboarding_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_onboarding_copy_u32(uint8_t *destination, const uint8_t *source)
{
    destination[0] = source[0];
    destination[1] = source[1];
    destination[2] = source[2];
    destination[3] = source[3];
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_onboarding_store_u32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
    destination[2] = (uint8_t)(value >> 16);
    destination[3] = (uint8_t)(value >> 24);
}

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_ENCODE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_onboarding_encode_and_send(
    uint32_t command, uint32_t magic, const void *raw_payload,
    uint32_t notify)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t *message = OPEN_CFW_PB_ONBOARDING_MESSAGE;
    open_cfw_pb_onboarding_output output;
    uint32_t state;

    open_cfw_pb_service_onboarding_zero(message, 0x10U);
    message[0] = (uint8_t)command;
    message[1] = (uint8_t)magic;
    message[2] = (uint8_t)(command + 2U);
    message[3] = 0U;

    if (command == 1U) {
        message[4] = payload[0];
        message[5] = 0U;
    } else if (command == 2U) {
        state = 8U;
        if (*OPEN_CFW_PB_ONBOARDING_DISPLAY_READY == 1U &&
            (*OPEN_CFW_PB_ONBOARDING_PRIMARY_MODE == 0x10U ||
             *OPEN_CFW_PB_ONBOARDING_SECONDARY_MODE == 0x10U)) {
            state = 0U;
        }
        message[4] = (uint8_t)state;
    } else {
        message[4] = payload[0];
        if (notify == 0U && payload[0] == 1U) {
            state = (*OPEN_CFW_PB_ONBOARDING_WEAR_STATE == 2U) ? 1U : 0U;
            open_cfw_pb_onboarding_store_u32(message + 8U, state);
        } else {
            open_cfw_pb_onboarding_copy_u32(message + 8U, payload + 4U);
        }
        message[12] = 0U;
    }

    output.write = open_cfw_pb_service_onboarding_buffer_write;
    output.context = OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_ONBOARDING_ENCODE(
            &output, OPEN_CFW_PB_ONBOARDING_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    if (notify == 0U) {
        (void)OPEN_CFW_PB_ONBOARDING_SEND(
            1U, 0x10U, OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER,
            output.length & 0xFFFFU);
    } else {
        (void)OPEN_CFW_PB_ONBOARDING_NOTIFY(
            1U, 0x10U, OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER,
            output.length & 0xFFFFU);
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_CONFIG)
__attribute__((used, noinline))
uint32_t PB_RxOnboardingConfig(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2U;
    }
    (void)OPEN_CFW_PB_ONBOARDING_CONTROL_UPDATE(1U, payload);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_CONFIG)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeOnboardingConfig(
    uint32_t magic, const void *payload)
{
    if (payload == (const void *)0) {
        return 2U;
    }
    return open_cfw_pb_onboarding_encode_and_send(1U, magic, payload, 0U);
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_CONFIG)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeOnboardingConfig(
    uint32_t ignored, const void *payload)
{
    uint32_t magic;
    (void)ignored;
    if (payload == (const void *)0) {
        return 2U;
    }
    magic = *OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE;
    *OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE = (uint8_t)(magic + 1U);
    return open_cfw_pb_onboarding_encode_and_send(1U, magic, payload, 1U);
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_HEARTBEAT)
__attribute__((used, noinline))
uint32_t PB_RxOnboardingHeartbeat(uint32_t magic, const void *payload)
{
    (void)magic;
    return payload == (const void *)0 ? 2U : 0U;
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_HEARTBEAT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeOnboardingHeartbeat(
    uint32_t magic, const void *payload)
{
    if (payload == (const void *)0) {
        return 2U;
    }
    return open_cfw_pb_onboarding_encode_and_send(2U, magic, payload, 0U);
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_RX_EVENT)
__attribute__((used, noinline))
uint32_t PB_RxOnboardingEvent(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2U;
    }
    (void)OPEN_CFW_PB_ONBOARDING_CONTROL_UPDATE(3U, payload);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_TX_EVENT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeOnboardingEvent(
    uint32_t magic, const void *payload)
{
    if (payload == (const void *)0) {
        return 2U;
    }
    return open_cfw_pb_onboarding_encode_and_send(3U, magic, payload, 0U);
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_NOTIFY_EVENT)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeOnboardingEvent(
    uint32_t ignored, const void *payload)
{
    uint32_t magic;
    (void)ignored;
    if (payload == (const void *)0) {
        return 2U;
    }
    magic = *OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE;
    *OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE = (uint8_t)(magic + 1U);
    return open_cfw_pb_onboarding_encode_and_send(3U, magic, payload, 1U);
}
#endif

#if defined(OPEN_CFW_PB_ONBOARDING_INCLUDE_DISPATCH)
__attribute__((used, noinline))
uint32_t APP_PbRxOnboardingFrameDataProcess(
    const void *data, uint32_t length)
{
    uint8_t *message = OPEN_CFW_PB_ONBOARDING_DECODED_MESSAGE;
    open_cfw_pb_onboarding_input input;
    uint32_t status;

    if (data == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_service_onboarding_zero(message, 0x10U);
    input = OPEN_CFW_PB_ONBOARDING_INPUT_FROM_BUFFER(data, length & 0xFFFFU);
    if (OPEN_CFW_PB_ONBOARDING_DECODE(
            &input, OPEN_CFW_PB_ONBOARDING_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }

    if (message[0] == 1U) {
        status = PB_RxOnboardingConfig(message[1], message + 4U);
        return status == 0U
            ? APP_PbTxEncodeOnboardingConfig(message[1], message + 4U) : 1U;
    }
    if (message[0] == 2U) {
        status = PB_RxOnboardingHeartbeat(message[1], message + 4U);
        return status == 0U
            ? APP_PbTxEncodeOnboardingHeartbeat(message[1], message + 4U) : 1U;
    }
    if (message[0] == 3U) {
        status = PB_RxOnboardingEvent(message[1], message + 4U);
        return status == 0U
            ? APP_PbTxEncodeOnboardingEvent(message[1], message + 4U) : 1U;
    }
    return 1U;
}
#endif
