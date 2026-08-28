/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 local 0xAA multipart transport.
 * Diagnostic-only EasyLogger calls are intentionally omitted.  The wire
 * format, callback ABI, four-slot reassembly lifecycle, shared timeout,
 * checksum, mutex, and Cordio timeout-message behavior are preserved.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TPL_MAGIC 0xAAU
#define OPEN_CFW_TPL_HEADER_BYTES 8U
#define OPEN_CFW_TPL_CRC_BYTES 2U
#define OPEN_CFW_TPL_MAX_PAYLOAD 4096U
#define OPEN_CFW_TPL_CONTEXT_COUNT 4U
#define OPEN_CFW_TPL_TIMEOUT_MS 1500U
#define OPEN_CFW_TPL_MUTEX_TIMEOUT 100U

typedef int (*open_cfw_tpl_receive_callback)(
    uint8_t service, const uint8_t *data, uint16_t length);
typedef int (*open_cfw_tpl_sync_receive_callback)(
    uint8_t service, const uint8_t *data, uint16_t length,
    int (*completion)(int, void *, int, void *));
typedef int8_t (*open_cfw_tpl_transmit_callback)(
    const uint8_t *packet, uint16_t length);

typedef struct {
    uint8_t service;
    uint8_t reserved[3];
    open_cfw_tpl_sync_receive_callback sync_receive;
    open_cfw_tpl_receive_callback receive;
    open_cfw_tpl_transmit_callback transmit;
    open_cfw_tpl_transmit_callback response_transmit;
} open_cfw_tpl_service;

typedef struct {
    uint8_t service;
    uint8_t sequence;
    uint16_t assembled_length;
    uint8_t source;
    uint8_t destination;
    uint8_t reserved_06[2];
    uintptr_t storage;
#if UINTPTR_MAX == UINT32_MAX
    uint8_t reserved_0c[4];
#endif
    uint8_t packet_bitmap[32];
    uint8_t active;
    uint8_t received_packets;
    uint8_t total_packets;
    uint8_t pipe;
    uint8_t reserved_34[4];
} open_cfw_tpl_context;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_tpl_service) == 20U,
    "G2 transport callback-record ABI changed");
_Static_assert(sizeof(open_cfw_tpl_context) == 56U,
    "G2 transport receive-context ABI changed");
_Static_assert(offsetof(open_cfw_tpl_context, active) == 0x30U,
    "G2 transport receive-context active offset changed");
#endif

#ifndef OPEN_CFW_TPL_SERVICES
#define OPEN_CFW_TPL_SERVICES \
    ((open_cfw_tpl_service *)(uintptr_t)0x20071414U)
#endif
#ifndef OPEN_CFW_TPL_CONTEXTS
#define OPEN_CFW_TPL_CONTEXTS \
    ((open_cfw_tpl_context *)(uintptr_t)0x20070DC8U)
#endif
#ifndef OPEN_CFW_TPL_MUTEX_CELL
#define OPEN_CFW_TPL_MUTEX_CELL \
    (*(void *volatile *)(uintptr_t)0x20074B00U)
#endif
#ifndef OPEN_CFW_TPL_TIMEOUT_TUPLE
#define OPEN_CFW_TPL_TIMEOUT_TUPLE \
    ((volatile uint8_t *)(uintptr_t)0x20074B04U)
#endif
#ifndef OPEN_CFW_TPL_RESPONSE_HEADER
#define OPEN_CFW_TPL_RESPONSE_HEADER \
    ((volatile uint8_t *)(uintptr_t)0x20004204U)
#endif
#ifndef OPEN_CFW_TPL_SEND_BUFFER
#define OPEN_CFW_TPL_SEND_BUFFER \
    ((uint8_t *)(uintptr_t)0x2036FE40U)
#endif
#ifndef OPEN_CFW_TPL_PACKET_BUFFER
#define OPEN_CFW_TPL_PACKET_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037C080U)
#endif
#ifndef OPEN_CFW_TPL_HEADER_TEMPLATE
#define OPEN_CFW_TPL_HEADER_TEMPLATE \
    ((const uint8_t *)(uintptr_t)0x0078EC74U)
#endif

#ifndef OPEN_CFW_TPL_PAYLOAD_CAPACITY
uint16_t open_cfw_tpl_payload_capacity(void);
#define OPEN_CFW_TPL_PAYLOAD_CAPACITY() open_cfw_tpl_payload_capacity()
#endif
#ifndef OPEN_CFW_TPL_ALLOCATE
void *open_cfw_tlsf_malloc(uint32_t bytes);
#define OPEN_CFW_TPL_ALLOCATE(bytes) open_cfw_tlsf_malloc((bytes))
#endif
#ifndef OPEN_CFW_TPL_FREE
void open_cfw_tlsf_free(void *pointer);
#define OPEN_CFW_TPL_FREE(pointer) open_cfw_tlsf_free((pointer))
#endif
#ifndef OPEN_CFW_TPL_MUTEX_NEW
void *open_cfw_cmsis_mutex_new(const void *attributes);
#define OPEN_CFW_TPL_MUTEX_NEW(attributes) \
    open_cfw_cmsis_mutex_new((attributes))
#endif
#ifndef OPEN_CFW_TPL_MUTEX_ACQUIRE
int open_cfw_cmsis_mutex_acquire(void *mutex, uint32_t timeout);
#define OPEN_CFW_TPL_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_cmsis_mutex_acquire((mutex), (timeout))
#endif
#ifndef OPEN_CFW_TPL_MUTEX_RELEASE
int open_cfw_cmsis_mutex_release(void *mutex);
#define OPEN_CFW_TPL_MUTEX_RELEASE(mutex) \
    open_cfw_cmsis_mutex_release((mutex))
#endif
#ifndef OPEN_CFW_TPL_TICK_COUNT
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_TPL_TICK_COUNT() open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_TPL_CRC16
uint16_t open_cfw_crc16_ccitt(
    const uint8_t *data, uint32_t length, const uint16_t *seed);
#define OPEN_CFW_TPL_CRC16(data, length) \
    open_cfw_crc16_ccitt((data), (length), (const uint16_t *)0)
#endif
#ifndef OPEN_CFW_TPL_EVENT_REMOVE
uint8_t open_cfw_event_loop_remove_delayed(const void *callback);
#define OPEN_CFW_TPL_EVENT_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_TPL_EVENT_PUSH
void open_cfw_event_loop_push_delayed(
    const void *callback, void *argument, uint32_t milliseconds);
#define OPEN_CFW_TPL_EVENT_PUSH(callback, argument, milliseconds) \
    open_cfw_event_loop_push_delayed((callback), (argument), (milliseconds))
#endif
#ifndef OPEN_CFW_TPL_CONTROLLER
void *open_cfw_tpl_controller(void);
#define OPEN_CFW_TPL_CONTROLLER() open_cfw_tpl_controller()
#endif
#ifndef OPEN_CFW_TPL_WSF_ALLOCATE
void *open_cfw_cordio_wsf_message_allocate_candidate(uint32_t bytes);
#define OPEN_CFW_TPL_WSF_ALLOCATE(bytes) \
    open_cfw_cordio_wsf_message_allocate_candidate((bytes))
#endif
#ifndef OPEN_CFW_TPL_WSF_SEND
void open_cfw_cordio_wsf_message_send_candidate(
    uint32_t handler, void *message);
#define OPEN_CFW_TPL_WSF_SEND(handler, message) \
    open_cfw_cordio_wsf_message_send_candidate((handler), (message))
#endif

void TPL_Init(uint8_t pipe, open_cfw_tpl_sync_receive_callback sync_receive,
    open_cfw_tpl_receive_callback receive,
    open_cfw_tpl_transmit_callback transmit,
    open_cfw_tpl_transmit_callback response_transmit);
open_cfw_tpl_context *_getOrCreateContext(
    const uint8_t *packet, uint8_t pipe);
void open_cfw_tpl_context_free(open_cfw_tpl_context *context);
void open_cfw_tpl_context_mark_packet(
    open_cfw_tpl_context *context, uint8_t index);
int open_cfw_tpl_context_packet_seen(
    const open_cfw_tpl_context *context, uint8_t index);
void open_cfw_tpl_schedule_rx_timeout(
    uint8_t pipe, uint8_t service, uint8_t sequence);
void _rxNextPacketTimeout(void *argument);
void TPL_RxPacketTimeoutHandler(const uint8_t *tuple);
int _rxSyncEventCallback(int status, void *argument, int event, void *context);
void _tplReponse(
    uint8_t pipe, uint8_t sequence, uint8_t service, uint8_t status);
uint32_t TPL_ReceivePacket(
    uint8_t pipe, const uint8_t *packet, uint16_t packet_length);
int8_t TPL_SendPacket(uint8_t pipe, uint8_t response, uint8_t destination,
    uint8_t service, const uint8_t *payload, uint16_t payload_length);
void open_cfw_tpl_reset_receive_contexts(void);

/*
 * Clang otherwise emits undefined address-taken C declarations as STT_NOTYPE
 * in these independently compiled leaves.  Preserve their Thumb-function
 * identity so strict PREL MOVW/MOVT relocation review can authenticate and
 * set bit zero without weakening the relocation contract.
 */
#if defined(__ELF__)
__asm__(".type _rxNextPacketTimeout,%function\n"
        ".type _rxSyncEventCallback,%function");
#endif

#if defined(OPEN_CFW_TPL_INIT_ONLY)
#define OPEN_CFW_TPL_INCLUDE_INIT 1
#elif defined(OPEN_CFW_TPL_CONTEXT_GET_ONLY)
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_GET 1
#elif defined(OPEN_CFW_TPL_CONTEXT_FREE_ONLY)
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_FREE 1
#elif defined(OPEN_CFW_TPL_CONTEXT_MARK_ONLY)
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_MARK 1
#elif defined(OPEN_CFW_TPL_CONTEXT_SEEN_ONLY)
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_SEEN 1
#elif defined(OPEN_CFW_TPL_SCHEDULE_ONLY)
#define OPEN_CFW_TPL_INCLUDE_SCHEDULE 1
#elif defined(OPEN_CFW_TPL_TIMEOUT_CALLBACK_ONLY)
#define OPEN_CFW_TPL_INCLUDE_TIMEOUT_CALLBACK 1
#elif defined(OPEN_CFW_TPL_TIMEOUT_HANDLER_ONLY)
#define OPEN_CFW_TPL_INCLUDE_TIMEOUT_HANDLER 1
#elif defined(OPEN_CFW_TPL_SYNC_CALLBACK_ONLY)
#define OPEN_CFW_TPL_INCLUDE_SYNC_CALLBACK 1
#elif defined(OPEN_CFW_TPL_RESPONSE_ONLY)
#define OPEN_CFW_TPL_INCLUDE_RESPONSE 1
#elif defined(OPEN_CFW_TPL_RECEIVE_ONLY)
#define OPEN_CFW_TPL_INCLUDE_RECEIVE 1
#elif defined(OPEN_CFW_TPL_SEND_ONLY)
#define OPEN_CFW_TPL_INCLUDE_SEND 1
#elif defined(OPEN_CFW_TPL_RESET_ONLY)
#define OPEN_CFW_TPL_INCLUDE_RESET 1
#else
#define OPEN_CFW_TPL_INCLUDE_INIT 1
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_GET 1
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_FREE 1
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_MARK 1
#define OPEN_CFW_TPL_INCLUDE_CONTEXT_SEEN 1
#define OPEN_CFW_TPL_INCLUDE_SCHEDULE 1
#define OPEN_CFW_TPL_INCLUDE_TIMEOUT_CALLBACK 1
#define OPEN_CFW_TPL_INCLUDE_TIMEOUT_HANDLER 1
#define OPEN_CFW_TPL_INCLUDE_SYNC_CALLBACK 1
#define OPEN_CFW_TPL_INCLUDE_RESPONSE 1
#define OPEN_CFW_TPL_INCLUDE_RECEIVE 1
#define OPEN_CFW_TPL_INCLUDE_SEND 1
#define OPEN_CFW_TPL_INCLUDE_RESET 1
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_tpl_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

static __attribute__((always_inline, unused)) inline void
open_cfw_tpl_copy(void *raw_destination, const void *raw_source,
    uint32_t length)
{
    uint8_t *destination_data = raw_destination;
    const uint8_t *source_data = raw_source;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        destination_data[index] = source_data[index];
    }
}

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_tpl_load16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline void
open_cfw_tpl_store16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline uint8_t *
open_cfw_tpl_context_storage(const open_cfw_tpl_context *context)
{
    return (uint8_t *)context->storage;
}

static __attribute__((always_inline, unused)) inline uint16_t
open_cfw_tpl_fragment_capacity(void)
{
    uint16_t capacity = OPEN_CFW_TPL_PAYLOAD_CAPACITY();
    return capacity > 11U ? (uint16_t)(capacity - 11U) : 0U;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_tpl_dispatch(uint8_t pipe, const uint8_t *packet,
    const uint8_t *payload, uint16_t length)
{
    open_cfw_tpl_service *service = &OPEN_CFW_TPL_SERVICES[0];
    uint8_t response = (uint8_t)((packet[7] >> 5) & 1U);
    if (pipe != 0U) {
        return;
    }
    if (response != 0U && service->sync_receive != 0) {
        (void)service->sync_receive(
            packet[6], payload, length, _rxSyncEventCallback);
    } else if (response == 0U && service->receive != 0) {
        (void)service->receive(packet[6], payload, length);
    }
}

#if defined(OPEN_CFW_TPL_INCLUDE_INIT)
__attribute__((used, noinline))
void TPL_Init(uint8_t pipe, open_cfw_tpl_sync_receive_callback sync_receive,
    open_cfw_tpl_receive_callback receive,
    open_cfw_tpl_transmit_callback transmit,
    open_cfw_tpl_transmit_callback response_transmit)
{
    open_cfw_tpl_service *service = &OPEN_CFW_TPL_SERVICES[pipe];
    service->service = pipe;
    service->sync_receive = sync_receive;
    service->receive = receive;
    service->transmit = transmit;
    service->response_transmit = response_transmit;
    open_cfw_tpl_zero(OPEN_CFW_TPL_CONTEXTS,
        sizeof(open_cfw_tpl_context) * OPEN_CFW_TPL_CONTEXT_COUNT);
    if (OPEN_CFW_TPL_MUTEX_CELL == 0) {
        OPEN_CFW_TPL_MUTEX_CELL = OPEN_CFW_TPL_MUTEX_NEW(0);
    }
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_CONTEXT_GET)
__attribute__((used, noinline, aligned(4)))
open_cfw_tpl_context *_getOrCreateContext(
    const uint8_t *packet, uint8_t pipe)
{
    open_cfw_tpl_context *contexts = OPEN_CFW_TPL_CONTEXTS;
    uint16_t fragment_capacity = open_cfw_tpl_fragment_capacity();
    uint32_t index;
    for (index = 0U; index < OPEN_CFW_TPL_CONTEXT_COUNT; ++index) {
        open_cfw_tpl_context *context = &contexts[index];
        if (context->active != 0U && context->service == packet[6] &&
                context->sequence == packet[2] &&
                context->source == (packet[1] & 0x0FU) &&
                context->destination == (packet[1] >> 4) &&
                context->pipe == pipe) {
            return context;
        }
    }
    if (packet[5] != 1U || fragment_capacity == 0U || packet[4] == 0U) {
        return 0;
    }
    for (index = 0U; index < OPEN_CFW_TPL_CONTEXT_COUNT; ++index) {
        open_cfw_tpl_context *context = &contexts[index];
        uint32_t bytes;
        if (context->active != 0U) {
            continue;
        }
        open_cfw_tpl_zero(context, sizeof(*context));
        context->active = 1U;
        context->service = packet[6];
        context->sequence = packet[2];
        context->source = (uint8_t)(packet[1] & 0x0FU);
        context->destination = (uint8_t)(packet[1] >> 4);
        context->total_packets = packet[4];
        context->pipe = pipe;
        bytes = (uint32_t)fragment_capacity * packet[4];
        context->storage = (uintptr_t)OPEN_CFW_TPL_ALLOCATE(bytes);
        if (context->storage != (uintptr_t)0) {
            return context;
        }
        context->active = 0U;
        return 0;
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_CONTEXT_FREE)
__attribute__((used, noinline))
void open_cfw_tpl_context_free(open_cfw_tpl_context *context)
{
    if (context == 0 || context->active == 0U) {
        return;
    }
    (void)OPEN_CFW_TPL_EVENT_REMOVE(_rxNextPacketTimeout);
    if (context->storage != (uintptr_t)0) {
        OPEN_CFW_TPL_FREE(open_cfw_tpl_context_storage(context));
        context->storage = (uintptr_t)0;
    }
    context->active = 0U;
    open_cfw_tpl_zero(context, 0x32U);
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_CONTEXT_MARK)
__attribute__((used, noinline))
void open_cfw_tpl_context_mark_packet(
    open_cfw_tpl_context *context, uint8_t index)
{
    context->packet_bitmap[index >> 3] |=
        (uint8_t)(1U << (index & 7U));
    ++context->received_packets;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_CONTEXT_SEEN)
__attribute__((used, noinline))
int open_cfw_tpl_context_packet_seen(
    const open_cfw_tpl_context *context, uint8_t index)
{
    return (context->packet_bitmap[index >> 3] &
        (uint8_t)(1U << (index & 7U))) != 0U;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_SCHEDULE)
__attribute__((used, noinline))
void open_cfw_tpl_schedule_rx_timeout(
    uint8_t pipe, uint8_t service, uint8_t sequence)
{
    volatile uint8_t *tuple = OPEN_CFW_TPL_TIMEOUT_TUPLE;
    (void)OPEN_CFW_TPL_EVENT_REMOVE(_rxNextPacketTimeout);
    tuple[0] = service;
    tuple[1] = sequence;
    tuple[2] = pipe;
    OPEN_CFW_TPL_EVENT_PUSH(
        _rxNextPacketTimeout, (void *)(uintptr_t)tuple,
        OPEN_CFW_TPL_TIMEOUT_MS);
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_TIMEOUT_CALLBACK)
__attribute__((used, noinline))
void _rxNextPacketTimeout(void *argument)
{
    uint8_t *controller = OPEN_CFW_TPL_CONTROLLER();
    uint8_t *message;
    if (controller == 0 || controller[0x56] == 0U || argument == 0) {
        return;
    }
    message = OPEN_CFW_TPL_WSF_ALLOCATE(15U);
    if (message == 0) {
        return;
    }
    open_cfw_tpl_zero(message, 15U);
    message[2] = 0xB8U;
    *(uint8_t **)(void *)(message + 4U) = message + 12U;
    open_cfw_tpl_copy(message + 12U, argument, 3U);
    open_cfw_tpl_store16(message + 8U, 3U);
    OPEN_CFW_TPL_WSF_SEND(controller[0x56], message);
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_TIMEOUT_HANDLER)
__attribute__((used, noinline))
void TPL_RxPacketTimeoutHandler(const uint8_t *tuple)
{
    open_cfw_tpl_context *contexts = OPEN_CFW_TPL_CONTEXTS;
    uint32_t index;
    if (tuple == 0) {
        return;
    }
    for (index = 0U; index < OPEN_CFW_TPL_CONTEXT_COUNT; ++index) {
        open_cfw_tpl_context *context = &contexts[index];
        if (context->active != 0U && context->service == tuple[0] &&
                context->sequence == tuple[1] && context->pipe == tuple[2]) {
            open_cfw_tpl_context_free(context);
            break;
        }
    }
    _tplReponse(tuple[2], tuple[1], tuple[0], 3U);
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_SYNC_CALLBACK)
__attribute__((used, noinline))
int _rxSyncEventCallback(
    int status, void *argument, int event, void *context)
{
    (void)argument;
    (void)event;
    (void)context;
    return status;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_RESPONSE)
__attribute__((used, noinline))
void _tplReponse(
    uint8_t pipe, uint8_t sequence, uint8_t service_id, uint8_t status)
{
    volatile uint8_t *header = OPEN_CFW_TPL_RESPONSE_HEADER;
    open_cfw_tpl_service *service = &OPEN_CFW_TPL_SERVICES[0];
    header[2] = sequence;
    header[6] = service_id;
    header[7] = (uint8_t)((header[7] & 0xE1U) |
        ((status & 0x0FU) << 1));
    if (pipe == 0U && service->response_transmit != 0) {
        (void)service->response_transmit((const uint8_t *)header, 8U);
    }
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_RECEIVE)
__attribute__((used, noinline))
uint32_t TPL_ReceivePacket(
    uint8_t pipe, const uint8_t *packet, uint16_t packet_length)
{
    open_cfw_tpl_context *context;
    uint16_t payload_length;
    uint16_t received_crc;
    uint16_t calculated_crc;
    uint8_t packet_number;

    if (packet == 0) {
        open_cfw_tpl_reset_receive_contexts();
        return 6U;
    }
    if (packet_length < OPEN_CFW_TPL_HEADER_BYTES) {
        open_cfw_tpl_reset_receive_contexts();
        return 11U;
    }
    if (packet[0] != OPEN_CFW_TPL_MAGIC) {
        open_cfw_tpl_reset_receive_contexts();
        return 10U;
    }
    if (packet[3] == 0U && packet_length == OPEN_CFW_TPL_HEADER_BYTES) {
        open_cfw_tpl_reset_receive_contexts();
        return 0U;
    }
    if (packet[4] == 0U || packet[5] == 0U || packet[5] > packet[4] ||
            (uint32_t)packet[3] + OPEN_CFW_TPL_HEADER_BYTES > packet_length) {
        open_cfw_tpl_reset_receive_contexts();
        return 11U;
    }
    (void)OPEN_CFW_TPL_EVENT_REMOVE(_rxNextPacketTimeout);
    if (packet[4] == 1U) {
        if (packet[3] < OPEN_CFW_TPL_CRC_BYTES) {
            _tplReponse(pipe, packet[2], packet[6], 1U);
            return 1U;
        }
        payload_length = (uint16_t)(packet[3] - OPEN_CFW_TPL_CRC_BYTES);
        received_crc = open_cfw_tpl_load16(packet + 8U + payload_length);
        calculated_crc = OPEN_CFW_TPL_CRC16(packet + 8U, payload_length);
        if (received_crc == calculated_crc) {
            open_cfw_tpl_dispatch(pipe, packet, packet + 8U, payload_length);
            return 0U;
        }
        _tplReponse(pipe, packet[2], packet[6], 1U);
        return 1U;
    }

    context = _getOrCreateContext(packet, pipe);
    if (context == 0) {
        if (packet[5] < packet[4]) {
            open_cfw_tpl_schedule_rx_timeout(pipe, packet[6], packet[2]);
            return 0U;
        }
        _tplReponse(pipe, packet[2], packet[6], 1U);
        return 1U;
    }
    if (packet[4] != context->total_packets) {
        open_cfw_tpl_context_free(context);
        _tplReponse(pipe, packet[2], packet[6], 1U);
        return 1U;
    }
    packet_number = (uint8_t)(packet[5] - 1U);
    if (open_cfw_tpl_context_packet_seen(context, packet_number)) {
        if (packet[5] < packet[4]) {
            open_cfw_tpl_schedule_rx_timeout(pipe, packet[6], packet[2]);
        } else {
            open_cfw_tpl_context_free(context);
        }
        return 13U;
    }
    if ((uint32_t)context->assembled_length + packet[3] >
            (uint32_t)open_cfw_tpl_fragment_capacity() *
                context->total_packets) {
        open_cfw_tpl_context_free(context);
        _tplReponse(pipe, packet[2], packet[6], 1U);
        return 1U;
    }
    open_cfw_tpl_copy(open_cfw_tpl_context_storage(context) +
        context->assembled_length, packet + 8U, packet[3]);
    open_cfw_tpl_context_mark_packet(context, packet_number);
    context->assembled_length =
        (uint16_t)(context->assembled_length + packet[3]);
    if (packet[5] < packet[4]) {
        open_cfw_tpl_schedule_rx_timeout(pipe, packet[6], packet[2]);
        return 0U;
    }
    if (context->assembled_length < OPEN_CFW_TPL_CRC_BYTES) {
        open_cfw_tpl_context_free(context);
        _tplReponse(pipe, packet[2], packet[6], 1U);
        return 1U;
    }
    context->assembled_length =
        (uint16_t)(context->assembled_length - OPEN_CFW_TPL_CRC_BYTES);
    received_crc = open_cfw_tpl_load16(
        open_cfw_tpl_context_storage(context) + context->assembled_length);
    calculated_crc = OPEN_CFW_TPL_CRC16(
        open_cfw_tpl_context_storage(context), context->assembled_length);
    (void)OPEN_CFW_TPL_EVENT_REMOVE(_rxNextPacketTimeout);
    if (received_crc == calculated_crc) {
        open_cfw_tpl_dispatch(pipe, packet,
            open_cfw_tpl_context_storage(context),
            context->assembled_length);
        open_cfw_tpl_context_free(context);
        return 0U;
    }
    open_cfw_tpl_context_free(context);
    _tplReponse(pipe, packet[2], packet[6], 1U);
    return 1U;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_SEND)
__attribute__((used, noinline))
int8_t TPL_SendPacket(uint8_t pipe, uint8_t response, uint8_t destination,
    uint8_t service_id, const uint8_t *payload, uint16_t payload_length)
{
    uint8_t *send_buffer = OPEN_CFW_TPL_SEND_BUFFER;
    uint8_t *packet = OPEN_CFW_TPL_PACKET_BUFFER;
    open_cfw_tpl_service *service = &OPEN_CFW_TPL_SERVICES[0];
    uint16_t fragment_capacity;
    uint16_t crc;
    uint16_t offset;
    uint16_t fragment_length;
    uint16_t packet_count;
    uint16_t packet_number;
    int8_t result = 0;

    if (payload == 0 || payload_length == 0U ||
            payload_length > OPEN_CFW_TPL_MAX_PAYLOAD) {
        return 11;
    }
    fragment_capacity = open_cfw_tpl_fragment_capacity();
    if (fragment_capacity == 0U || OPEN_CFW_TPL_MUTEX_CELL == 0 ||
            OPEN_CFW_TPL_MUTEX_ACQUIRE(
                OPEN_CFW_TPL_MUTEX_CELL, OPEN_CFW_TPL_MUTEX_TIMEOUT) != 0) {
        return 4;
    }
    open_cfw_tpl_zero(send_buffer, OPEN_CFW_TPL_MAX_PAYLOAD);
    open_cfw_tpl_zero(packet, 257U);
    open_cfw_tpl_copy(send_buffer, payload, payload_length);
    crc = OPEN_CFW_TPL_CRC16(send_buffer, payload_length);
    packet_count = (uint16_t)((payload_length + fragment_capacity - 1U) /
        fragment_capacity);
    open_cfw_tpl_copy(packet, OPEN_CFW_TPL_HEADER_TEMPLATE, 8U);
    packet[1] = (uint8_t)((packet[1] & 0x0FU) | (destination << 4));
    packet[2] = (uint8_t)OPEN_CFW_TPL_TICK_COUNT();
    packet[4] = (uint8_t)packet_count;
    packet[6] = service_id;
    packet[7] = (uint8_t)((packet[7] & 0xFEU) | (response & 1U));
    for (packet_number = 1U; packet_number <= packet_count;
            ++packet_number) {
        offset = (uint16_t)((packet_number - 1U) * fragment_capacity);
        fragment_length = packet_number == packet_count ?
            (uint16_t)(payload_length - offset) : fragment_capacity;
        packet[3] = (uint8_t)(fragment_length +
            (packet_number == packet_count ? OPEN_CFW_TPL_CRC_BYTES : 0U));
        packet[5] = (uint8_t)packet_number;
        open_cfw_tpl_copy(packet + 8U, send_buffer + offset, fragment_length);
        if (packet_number == packet_count) {
            open_cfw_tpl_store16(packet + 8U + fragment_length, crc);
        }
        if (pipe == 0U && service->transmit != 0) {
            result = service->transmit(packet, (uint16_t)(packet[3] + 8U));
        }
        if (result != 0) {
            (void)OPEN_CFW_TPL_MUTEX_RELEASE(OPEN_CFW_TPL_MUTEX_CELL);
            return result;
        }
    }
    (void)OPEN_CFW_TPL_MUTEX_RELEASE(OPEN_CFW_TPL_MUTEX_CELL);
    return 0;
}
#endif

#if defined(OPEN_CFW_TPL_INCLUDE_RESET)
__attribute__((used, noinline))
void open_cfw_tpl_reset_receive_contexts(void)
{
    open_cfw_tpl_context *contexts = OPEN_CFW_TPL_CONTEXTS;
    uint32_t index;
    (void)OPEN_CFW_TPL_EVENT_REMOVE(_rxNextPacketTimeout);
    for (index = 0U; index < OPEN_CFW_TPL_CONTEXT_COUNT; ++index) {
        if (contexts[index].active != 0U) {
            open_cfw_tpl_context_free(&contexts[index]);
        }
    }
}
#endif
