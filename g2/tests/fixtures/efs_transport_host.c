#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static uint16_t efs_test_payload_capacity(void);
static uint16_t efs_test_crc(
    const uint8_t *, uint32_t, const uint16_t *);
static void efs_test_free(void *);
static uint8_t efs_test_remove(const void *);
static void efs_test_push(const void *, void *, uint32_t);
static void efs_test_reply_crc(uint8_t);
static void efs_test_reply_resources(uint8_t);
static uint32_t efs_test_kernel_tick(void);
static void efs_timeout(void *);
static int efs_receive(uint8_t, const uint8_t *, uint16_t);
static int8_t efs_transmit(const uint8_t *, uint16_t);

static uint32_t efs_total_rx;
static uint8_t *efs_receive_buffer;
static uint8_t efs_authenticated;
static uint8_t efs_error_pending;
static uint8_t efs_error_sequence;
static uint8_t *efs_default_receive_buffer;
static uint8_t *efs_send_buffer;
static uint8_t *efs_packet_buffer;
static int (*efs_receive_callback)(uint8_t, const uint8_t *, uint16_t);
static int8_t (*efs_transmit_callback)(const uint8_t *, uint16_t);
static const uint8_t efs_header_template[8] = {0xaa, 0x02};

#define OPEN_CFW_EFS_TOTAL_RX efs_total_rx
#define OPEN_CFW_EFS_RECEIVE_BUFFER efs_receive_buffer
#define OPEN_CFW_EFS_AUTHENTICATED efs_authenticated
#define OPEN_CFW_EFS_ERROR_PENDING efs_error_pending
#define OPEN_CFW_EFS_ERROR_SEQUENCE efs_error_sequence
#define OPEN_CFW_EFS_DEFAULT_RECEIVE_BUFFER efs_default_receive_buffer
#define OPEN_CFW_EFS_SEND_BUFFER efs_send_buffer
#define OPEN_CFW_EFS_PACKET_BUFFER efs_packet_buffer
#define OPEN_CFW_EFS_RECEIVE_CALLBACK efs_receive_callback
#define OPEN_CFW_EFS_TRANSMIT_CALLBACK efs_transmit_callback
#define OPEN_CFW_EFS_HEADER_TEMPLATE efs_header_template
#define OPEN_CFW_EFS_TIMEOUT_CALLBACK efs_timeout
#define OPEN_CFW_EFS_KERNEL_TICK() efs_test_kernel_tick()
#define OPEN_CFW_EFS_PAYLOAD_CAPACITY() efs_test_payload_capacity()
#define OPEN_CFW_EFS_CRC16(data, length) efs_test_crc((data), (length), 0)
#define OPEN_CFW_EFS_FREE(pointer) efs_test_free((pointer))
#define OPEN_CFW_EFS_EVENT_REMOVE(callback) efs_test_remove((callback))
#define OPEN_CFW_EFS_EVENT_PUSH(callback, argument, milliseconds) \
    efs_test_push((callback), (argument), (milliseconds))
#define OPEN_CFW_EFS_REPLY_CRC_ERROR(command) efs_test_reply_crc((command))
#define OPEN_CFW_EFS_REPLY_NO_RESOURCES(command) \
    efs_test_reply_resources((command))

#include "../../components/apollo_main/core_overlay/efs_transport.c"

static uint8_t efs_default_buffer[OPEN_CFW_EFS_BUFFER_BYTES];
static uint8_t efs_tx_buffer[OPEN_CFW_EFS_BUFFER_BYTES];
static uint8_t efs_fragment_buffer[OPEN_CFW_EFS_PACKET_BUFFER_BYTES];
static uint8_t efs_received[OPEN_CFW_EFS_BUFFER_BYTES];
static uint16_t efs_received_length;
static uint8_t efs_received_command;
static unsigned efs_receive_count;
static unsigned efs_free_count;
static unsigned efs_remove_count;
static unsigned efs_push_count;
static uint32_t efs_push_delay;
static unsigned efs_crc_reply_count;
static unsigned efs_resource_reply_count;
static uint8_t efs_reply_command;
static uint8_t efs_transmitted[8][OPEN_CFW_EFS_PACKET_BUFFER_BYTES];
static uint16_t efs_transmitted_length[8];
static unsigned efs_transmit_count;
static int8_t efs_transmit_result;

static uint16_t efs_test_payload_capacity(void) { return 31U; }
static uint32_t efs_test_kernel_tick(void) { return 0x12345678U; }

static uint16_t efs_test_crc(
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

static void efs_test_free(void *pointer)
{
    ++efs_free_count;
    free(pointer);
}

static uint8_t efs_test_remove(const void *callback)
{
    assert(callback == (const void *)efs_timeout);
    ++efs_remove_count;
    return 1U;
}

static void efs_test_push(
    const void *callback, void *argument, uint32_t milliseconds)
{
    assert(callback == (const void *)efs_timeout);
    assert(argument == 0);
    ++efs_push_count;
    efs_push_delay = milliseconds;
}

static void efs_test_reply_crc(uint8_t command)
{
    ++efs_crc_reply_count;
    efs_reply_command = command;
}

static void efs_test_reply_resources(uint8_t command)
{
    ++efs_resource_reply_count;
    efs_reply_command = command;
}

static void efs_timeout(void *argument) { assert(argument == 0); }

static int efs_receive(
    uint8_t command, const uint8_t *data, uint16_t length)
{
    assert(length <= sizeof(efs_received));
    memcpy(efs_received, data, length);
    efs_received_command = command;
    efs_received_length = length;
    ++efs_receive_count;
    return 0;
}

static int8_t efs_transmit(const uint8_t *packet, uint16_t length)
{
    assert(efs_transmit_count < 8U);
    assert(length <= sizeof(efs_transmitted[0]));
    memcpy(efs_transmitted[efs_transmit_count], packet, length);
    efs_transmitted_length[efs_transmit_count] = length;
    ++efs_transmit_count;
    return efs_transmit_result;
}

static void reset_state(void)
{
    memset(efs_default_buffer, 0xa5, sizeof(efs_default_buffer));
    memset(efs_tx_buffer, 0, sizeof(efs_tx_buffer));
    memset(efs_fragment_buffer, 0, sizeof(efs_fragment_buffer));
    memset(efs_received, 0, sizeof(efs_received));
    memset(efs_transmitted, 0, sizeof(efs_transmitted));
    memset(efs_transmitted_length, 0, sizeof(efs_transmitted_length));
    efs_total_rx = 0U;
    efs_receive_buffer = efs_default_buffer;
    efs_authenticated = efs_error_pending = efs_error_sequence = 0U;
    efs_default_receive_buffer = efs_default_buffer;
    efs_send_buffer = efs_tx_buffer;
    efs_packet_buffer = efs_fragment_buffer;
    efs_receive_callback = efs_receive;
    efs_transmit_callback = efs_transmit;
    efs_received_length = 0U;
    efs_received_command = 0U;
    efs_receive_count = efs_free_count = efs_remove_count = 0U;
    efs_push_count = efs_crc_reply_count = efs_resource_reply_count = 0U;
    efs_push_delay = 0U;
    efs_reply_command = 0U;
    efs_transmit_count = 0U;
    efs_transmit_result = 0;
}

static uint16_t make_packet(uint8_t *packet, uint8_t sequence,
    uint8_t total, uint8_t number, uint8_t command, uint8_t flags,
    const uint8_t *payload, uint8_t payload_length, int append_crc)
{
    uint16_t crc;
    memset(packet, 0, OPEN_CFW_EFS_PACKET_BUFFER_BYTES);
    packet[0] = OPEN_CFW_EFS_MAGIC;
    packet[1] = 0x21U;
    packet[2] = sequence;
    packet[3] = (uint8_t)(payload_length + (append_crc ? 2U : 0U));
    packet[4] = total;
    packet[5] = number;
    packet[6] = command;
    packet[7] = flags;
    memcpy(packet + 8U, payload, payload_length);
    if (append_crc) {
        crc = efs_test_crc(payload, payload_length, 0);
        packet[8U + payload_length] = (uint8_t)crc;
        packet[9U + payload_length] = (uint8_t)(crc >> 8);
    }
    return (uint16_t)(OPEN_CFW_EFS_HEADER_BYTES + packet[3]);
}

int main(void)
{
    uint8_t packet[OPEN_CFW_EFS_PACKET_BUFFER_BYTES];
    uint8_t first[12];
    uint8_t second[10];
    uint8_t complete[20];
    uint8_t payload[35];
    uint16_t length;
    uint16_t crc;
    unsigned index;

    reset_state();
    first[0] = 1U;
    first[1] = 9U;
    length = make_packet(packet, 4U, 1U, 1U,
        OPEN_CFW_EFS_COMMAND_START, 0U, first, 2U, 1);
    assert(EFS_ReceivePacket(packet, length) == 0U);
    assert(efs_authenticated == 1U);
    assert(efs_receive_count == 1U && efs_received_command == 0xc4U);
    assert(efs_received_length == 2U && memcmp(efs_received, first, 2U) == 0);
    assert(efs_receive_buffer == efs_default_buffer && efs_total_rx == 0U);
    for (index = 0U; index < sizeof(efs_default_buffer); ++index) {
        assert(efs_default_buffer[index] == 0U);
    }

    reset_state();
    length = make_packet(packet, 7U, 1U, 1U,
        OPEN_CFW_EFS_COMMAND_CONTROL, 0U, first, 2U, 1);
    packet[length - 1U] ^= 0x40U;
    assert(EFS_ReceivePacket(packet, length) == 0U);
    assert(efs_receive_count == 0U && efs_crc_reply_count == 1U);
    assert(efs_error_pending == 1U && efs_error_sequence == 7U);
    assert(EFS_ReceivePacket(packet, length) == 0U);
    assert(efs_crc_reply_count == 2U);

    reset_state();
    for (index = 0U; index < sizeof(complete); ++index) {
        complete[index] = (uint8_t)(index + 1U);
    }
    memcpy(first, complete, sizeof(first));
    memcpy(second, complete + sizeof(first), 8U);
    crc = efs_test_crc(complete, sizeof(complete), 0);
    second[8] = (uint8_t)crc;
    second[9] = (uint8_t)(crc >> 8);
    length = make_packet(packet, 9U, 2U, 1U,
        OPEN_CFW_EFS_COMMAND_DATA, 0U, first, sizeof(first), 0);
    assert(EFS_ReceivePacket(packet, length) == 0U);
    assert(efs_push_count == 1U && efs_push_delay == 1500U);
    length = make_packet(packet, 9U, 2U, 2U,
        OPEN_CFW_EFS_COMMAND_DATA, 0U, second, sizeof(second), 0);
    assert(EFS_ReceivePacket(packet, length) == 0U);
    assert(efs_receive_count == 1U && efs_received_command == 0xc5U);
    assert(efs_received_length == sizeof(complete));
    assert(memcmp(efs_received, complete, sizeof(complete)) == 0);
    assert(efs_receive_buffer == 0 && efs_total_rx == 0U);

    reset_state();
    efs_receive_buffer = malloc(OPEN_CFW_EFS_BUFFER_BYTES);
    assert(efs_receive_buffer != 0);
    length = make_packet(packet, 10U, 1U, 1U,
        OPEN_CFW_EFS_COMMAND_DATA, 0U, first, 2U, 1);
    packet[length - 1U] ^= 1U;
    assert(EFS_ReceivePacket(packet, length) == 1U);
    assert(efs_free_count == 1U && efs_receive_buffer == 0);
    assert(efs_crc_reply_count == 1U && efs_reply_command == 0xc5U);

    reset_state();
    assert(EFS_ReceivePacket(0, 0U) == 11U);
    memset(packet, 0, sizeof(packet));
    assert(EFS_ReceivePacket(packet, 7U) == 11U);
    packet[0] = 0x55U;
    assert(EFS_ReceivePacket(packet, 8U) == 10U);

    reset_state();
    for (index = 0U; index < sizeof(payload); ++index) {
        payload[index] = (uint8_t)(0x80U + index);
    }
    assert(EFS_SendPacket(1U, 3U, 0xc6U,
        payload, sizeof(payload)) == 0);
    assert(efs_transmit_count == 2U);
    assert(efs_transmitted_length[0] == 28U);
    assert(efs_transmitted_length[1] == 25U);
    assert(efs_transmitted[0][0] == 0xaaU);
    assert(efs_transmitted[0][1] == 0x32U);
    assert(efs_transmitted[0][2] == 0x78U);
    assert(efs_transmitted[0][3] == 20U);
    assert(efs_transmitted[0][4] == 2U && efs_transmitted[0][5] == 1U);
    assert(efs_transmitted[0][6] == 0xc6U && efs_transmitted[0][7] == 1U);
    assert(memcmp(efs_transmitted[0] + 8U, payload, 20U) == 0);
    assert(efs_transmitted[1][3] == 17U && efs_transmitted[1][5] == 2U);
    assert(memcmp(efs_transmitted[1] + 8U, payload + 20U, 15U) == 0);
    crc = efs_test_crc(payload, sizeof(payload), 0);
    assert(efs_transmitted[1][23] == (uint8_t)crc);
    assert(efs_transmitted[1][24] == (uint8_t)(crc >> 8));

    reset_state();
    efs_transmit_result = -6;
    assert(EFS_SendPacket(0U, 1U, 0xc4U, payload, 1U) == -6);
    assert(efs_transmit_count == 1U);
    assert(EFS_SendPacket(0U, 0U, 0U, 0, 1U) == 11);
    assert(EFS_SendPacket(0U, 0U, 0U, payload, 0U) == 11);

    reset_state();
    efs_default_receive_buffer = 0;
    length = make_packet(packet, 12U, 1U, 1U,
        OPEN_CFW_EFS_COMMAND_START, 0U, first, 1U, 1);
    first[0] = packet[8];
    packet[8] = 1U;
    crc = efs_test_crc(packet + 8U, 1U, 0);
    packet[9] = (uint8_t)crc;
    packet[10] = (uint8_t)(crc >> 8);
    assert(EFS_ReceivePacket(packet, length) == 4U);
    assert(efs_resource_reply_count == 1U);

    return 0;
}
