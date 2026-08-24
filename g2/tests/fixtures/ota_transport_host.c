#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static uint16_t ota_test_payload_capacity(void);
static uint16_t ota_test_crc(
    const uint8_t *, uint32_t, const uint16_t *);
static void ota_test_free(void *);
static uint8_t ota_test_remove(const void *);
static void ota_test_push(const void *, void *, uint32_t);
static void ota_test_reply_crc(uint8_t);
static void ota_test_reply_resources(uint8_t);
static void ota_timeout(void *);
static int ota_receive(uint8_t, const uint8_t *, uint16_t);
static int8_t ota_transmit(const uint8_t *, uint16_t);

static uint32_t ota_total_rx;
static uint8_t *ota_receive_buffer;
static uint8_t ota_authenticated;
static uint8_t ota_error_pending;
static uint8_t ota_error_sequence;
static uint8_t ota_last_sequence;
static uint8_t *ota_default_receive_buffer;
static uint8_t *ota_send_buffer;
static uint8_t *ota_packet_buffer;
static int (*ota_receive_callback)(uint8_t, const uint8_t *, uint16_t);
static int8_t (*ota_transmit_callback)(const uint8_t *, uint16_t);
static uint32_t ota_transfer_state;
static const uint8_t ota_header_template[8] = {0xaa, 0x02};

#define OPEN_CFW_OTA_TOTAL_RX ota_total_rx
#define OPEN_CFW_OTA_RECEIVE_BUFFER ota_receive_buffer
#define OPEN_CFW_OTA_AUTHENTICATED ota_authenticated
#define OPEN_CFW_OTA_ERROR_PENDING ota_error_pending
#define OPEN_CFW_OTA_ERROR_SEQUENCE ota_error_sequence
#define OPEN_CFW_OTA_LAST_SEQUENCE ota_last_sequence
#define OPEN_CFW_OTA_DEFAULT_RECEIVE_BUFFER ota_default_receive_buffer
#define OPEN_CFW_OTA_SEND_BUFFER ota_send_buffer
#define OPEN_CFW_OTA_PACKET_BUFFER ota_packet_buffer
#define OPEN_CFW_OTA_RECEIVE_CALLBACK ota_receive_callback
#define OPEN_CFW_OTA_TRANSMIT_CALLBACK ota_transmit_callback
#define OPEN_CFW_OTA_HEADER_TEMPLATE ota_header_template
#define OPEN_CFW_OTA_TRANSFER_STATE ota_transfer_state
#define OPEN_CFW_OTA_TIMEOUT_CALLBACK ota_timeout
#define OPEN_CFW_OTA_PAYLOAD_CAPACITY() ota_test_payload_capacity()
#define OPEN_CFW_OTA_CRC16(data, length) ota_test_crc((data), (length), 0)
#define OPEN_CFW_OTA_FREE(pointer) ota_test_free((pointer))
#define OPEN_CFW_OTA_EVENT_REMOVE(callback) ota_test_remove((callback))
#define OPEN_CFW_OTA_EVENT_PUSH(callback, argument, milliseconds) \
    ota_test_push((callback), (argument), (milliseconds))
#define OPEN_CFW_OTA_REPLY_CRC_ERROR(command) ota_test_reply_crc((command))
#define OPEN_CFW_OTA_REPLY_NO_RESOURCES(command) \
    ota_test_reply_resources((command))

#include "../../components/apollo_main/core_overlay/ota_transport.c"

static uint8_t ota_default_buffer[OPEN_CFW_OTA_BUFFER_BYTES];
static uint8_t ota_tx_buffer[OPEN_CFW_OTA_BUFFER_BYTES];
static uint8_t ota_fragment_buffer[OPEN_CFW_OTA_PACKET_BUFFER_BYTES];
static uint8_t ota_received[OPEN_CFW_OTA_BUFFER_BYTES];
static uint16_t ota_received_length;
static uint8_t ota_received_command;
static unsigned ota_receive_count;
static unsigned ota_free_count;
static unsigned ota_remove_count;
static unsigned ota_push_count;
static uint32_t ota_push_delay;
static unsigned ota_crc_reply_count;
static unsigned ota_resource_reply_count;
static uint8_t ota_reply_command;
static uint8_t ota_transmitted[8][OPEN_CFW_OTA_PACKET_BUFFER_BYTES];
static uint16_t ota_transmitted_length[8];
static unsigned ota_transmit_count;
static int8_t ota_transmit_result;

static uint16_t ota_test_payload_capacity(void) { return 31U; }

static uint16_t ota_test_crc(
    const uint8_t *data, uint32_t length, const uint16_t *seed)
{
    uint16_t crc = seed != 0 ? *seed : 0xffffU;
    uint32_t index;
    unsigned bit;
    for (index = 0U; index < length; ++index) {
        crc ^= (uint16_t)data[index] << 8;
        for (bit = 0U; bit < 8U; ++bit) {
            crc = (uint16_t)((crc & 0x8000U) != 0U ?
                (crc << 1) ^ 0x1021U : crc << 1);
        }
    }
    return crc;
}

static void ota_test_free(void *pointer)
{
    ++ota_free_count;
    free(pointer);
}

static uint8_t ota_test_remove(const void *callback)
{
    assert(callback == (const void *)ota_timeout);
    ++ota_remove_count;
    return 1U;
}

static void ota_test_push(
    const void *callback, void *argument, uint32_t milliseconds)
{
    assert(callback == (const void *)ota_timeout);
    assert(argument == 0);
    ++ota_push_count;
    ota_push_delay = milliseconds;
}

static void ota_test_reply_crc(uint8_t command)
{
    ++ota_crc_reply_count;
    ota_reply_command = command;
}

static void ota_test_reply_resources(uint8_t command)
{
    ++ota_resource_reply_count;
    ota_reply_command = command;
}

static void ota_timeout(void *argument) { assert(argument == 0); }

static int ota_receive(
    uint8_t command, const uint8_t *data, uint16_t length)
{
    assert(length <= sizeof(ota_received));
    memcpy(ota_received, data, length);
    ota_received_command = command;
    ota_received_length = length;
    ++ota_receive_count;
    return 0;
}

static int8_t ota_transmit(const uint8_t *packet, uint16_t length)
{
    assert(ota_transmit_count < 8U);
    assert(length <= sizeof(ota_transmitted[0]));
    memcpy(ota_transmitted[ota_transmit_count], packet, length);
    ota_transmitted_length[ota_transmit_count] = length;
    ++ota_transmit_count;
    return ota_transmit_result;
}

static void reset_state(void)
{
    memset(ota_default_buffer, 0xa5, sizeof(ota_default_buffer));
    memset(ota_tx_buffer, 0, sizeof(ota_tx_buffer));
    memset(ota_fragment_buffer, 0, sizeof(ota_fragment_buffer));
    memset(ota_received, 0, sizeof(ota_received));
    memset(ota_transmitted, 0, sizeof(ota_transmitted));
    memset(ota_transmitted_length, 0, sizeof(ota_transmitted_length));
    ota_total_rx = 0U;
    ota_receive_buffer = ota_default_buffer;
    ota_authenticated = ota_error_pending = ota_error_sequence = 0U;
    ota_last_sequence = 0U;
    ota_default_receive_buffer = ota_default_buffer;
    ota_send_buffer = ota_tx_buffer;
    ota_packet_buffer = ota_fragment_buffer;
    ota_receive_callback = ota_receive;
    ota_transmit_callback = ota_transmit;
    ota_transfer_state = 0x12345678U;
    ota_received_length = 0U;
    ota_received_command = 0U;
    ota_receive_count = ota_free_count = ota_remove_count = 0U;
    ota_push_count = ota_crc_reply_count = ota_resource_reply_count = 0U;
    ota_push_delay = 0U;
    ota_reply_command = 0U;
    ota_transmit_count = 0U;
    ota_transmit_result = 0;
}

static uint16_t make_packet(uint8_t *packet, uint8_t sequence,
    uint8_t total, uint8_t number, uint8_t command, uint8_t flags,
    const uint8_t *payload, uint8_t payload_length, int append_crc)
{
    uint16_t crc;
    memset(packet, 0, OPEN_CFW_OTA_PACKET_BUFFER_BYTES);
    packet[0] = OPEN_CFW_OTA_MAGIC;
    packet[1] = 0x21U;
    packet[2] = sequence;
    packet[3] = (uint8_t)(payload_length + (append_crc ? 2U : 0U));
    packet[4] = total;
    packet[5] = number;
    packet[6] = command;
    packet[7] = flags;
    memcpy(packet + 8U, payload, payload_length);
    if (append_crc) {
        crc = ota_test_crc(payload, payload_length, 0);
        packet[8U + payload_length] = (uint8_t)crc;
        packet[9U + payload_length] = (uint8_t)(crc >> 8);
    }
    return (uint16_t)(OPEN_CFW_OTA_HEADER_BYTES + packet[3]);
}

int main(void)
{
    uint8_t packet[OPEN_CFW_OTA_PACKET_BUFFER_BYTES];
    uint8_t first[12];
    uint8_t second[10];
    uint8_t complete[20];
    uint8_t payload[35];
    uint16_t length;
    uint16_t crc;
    unsigned index;

    reset_state();
    first[0] = 2U;
    first[1] = 9U;
    length = make_packet(packet, 4U, 1U, 1U,
        OPEN_CFW_OTA_COMMAND_START, 0U, first, 2U, 1);
    assert(OTA_ReceivePacket(packet, length) == 0U);
    assert(ota_authenticated == 1U && ota_last_sequence == 4U);
    assert(ota_receive_count == 1U && ota_received_command == 0xc0U);
    assert(ota_received_length == 2U && memcmp(ota_received, first, 2U) == 0);
    assert(ota_receive_buffer == ota_default_buffer && ota_total_rx == 0U);
    for (index = 0U; index < sizeof(ota_default_buffer); ++index) {
        assert(ota_default_buffer[index] == 0U);
    }

    reset_state();
    length = make_packet(packet, 7U, 1U, 1U,
        OPEN_CFW_OTA_COMMAND_CONTROL, 0U, first, 2U, 1);
    packet[length - 1U] ^= 0x40U;
    assert(OTA_ReceivePacket(packet, length) == 0U);
    assert(ota_receive_count == 0U && ota_crc_reply_count == 1U);
    assert(ota_error_pending == 1U && ota_error_sequence == 7U);
    assert(OTA_ReceivePacket(packet, length) == 0U);
    assert(ota_crc_reply_count == 2U);

    reset_state();
    for (index = 0U; index < sizeof(complete); ++index) {
        complete[index] = (uint8_t)(index + 1U);
    }
    memcpy(first, complete, sizeof(first));
    memcpy(second, complete + sizeof(first), 8U);
    crc = ota_test_crc(complete, sizeof(complete), 0);
    second[8] = (uint8_t)crc;
    second[9] = (uint8_t)(crc >> 8);
    length = make_packet(packet, 9U, 2U, 1U,
        OPEN_CFW_OTA_COMMAND_DATA, 0U, first, sizeof(first), 0);
    assert(OTA_ReceivePacket(packet, length) == 0U);
    assert(ota_push_count == 1U && ota_push_delay == 1500U);
    length = make_packet(packet, 9U, 2U, 2U,
        OPEN_CFW_OTA_COMMAND_DATA, 0U, second, sizeof(second), 0);
    assert(OTA_ReceivePacket(packet, length) == 0U);
    assert(ota_receive_count == 1U && ota_received_command == 0xc1U);
    assert(ota_received_length == sizeof(complete));
    assert(memcmp(ota_received, complete, sizeof(complete)) == 0);
    assert(ota_receive_buffer == 0 && ota_total_rx == 0U);

    reset_state();
    ota_receive_buffer = malloc(OPEN_CFW_OTA_BUFFER_BYTES);
    assert(ota_receive_buffer != 0);
    length = make_packet(packet, 10U, 1U, 1U,
        OPEN_CFW_OTA_COMMAND_DATA, 0U, first, 2U, 1);
    packet[length - 1U] ^= 1U;
    assert(OTA_ReceivePacket(packet, length) == 1U);
    assert(ota_free_count == 1U && ota_receive_buffer == 0);
    assert(ota_crc_reply_count == 1U && ota_reply_command == 0xc1U);

    reset_state();
    assert(OTA_ReceivePacket(0, 0U) == 11U);
    memset(packet, 0, sizeof(packet));
    assert(OTA_ReceivePacket(packet, 7U) == 11U);
    packet[0] = 0x55U;
    assert(OTA_ReceivePacket(packet, 8U) == 10U);

    reset_state();
    for (index = 0U; index < sizeof(payload); ++index) {
        payload[index] = (uint8_t)(0x80U + index);
    }
    ota_last_sequence = 0x44U;
    assert(OTA_SendPacket(1U, 3U, 0xc2U,
        payload, sizeof(payload)) == 0);
    assert(ota_transmit_count == 2U);
    assert(ota_transmitted_length[0] == 28U);
    assert(ota_transmitted_length[1] == 25U);
    assert(ota_transmitted[0][0] == 0xaaU);
    assert(ota_transmitted[0][1] == 0x32U);
    assert(ota_transmitted[0][2] == 0x44U);
    assert(ota_transmitted[0][3] == 20U);
    assert(ota_transmitted[0][4] == 2U && ota_transmitted[0][5] == 1U);
    assert(ota_transmitted[0][6] == 0xc2U && ota_transmitted[0][7] == 1U);
    assert(memcmp(ota_transmitted[0] + 8U, payload, 20U) == 0);
    assert(ota_transmitted[1][3] == 17U && ota_transmitted[1][5] == 2U);
    assert(memcmp(ota_transmitted[1] + 8U, payload + 20U, 15U) == 0);
    crc = ota_test_crc(payload, sizeof(payload), 0);
    assert(ota_transmitted[1][23] == (uint8_t)crc);
    assert(ota_transmitted[1][24] == (uint8_t)(crc >> 8));

    reset_state();
    ota_transmit_result = -6;
    assert(OTA_SendPacket(0U, 1U, 0xc0U, payload, 1U) == -6);
    assert(ota_transmit_count == 1U);
    assert(OTA_SendPacket(0U, 0U, 0U, 0, 1U) == 11);
    assert(OTA_SendPacket(0U, 0U, 0U, payload, 0U) == 11);
    assert(OTA_GetTransferState() == 0x12345678U);

    reset_state();
    ota_default_receive_buffer = 0;
    length = make_packet(packet, 12U, 1U, 1U,
        OPEN_CFW_OTA_COMMAND_START, 0U, first, 1U, 1);
    first[0] = packet[8];
    packet[8] = 2U;
    crc = ota_test_crc(packet + 8U, 1U, 0);
    packet[9] = (uint8_t)crc;
    packet[10] = (uint8_t)(crc >> 8);
    assert(OTA_ReceivePacket(packet, length) == 4U);
    assert(ota_resource_reply_count == 1U);

    return 0;
}
