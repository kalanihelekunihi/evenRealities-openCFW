/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the four linked G2 pb_service_ring.c entries.
 * Diagnostic-only logging and assertion dispatch are intentionally omitted;
 * the recovered message, nanopb, callback, and transport contracts are kept.
 */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_ring_input;

struct open_cfw_pb_ring_output;
typedef uint32_t (*open_cfw_pb_ring_write_fn)(
    struct open_cfw_pb_ring_output *, const void *, uint32_t);
typedef struct open_cfw_pb_ring_output {
    open_cfw_pb_ring_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_ring_output;

typedef struct {
    uint16_t mac_count;
    uint8_t mac[6];
    uint8_t event_id;
    uint8_t reserved[3];
    uint32_t event_param;
} open_cfw_pb_ring_event;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_ring_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_ring_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif
_Static_assert(sizeof(open_cfw_pb_ring_event) == 16U,
    "G2 ring-event ABI changed");
_Static_assert(offsetof(open_cfw_pb_ring_event, event_id) == 8U,
    "G2 ring-event ID offset changed");
_Static_assert(offsetof(open_cfw_pb_ring_event, event_param) == 12U,
    "G2 ring-event parameter offset changed");

#ifndef OPEN_CFW_PB_RING_MESSAGE_RX
#define OPEN_CFW_PB_RING_MESSAGE_RX ((uint8_t *)(uintptr_t)0x200F86BCU)
#endif
#ifndef OPEN_CFW_PB_RING_MESSAGE_TX
#define OPEN_CFW_PB_RING_MESSAGE_TX ((uint8_t *)(uintptr_t)0x200F86FCU)
#endif
#ifndef OPEN_CFW_PB_RING_ENCODE_BUFFER
#define OPEN_CFW_PB_RING_ENCODE_BUFFER ((uint8_t *)(uintptr_t)0x2037C8A0U)
#endif
#ifndef OPEN_CFW_PB_RING_DESCRIPTOR
#define OPEN_CFW_PB_RING_DESCRIPTOR ((const void *)(uintptr_t)0x0077B104U)
#endif

#ifndef OPEN_CFW_PB_RING_INPUT_FROM_BUFFER
open_cfw_pb_ring_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_RING_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_RING_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_ring_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_RING_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_RING_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_RING_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_RING_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_RING_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_RING_RX_FRAME_ONLY)
#define OPEN_CFW_PB_RING_INCLUDE_RX_FRAME 1
#elif defined(OPEN_CFW_PB_RING_RX_EVENT_ONLY)
#define OPEN_CFW_PB_RING_INCLUDE_RX_EVENT 1
#elif defined(OPEN_CFW_PB_RING_TX_EVENT_ONLY)
#define OPEN_CFW_PB_RING_INCLUDE_TX_EVENT 1
#elif defined(OPEN_CFW_PB_RING_RELAY_ONLY)
#define OPEN_CFW_PB_RING_INCLUDE_RELAY 1
#elif defined(OPEN_CFW_PB_RING_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_RING_INCLUDE_BUFFER_WRITE 1
#else
#define OPEN_CFW_PB_RING_INCLUDE_RX_FRAME 1
#define OPEN_CFW_PB_RING_INCLUDE_RX_EVENT 1
#define OPEN_CFW_PB_RING_INCLUDE_TX_EVENT 1
#define OPEN_CFW_PB_RING_INCLUDE_RELAY 1
#define OPEN_CFW_PB_RING_INCLUDE_BUFFER_WRITE 1
#endif

#if !defined(OPEN_CFW_PB_RING_INCLUDE_BUFFER_WRITE)
uint32_t open_cfw_pb_service_ring_buffer_write(
    open_cfw_pb_ring_output *output, const void *data, uint32_t length);
#endif
#if !defined(OPEN_CFW_PB_RING_INCLUDE_RX_FRAME)
uint32_t APP_PbRxRingFrameDataProcess(const void *data, uint32_t length);
#endif
#if !defined(OPEN_CFW_PB_RING_INCLUDE_RX_EVENT)
uint32_t PB_RxRingEvent(uint32_t sequence, const void *event);
#endif
#if !defined(OPEN_CFW_PB_RING_INCLUDE_TX_EVENT)
uint32_t APP_PbTxEncodeRingEvent(uint32_t sequence, const void *event);
#endif

static __attribute__((always_inline, unused)) inline void open_cfw_pb_ring_zero(
    uint8_t *data, uint32_t length)
{
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

#if defined(OPEN_CFW_PB_RING_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_ring_buffer_write(
    open_cfw_pb_ring_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_RING_INCLUDE_RX_EVENT)
__attribute__((used, noinline))
uint32_t PB_RxRingEvent(uint32_t sequence, const void *raw_event)
{
    const open_cfw_pb_ring_event *event =
        (const open_cfw_pb_ring_event *)raw_event;
    (void)sequence;
    if (event == (const open_cfw_pb_ring_event *)0) {
        return 2U;
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_RING_INCLUDE_TX_EVENT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeRingEvent(uint32_t sequence, const void *raw_event)
{
    const open_cfw_pb_ring_event *event =
        (const open_cfw_pb_ring_event *)raw_event;
    uint8_t *message = OPEN_CFW_PB_RING_MESSAGE_TX;
    uint8_t *buffer = OPEN_CFW_PB_RING_ENCODE_BUFFER;
    open_cfw_pb_ring_output output;
    uint32_t index;
    if (event == (const open_cfw_pb_ring_event *)0) {
        return 2U;
    }
    output.write = open_cfw_pb_service_ring_buffer_write;
    output.context = buffer;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;
    open_cfw_pb_ring_zero(message, 0x40U);
    message[0] = 1U;
    message[1] = (uint8_t)sequence;
    message[2] = 3U;
    message[3] = 0U;
    message[4] = (uint8_t)event->mac_count;
    message[5] = (uint8_t)(event->mac_count >> 8);
    if (event->mac_count > 0U && event->mac_count < 7U) {
        for (index = 0U; index < event->mac_count; ++index) {
            message[6U + index] = event->mac[index];
        }
    }
    message[12] = event->event_id;
    message[16] = (uint8_t)event->event_param;
    message[17] = (uint8_t)(event->event_param >> 8);
    message[18] = (uint8_t)(event->event_param >> 16);
    message[19] = (uint8_t)(event->event_param >> 24);
    message[20] = 0U;
    if (OPEN_CFW_PB_RING_ENCODE(
            &output, OPEN_CFW_PB_RING_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_RING_SEND(
        1U, 0x91U, buffer, (uint16_t)output.length);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_RING_INCLUDE_RX_FRAME)
__attribute__((used, noinline))
uint32_t APP_PbRxRingFrameDataProcess(const void *data, uint32_t length)
{
    uint8_t *message = OPEN_CFW_PB_RING_MESSAGE_RX;
    open_cfw_pb_ring_input input;
    uint32_t status;
    if (data == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_ring_zero(message, 0x40U);
    input = OPEN_CFW_PB_RING_INPUT_FROM_BUFFER(data, (uint16_t)length);
    if (OPEN_CFW_PB_RING_DECODE(
            &input, OPEN_CFW_PB_RING_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    if (message[0] != 1U) {
        return 1U;
    }
    status = PB_RxRingEvent(message[1], message + 4U);
    if (status != 0U) {
        return 1U;
    }
    return APP_PbTxEncodeRingEvent(message[1], message + 4U);
}
#endif

#if defined(OPEN_CFW_PB_RING_INCLUDE_RELAY)
__attribute__((used, noinline))
uint32_t RingDataRelay_common_data_handler(
    uint32_t event_type, const void *data, uint32_t length)
{
    if (event_type == 0U) {
        (void)APP_PbRxRingFrameDataProcess(data, (uint16_t)length);
    }
    return 0U;
}
#endif
