/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the ten linked G2
 * pb_service_quicklist.c entries. Diagnostic-only EasyLogger/assertion
 * construction is omitted; the nanopb layouts, data-manager callbacks,
 * dispatch results, notification sequence, and service-0x0c transports are
 * preserved. The multi-item notification copy is explicitly bounded to the
 * twenty records that fit in the recovered 0x1238-byte message workspace.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_quicklist_input;

struct open_cfw_pb_quicklist_output;
typedef uint32_t (*open_cfw_pb_quicklist_write_fn)(
    struct open_cfw_pb_quicklist_output *, const void *, uint32_t);
typedef struct open_cfw_pb_quicklist_output {
    open_cfw_pb_quicklist_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_quicklist_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_quicklist_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_quicklist_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#define OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES 0x1238U
#define OPEN_CFW_PB_QUICKLIST_ENCODE_CAPACITY 0x400U
#define OPEN_CFW_PB_QUICKLIST_ITEM_STRIDE 0xE8U
#define OPEN_CFW_PB_QUICKLIST_MAX_ITEMS 20U

#ifndef OPEN_CFW_PB_QUICKLIST_MESSAGE_RX
#define OPEN_CFW_PB_QUICKLIST_MESSAGE_RX \
    ((uint8_t *)(uintptr_t)0x200F624CU)
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_MESSAGE_TX
#define OPEN_CFW_PB_QUICKLIST_MESSAGE_TX \
    ((uint8_t *)(uintptr_t)0x200F7484U)
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER
#define OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037A5A0U)
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_DESCRIPTOR
#define OPEN_CFW_PB_QUICKLIST_DESCRIPTOR \
    ((const void *)(uintptr_t)0x0077B02CU)
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE
#define OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE \
    ((volatile uint8_t *)(uintptr_t)0x20074FFDU)
#endif

#ifndef OPEN_CFW_PB_QUICKLIST_INPUT_FROM_BUFFER
open_cfw_pb_quicklist_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_QUICKLIST_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_quicklist_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_QUICKLIST_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_QUICKLIST_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_QUICKLIST_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_QUICKLIST_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_ITEM_RECEIVE
int open_cfw_quicklist_data_manager_load(const void *item);
#define OPEN_CFW_PB_QUICKLIST_ITEM_RECEIVE(item) \
    open_cfw_quicklist_data_manager_load((item))
#endif
#ifndef OPEN_CFW_PB_QUICKLIST_MULTI_RECEIVE
int open_cfw_quicklist_data_manager_save(const void *items);
#define OPEN_CFW_PB_QUICKLIST_MULTI_RECEIVE(items) \
    open_cfw_quicklist_data_manager_save((items))
#endif

uint32_t open_cfw_pb_service_quicklist_buffer_write(
    open_cfw_pb_quicklist_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_quicklist_zero(void *data, uint32_t length);
int open_cfw_pb_service_quicklist_transmit(uint32_t notify);
int APP_PbRxQuicklistFrameDataProcess(const void *data, uint32_t length);
int APP_DecodePbRxQuicklistData(void);
int PB_RxQuicklistItem(uint8_t magic, const uint8_t *payload);
int APP_PbTxEncodeQuicklistItem(uint8_t magic, const uint8_t *payload);
int PB_RxQuicklistMultItems(uint8_t magic, const uint8_t *payload);
int APP_PbTxEncodeQuicklistMultItems(uint8_t magic, const uint8_t *payload);
int APP_PbNotifyEncodeQuicklistMultItems(uint8_t event, const uint8_t *payload);
int PB_RxQuicklistEvent(uint8_t magic, const uint8_t *payload);
int APP_PbTxEncodeQuicklistEvent(uint8_t magic, const uint8_t *payload);
int APP_PbNotifyEncodeQuicklistEvent(uint8_t event, const uint8_t *payload);

#if defined(OPEN_CFW_PB_QUICKLIST_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_QUICKLIST_ZERO_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_ZERO 1
#elif defined(OPEN_CFW_PB_QUICKLIST_TRANSMIT_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TRANSMIT 1
#elif defined(OPEN_CFW_PB_QUICKLIST_RX_FRAME_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_FRAME 1
#elif defined(OPEN_CFW_PB_QUICKLIST_DECODE_DATA_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_DECODE_DATA 1
#elif defined(OPEN_CFW_PB_QUICKLIST_RX_ITEM_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_ITEM 1
#elif defined(OPEN_CFW_PB_QUICKLIST_TX_ITEM_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_ITEM 1
#elif defined(OPEN_CFW_PB_QUICKLIST_RX_MULTI_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_MULTI 1
#elif defined(OPEN_CFW_PB_QUICKLIST_TX_MULTI_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_MULTI 1
#elif defined(OPEN_CFW_PB_QUICKLIST_NOTIFY_MULTI_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_MULTI 1
#elif defined(OPEN_CFW_PB_QUICKLIST_RX_EVENT_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_EVENT 1
#elif defined(OPEN_CFW_PB_QUICKLIST_TX_EVENT_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_EVENT 1
#elif defined(OPEN_CFW_PB_QUICKLIST_NOTIFY_EVENT_ONLY)
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_EVENT 1
#else
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_ZERO 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TRANSMIT 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_FRAME 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_DECODE_DATA 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_ITEM 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_ITEM 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_MULTI 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_MULTI 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_MULTI 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_EVENT 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_EVENT 1
#define OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_EVENT 1
#endif

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_pb_quicklist_load16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_quicklist_load32(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_quicklist_store16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_quicklist_store32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_quicklist_buffer_write(
    open_cfw_pb_quicklist_output *output, const void *raw_data, uint32_t length)
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
    output->length += length;
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_quicklist_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_TRANSMIT)
__attribute__((used, noinline))
int open_cfw_pb_service_quicklist_transmit(uint32_t notify)
{
    open_cfw_pb_quicklist_output output;
    output.write = open_cfw_pb_service_quicklist_buffer_write;
    output.context = OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER;
    output.capacity = OPEN_CFW_PB_QUICKLIST_ENCODE_CAPACITY;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_QUICKLIST_ENCODE(
            &output, OPEN_CFW_PB_QUICKLIST_DESCRIPTOR,
            OPEN_CFW_PB_QUICKLIST_MESSAGE_TX) == 0U) {
        return 0x2B;
    }
    if (notify != 0U) {
        (void)OPEN_CFW_PB_QUICKLIST_NOTIFY(
            1U, 0x0CU, OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER,
            output.length & 0xFFFFU);
    } else {
        (void)OPEN_CFW_PB_QUICKLIST_SEND(
            1U, 0x0CU, OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER,
            output.length & 0xFFFFU);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_DECODE_DATA)
__attribute__((used, noinline))
int APP_DecodePbRxQuicklistData(void)
{
    const uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_RX;
    if (message[0] == 1U) {
        return OPEN_CFW_PB_QUICKLIST_ITEM_RECEIVE(message + 8U);
    }
    if (message[0] == 2U) {
        return OPEN_CFW_PB_QUICKLIST_MULTI_RECEIVE(message + 8U);
    }
    if (message[0] == 3U) {
        /* Stock records invalid values diagnostically but accepts the frame. */
        return 0;
    }
    return 3;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_ITEM)
__attribute__((used, noinline))
int PB_RxQuicklistItem(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    return payload == (const uint8_t *)0 ? 2 : 0;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_ITEM)
__attribute__((used, noinline))
int APP_PbTxEncodeQuicklistItem(uint8_t magic, const uint8_t *payload)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_TX;
    uint32_t index;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    message[0] = 1U;
    message[1] = magic;
    open_cfw_pb_quicklist_store16(message + 2U, 3U);
    for (index = 0U; index < 12U; ++index) {
        message[8U + index] = payload[index];
    }
    message[0xECU] = 0U;
    return open_cfw_pb_service_quicklist_transmit(0U);
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_MULTI)
__attribute__((used, noinline))
int PB_RxQuicklistMultItems(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    return payload == (const uint8_t *)0 ? 2 : 0;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_MULTI)
__attribute__((used, noinline))
int APP_PbTxEncodeQuicklistMultItems(uint8_t magic, const uint8_t *payload)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_TX;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    message[0] = 2U;
    message[1] = magic;
    open_cfw_pb_quicklist_store16(message + 2U, 4U);
    message[8] = payload[0];
    message[9] = payload[1];
    message[0x1230U] = 0U;
    return open_cfw_pb_service_quicklist_transmit(0U);
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_MULTI)
__attribute__((used, noinline, aligned(4)))
int APP_PbNotifyEncodeQuicklistMultItems(
    uint8_t event, const uint8_t *payload)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_TX;
    uint32_t count;
    uint32_t index;
    uint32_t bytes;
    (void)event;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    count = open_cfw_pb_quicklist_load16(payload + 2U);
    if (count > OPEN_CFW_PB_QUICKLIST_MAX_ITEMS) {
        return 1;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    message[0] = 2U;
    message[1] = *OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE;
    *OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE =
        (uint8_t)(*OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE + 1U);
    open_cfw_pb_quicklist_store16(message + 2U, 4U);
    message[8] = payload[0];
    message[9] = payload[1];
    open_cfw_pb_quicklist_store16(message + 10U, (uint16_t)count);
    bytes = count * OPEN_CFW_PB_QUICKLIST_ITEM_STRIDE;
#pragma clang loop vectorize(disable) interleave(disable)
    for (index = 0U; index < bytes; ++index) {
        message[0x10U + index] = payload[8U + index];
    }
    return open_cfw_pb_service_quicklist_transmit(1U);
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_EVENT)
__attribute__((used, noinline))
int PB_RxQuicklistEvent(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    return payload == (const uint8_t *)0 ? 2 : 0;
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_TX_EVENT)
__attribute__((used, noinline))
int APP_PbTxEncodeQuicklistEvent(uint8_t magic, const uint8_t *payload)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_TX;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    message[0] = 3U;
    message[1] = magic;
    open_cfw_pb_quicklist_store16(message + 2U, 5U);
    message[8] = payload[0];
    open_cfw_pb_quicklist_store32(
        message + 12U, open_cfw_pb_quicklist_load32(payload + 4U));
    message[0x10U] = 0U;
    return open_cfw_pb_service_quicklist_transmit(0U);
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_NOTIFY_EVENT)
__attribute__((used, noinline))
int APP_PbNotifyEncodeQuicklistEvent(uint8_t event, const uint8_t *payload)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_TX;
    (void)event;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    message[0] = 3U;
    message[1] = *OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE;
    *OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE =
        (uint8_t)(*OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE + 1U);
    open_cfw_pb_quicklist_store16(message + 2U, 5U);
    message[8] = payload[0];
    open_cfw_pb_quicklist_store32(
        message + 12U, open_cfw_pb_quicklist_load32(payload + 4U));
    return open_cfw_pb_service_quicklist_transmit(1U);
}
#endif

#if defined(OPEN_CFW_PB_QUICKLIST_INCLUDE_RX_FRAME)
__attribute__((used, noinline))
int APP_PbRxQuicklistFrameDataProcess(const void *data, uint32_t length)
{
    uint8_t *message = OPEN_CFW_PB_QUICKLIST_MESSAGE_RX;
    open_cfw_pb_quicklist_input input;
    int status;
    if (data == (const void *)0) {
        return 2;
    }
    open_cfw_pb_service_quicklist_zero(
        message, OPEN_CFW_PB_QUICKLIST_MESSAGE_BYTES);
    input = OPEN_CFW_PB_QUICKLIST_INPUT_FROM_BUFFER(data, length & 0xFFFFU);
    if (OPEN_CFW_PB_QUICKLIST_DECODE(
            &input, OPEN_CFW_PB_QUICKLIST_DESCRIPTOR, message) == 0U) {
        return 0x2B;
    }
    if (message[0] == 1U) {
        status = PB_RxQuicklistItem(message[1], message + 8U);
        return status == 0 ?
            APP_PbTxEncodeQuicklistItem(message[1], message + 8U) : 1;
    }
    if (message[0] == 2U) {
        status = PB_RxQuicklistMultItems(message[1], message + 8U);
        return status == 0 ?
            APP_PbTxEncodeQuicklistMultItems(message[1], message + 8U) : 1;
    }
    if (message[0] == 3U) {
        status = PB_RxQuicklistEvent(message[1], message + 8U);
        return status == 0 ?
            APP_PbTxEncodeQuicklistEvent(message[1], message + 8U) : 1;
    }
    return 1;
}
#endif
