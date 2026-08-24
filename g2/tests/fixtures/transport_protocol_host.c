#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static void *transport_test_services(void);
static void *transport_test_contexts(void);
static uint16_t transport_test_capacity(void);
static void *transport_test_allocate(uint32_t);
static void transport_test_free(void *);
static void *transport_test_mutex_new(const void *);
static int transport_test_mutex_acquire(void *, uint32_t);
static int transport_test_mutex_release(void *);
static uint32_t transport_test_tick(void);
static uint16_t transport_test_crc(
    const uint8_t *, uint32_t, const uint16_t *);
static uint8_t transport_test_remove(const void *);
static void transport_test_push(const void *, void *, uint32_t);
static void *transport_test_controller(void);
static void *transport_test_wsf_allocate(uint32_t);
static void transport_test_wsf_send(uint32_t, void *);

static void *transport_mutex;
static uint8_t transport_timeout_tuple[3];
static uint8_t transport_response_header[8] = {0xaa, 0x02};
static uint8_t transport_send_buffer[4096];
static uint8_t transport_packet_buffer[257];
static const uint8_t transport_header_template[8] = {0xaa, 0x02};

#define OPEN_CFW_TPL_SERVICES \
    ((open_cfw_tpl_service *)transport_test_services())
#define OPEN_CFW_TPL_CONTEXTS \
    ((open_cfw_tpl_context *)transport_test_contexts())
#define OPEN_CFW_TPL_MUTEX_CELL transport_mutex
#define OPEN_CFW_TPL_TIMEOUT_TUPLE transport_timeout_tuple
#define OPEN_CFW_TPL_RESPONSE_HEADER transport_response_header
#define OPEN_CFW_TPL_SEND_BUFFER transport_send_buffer
#define OPEN_CFW_TPL_PACKET_BUFFER transport_packet_buffer
#define OPEN_CFW_TPL_HEADER_TEMPLATE transport_header_template
#define OPEN_CFW_TPL_PAYLOAD_CAPACITY() transport_test_capacity()
#define OPEN_CFW_TPL_ALLOCATE(n) transport_test_allocate((n))
#define OPEN_CFW_TPL_FREE(p) transport_test_free((p))
#define OPEN_CFW_TPL_MUTEX_NEW(a) transport_test_mutex_new((a))
#define OPEN_CFW_TPL_MUTEX_ACQUIRE(m,t) transport_test_mutex_acquire((m),(t))
#define OPEN_CFW_TPL_MUTEX_RELEASE(m) transport_test_mutex_release((m))
#define OPEN_CFW_TPL_TICK_COUNT() transport_test_tick()
#define OPEN_CFW_TPL_CRC16(d,n) transport_test_crc((d),(n),0)
#define OPEN_CFW_TPL_EVENT_REMOVE(c) transport_test_remove((c))
#define OPEN_CFW_TPL_EVENT_PUSH(c,a,m) transport_test_push((c),(a),(m))
#define OPEN_CFW_TPL_CONTROLLER() transport_test_controller()
#define OPEN_CFW_TPL_WSF_ALLOCATE(n) transport_test_wsf_allocate((n))
#define OPEN_CFW_TPL_WSF_SEND(h,m) transport_test_wsf_send((h),(m))

#include "../../components/apollo_main/core_overlay/transport_protocol.c"

static open_cfw_tpl_service transport_services[4];
static open_cfw_tpl_context transport_contexts[4];
static uint8_t transport_controller[0x60];
static uint8_t transport_wsf_message[15];
static uint8_t transmitted[8][257];
static uint16_t transmitted_lengths[8];
static uint32_t transmit_count;
static int8_t transmit_result;
static uint8_t received[4096];
static uint16_t received_length;
static uint8_t received_service;
static uint32_t receive_count;
static uint32_t sync_receive_count;
static uint32_t allocation_count;
static uint32_t free_count;
static uint32_t acquire_count;
static uint32_t release_count;
static uint32_t remove_count;
static uint32_t push_count;
static uint32_t pushed_delay;
static void *pushed_argument;
static uint32_t wsf_send_count;
static uint32_t wsf_handler;
static int acquire_result;

static void *transport_test_services(void) { return transport_services; }
static void *transport_test_contexts(void) { return transport_contexts; }
static uint16_t transport_test_capacity(void) { return 31U; }
static void *transport_test_allocate(uint32_t bytes)
{
    ++allocation_count;
    return calloc(1U, bytes);
}
static void transport_test_free(void *pointer)
{
    ++free_count;
    free(pointer);
}
static void *transport_test_mutex_new(const void *attributes)
{
    assert(attributes == 0);
    return (void *)(uintptr_t)0x1234U;
}
static int transport_test_mutex_acquire(void *mutex, uint32_t timeout)
{
    assert(mutex == (void *)(uintptr_t)0x1234U && timeout == 100U);
    ++acquire_count;
    return acquire_result;
}
static int transport_test_mutex_release(void *mutex)
{
    assert(mutex == (void *)(uintptr_t)0x1234U);
    ++release_count;
    return 0;
}
static uint32_t transport_test_tick(void) { return 0x12345678U; }
static uint16_t transport_test_crc(
    const uint8_t *data, uint32_t length, const uint16_t *seed)
{
    uint16_t crc = seed != 0 ? *seed : 0xffffU;
    uint32_t index;
    unsigned bit;
    for (index = 0; index < length; ++index) {
        crc ^= (uint16_t)data[index] << 8;
        for (bit = 0; bit < 8; ++bit) {
            crc = (uint16_t)((crc & 0x8000U) != 0U ?
                (crc << 1) ^ 0x1021U : crc << 1);
        }
    }
    return crc;
}
static uint8_t transport_test_remove(const void *callback)
{
    assert(callback == _rxNextPacketTimeout);
    ++remove_count;
    return 1U;
}
static void transport_test_push(
    const void *callback, void *argument, uint32_t milliseconds)
{
    assert(callback == _rxNextPacketTimeout);
    ++push_count;
    pushed_argument = argument;
    pushed_delay = milliseconds;
}
static void *transport_test_controller(void) { return transport_controller; }
static void *transport_test_wsf_allocate(uint32_t bytes)
{
    assert(bytes == sizeof(transport_wsf_message));
    memset(transport_wsf_message, 0xcc, sizeof(transport_wsf_message));
    return transport_wsf_message;
}
static void transport_test_wsf_send(uint32_t handler, void *message)
{
    assert(message == transport_wsf_message);
    ++wsf_send_count;
    wsf_handler = handler;
}

static int transport_receive(
    uint8_t service, const uint8_t *data, uint16_t length)
{
    assert(length <= sizeof(received));
    received_service = service;
    received_length = length;
    memcpy(received, data, length);
    ++receive_count;
    return 0;
}

static int transport_sync_receive(uint8_t service, const uint8_t *data,
    uint16_t length, int (*completion)(int, void *, int, void *))
{
    assert(completion(7, 0, 0, 0) == 7);
    ++sync_receive_count;
    return transport_receive(service, data, length);
}

static int8_t transport_transmit(const uint8_t *packet, uint16_t length)
{
    assert(transmit_count < 8U && length <= sizeof(transmitted[0]));
    memcpy(transmitted[transmit_count], packet, length);
    transmitted_lengths[transmit_count] = length;
    ++transmit_count;
    return transmit_result;
}

static void reset_state(void)
{
    unsigned index;
    for (index = 0; index < 4U; ++index) {
        if (transport_contexts[index].active != 0U &&
                transport_contexts[index].storage != 0U) {
            free((void *)transport_contexts[index].storage);
        }
    }
    memset(transport_services, 0, sizeof(transport_services));
    memset(transport_contexts, 0, sizeof(transport_contexts));
    memset(transport_controller, 0, sizeof(transport_controller));
    memset(transport_wsf_message, 0, sizeof(transport_wsf_message));
    memset(transmitted, 0, sizeof(transmitted));
    memset(transmitted_lengths, 0, sizeof(transmitted_lengths));
    memset(received, 0, sizeof(received));
    memset(transport_timeout_tuple, 0, sizeof(transport_timeout_tuple));
    memcpy(transport_response_header, transport_header_template, 8U);
    transport_mutex = 0;
    transmit_count = receive_count = sync_receive_count = 0U;
    allocation_count = free_count = acquire_count = release_count = 0U;
    remove_count = push_count = pushed_delay = 0U;
    pushed_argument = 0;
    wsf_send_count = wsf_handler = 0U;
    received_length = 0U;
    received_service = 0U;
    transmit_result = 0;
    acquire_result = 0;
}

static uint16_t make_packet(uint8_t *packet, uint8_t sequence,
    uint8_t total, uint8_t number, uint8_t service, uint8_t flags,
    const uint8_t *payload, uint8_t length, int append_crc)
{
    uint16_t crc;
    memset(packet, 0, 257U);
    packet[0] = 0xaaU;
    packet[1] = 0x21U;
    packet[2] = sequence;
    packet[3] = (uint8_t)(length + (append_crc ? 2U : 0U));
    packet[4] = total;
    packet[5] = number;
    packet[6] = service;
    packet[7] = flags;
    memcpy(packet + 8U, payload, length);
    if (append_crc) {
        crc = transport_test_crc(payload, length, 0);
        packet[8U + length] = (uint8_t)crc;
        packet[9U + length] = (uint8_t)(crc >> 8);
    }
    return (uint16_t)(8U + packet[3]);
}

int main(void)
{
    uint8_t payload[32];
    uint8_t packet[257];
    uint8_t packet2[257];
    uint16_t length;
    uint16_t crc;
    unsigned index;

    reset_state();
    TPL_Init(0U, transport_sync_receive, transport_receive,
        transport_transmit, transport_transmit);
    assert(transport_mutex == (void *)(uintptr_t)0x1234U);
    assert(transport_services[0].service == 0U);
    assert(transport_services[0].receive == transport_receive);

    for (index = 0; index < 25U; ++index) payload[index] = (uint8_t)index;
    assert(TPL_SendPacket(0U, 1U, 3U, 0x44U, payload, 25U) == 0);
    assert(acquire_count == 1U && release_count == 1U);
    assert(transmit_count == 2U);
    assert(transmitted_lengths[0] == 28U && transmitted_lengths[1] == 15U);
    assert(transmitted[0][0] == 0xaaU && transmitted[0][1] == 0x32U);
    assert(transmitted[0][2] == 0x78U && transmitted[0][4] == 2U);
    assert(transmitted[0][5] == 1U && transmitted[0][6] == 0x44U);
    assert(transmitted[0][7] == 1U && transmitted[0][3] == 20U);
    assert(memcmp(transmitted[0] + 8U, payload, 20U) == 0);
    assert(transmitted[1][3] == 7U && transmitted[1][5] == 2U);
    assert(memcmp(transmitted[1] + 8U, payload + 20U, 5U) == 0);
    crc = transport_test_crc(payload, 25U, 0);
    assert(transmitted[1][13] == (uint8_t)crc);
    assert(transmitted[1][14] == (uint8_t)(crc >> 8));
    assert(TPL_SendPacket(0U, 0U, 0U, 0U, 0, 1U) == 11);
    acquire_result = 1;
    assert(TPL_SendPacket(0U, 0U, 0U, 0U, payload, 1U) == 4);

    reset_state();
    TPL_Init(0U, transport_sync_receive, transport_receive,
        transport_transmit, transport_transmit);
    memcpy(payload, "hello", 5U);
    length = make_packet(packet, 7U, 1U, 1U, 0x55U, 0U,
        payload, 5U, 1);
    assert(TPL_ReceivePacket(0U, packet, length) == 0U);
    assert(receive_count == 1U && sync_receive_count == 0U);
    assert(received_service == 0x55U && received_length == 5U);
    assert(memcmp(received, "hello", 5U) == 0);
    packet[7] = 0x20U;
    assert(TPL_ReceivePacket(0U, packet, length) == 0U);
    assert(sync_receive_count == 1U);
    packet[length - 1U] ^= 1U;
    assert(TPL_ReceivePacket(0U, packet, length) == 1U);
    assert(transmit_count == 1U && transmitted[0][2] == 7U);
    assert(transmitted[0][6] == 0x55U && (transmitted[0][7] & 0x1eU) == 2U);

    reset_state();
    TPL_Init(0U, transport_sync_receive, transport_receive,
        transport_transmit, transport_transmit);
    memcpy(payload, "abcdefghijklmnopqrstuvwxy", 25U);
    length = make_packet(packet, 9U, 2U, 1U, 0x66U, 0U,
        payload, 20U, 0);
    assert(TPL_ReceivePacket(0U, packet, length) == 0U);
    assert(allocation_count == 1U && push_count == 1U);
    assert(pushed_delay == 1500U && pushed_argument == transport_timeout_tuple);
    assert(transport_timeout_tuple[0] == 0x66U);
    assert(TPL_ReceivePacket(0U, packet, length) == 13U);
    crc = transport_test_crc(payload, 25U, 0);
    memcpy(payload + 25U, &crc, 2U);
    length = make_packet(packet2, 9U, 2U, 2U, 0x66U, 0U,
        payload + 20U, 7U, 0);
    assert(TPL_ReceivePacket(0U, packet2, length) == 0U);
    assert(receive_count == 1U && received_length == 25U);
    assert(memcmp(received, payload, 25U) == 0 && free_count == 1U);

    reset_state();
    TPL_Init(0U, transport_sync_receive, transport_receive,
        transport_transmit, transport_transmit);
    length = make_packet(packet, 3U, 2U, 1U, 0x77U, 0U,
        payload, 4U, 0);
    assert(TPL_ReceivePacket(0U, packet, length) == 0U);
    transport_controller[0x56] = 5U;
    _rxNextPacketTimeout(transport_timeout_tuple);
    assert(wsf_send_count == 1U && wsf_handler == 5U);
    assert(transport_wsf_message[2] == 0xb8U);
    assert(transport_wsf_message[8] == 3U && transport_wsf_message[9] == 0U);
    assert(memcmp(transport_wsf_message + 12U,
        transport_timeout_tuple, 3U) == 0);
    TPL_RxPacketTimeoutHandler(transport_timeout_tuple);
    assert(free_count == 1U && transmit_count == 1U);
    assert((transmitted[0][7] & 0x1eU) == 6U);

    reset_state();
    assert(TPL_ReceivePacket(0U, 0, 0U) == 6U);
    memset(packet, 0, sizeof(packet));
    assert(TPL_ReceivePacket(0U, packet, 7U) == 11U);
    packet[0] = 0xaaU; packet[3] = 20U; packet[4] = 1U; packet[5] = 1U;
    assert(TPL_ReceivePacket(0U, packet, 8U) == 11U);
    packet[0] = 0U;
    assert(TPL_ReceivePacket(0U, packet, 8U) == 10U);
    return 0;
}
