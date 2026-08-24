#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint8_t rx_message[0x40];
static uint8_t tx_message[0x40];
static uint8_t encode_buffer[0x100];
static uint8_t decoded_message[0x40];
static uint32_t decode_result = 1U;
static uint32_t encode_result = 1U;
static uint32_t decode_calls;
static uint32_t encode_calls;
static uint32_t send_calls;
static uint32_t send_route;
static uint32_t send_service;
static uint32_t send_length;
static uint32_t relay_rx_calls;

#define OPEN_CFW_PB_RING_MESSAGE_RX rx_message
#define OPEN_CFW_PB_RING_MESSAGE_TX tx_message
#define OPEN_CFW_PB_RING_ENCODE_BUFFER encode_buffer
#define OPEN_CFW_PB_RING_DESCRIPTOR ((const void *)0x1234U)
#include "../../components/apollo_main/core_overlay/pb_service_ring.c"

open_cfw_pb_ring_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length)
{
    open_cfw_pb_ring_input input = {0};
    input.state = (void *)data;
    input.bytes_left = length;
    return input;
}

uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_ring_input *input, const void *descriptor, void *message)
{
    ++decode_calls;
    assert(input->state != NULL);
    assert(descriptor == (const void *)0x1234U);
    if (decode_result == 0U) {
        input->error = "decode";
        return 0U;
    }
    memcpy(message, decoded_message, sizeof(decoded_message));
    return 1U;
}

uint32_t open_cfw_format_message_encode(
    void *raw_output, const void *descriptor, const void *message)
{
    open_cfw_pb_ring_output *output = (open_cfw_pb_ring_output *)raw_output;
    static const uint8_t encoded[] = {0xA1U, 0xB2U, 0xC3U};
    ++encode_calls;
    assert(descriptor == (const void *)0x1234U);
    assert(message == tx_message);
    if (encode_result == 0U) {
        output->error = "encode";
        return 0U;
    }
    assert(output->write(output, encoded, sizeof(encoded)) == 1U);
    output->length += sizeof(encoded);
    return 1U;
}

int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++send_calls;
    send_route = route;
    send_service = service;
    send_length = length;
    assert(data == encode_buffer);
    return -7;
}

static void reset_host(void)
{
    memset(rx_message, 0xA5, sizeof(rx_message));
    memset(tx_message, 0xA5, sizeof(tx_message));
    memset(encode_buffer, 0, sizeof(encode_buffer));
    memset(decoded_message, 0, sizeof(decoded_message));
    decode_result = encode_result = 1U;
    decode_calls = encode_calls = send_calls = 0U;
    send_route = send_service = send_length = 0U;
}

int main(void)
{
    open_cfw_pb_ring_event event = {0};
    open_cfw_pb_ring_output output;
    uint8_t scratch[4] = {0};
    static const uint8_t sample[3] = {1U, 2U, 3U};

    output.write = open_cfw_pb_service_ring_buffer_write;
    output.context = scratch;
    output.capacity = sizeof(scratch);
    output.length = 1U;
    output.error = NULL;
    assert(output.write(&output, sample, 3U) == 1U);
    assert(memcmp(scratch + 1, sample, 3U) == 0);
    output.length = 2U;
    assert(output.write(&output, sample, 3U) == 0U);

    assert(PB_RxRingEvent(7U, NULL) == 2U);
    event.event_id = 9U;
    assert(PB_RxRingEvent(7U, &event) == 0U);

    assert(APP_PbTxEncodeRingEvent(1U, NULL) == 2U);
    reset_host();
    event.mac_count = 6U;
    memcpy(event.mac, "ABCDEF", 6U);
    event.event_id = 1U;
    event.event_param = 0x78563412U;
    assert(APP_PbTxEncodeRingEvent(0xA6U, &event) == 0U);
    assert(tx_message[0] == 1U && tx_message[1] == 0xA6U);
    assert(tx_message[2] == 3U && tx_message[3] == 0U);
    assert(tx_message[4] == 6U && tx_message[5] == 0U);
    assert(memcmp(tx_message + 6, "ABCDEF", 6U) == 0);
    assert(tx_message[12] == 1U && tx_message[16] == 0x12U);
    assert(tx_message[19] == 0x78U && tx_message[20] == 0U);
    assert(send_calls == 1U && send_route == 1U && send_service == 0x91U);
    assert(send_length == 3U && encode_buffer[0] == 0xA1U);

    reset_host();
    event.mac_count = 7U;
    memset(event.mac, 0xCC, sizeof(event.mac));
    assert(APP_PbTxEncodeRingEvent(2U, &event) == 0U);
    assert(tx_message[4] == 7U && tx_message[6] == 0U);
    reset_host();
    encode_result = 0U;
    assert(APP_PbTxEncodeRingEvent(2U, &event) == 0x2BU);
    assert(send_calls == 0U);

    reset_host();
    assert(APP_PbRxRingFrameDataProcess(NULL, 3U) == 2U);
    decode_result = 0U;
    assert(APP_PbRxRingFrameDataProcess(sample, 3U) == 0x2BU);
    reset_host();
    decoded_message[0] = 2U;
    assert(APP_PbRxRingFrameDataProcess(sample, 3U) == 1U);
    reset_host();
    decoded_message[0] = 1U;
    decoded_message[1] = 0x55U;
    decoded_message[4] = 1U;
    decoded_message[6] = 0xDAU;
    decoded_message[12] = 1U;
    decoded_message[16] = 0x44U;
    assert(APP_PbRxRingFrameDataProcess(sample, 3U) == 0U);
    assert(decode_calls == 1U && encode_calls == 1U && send_calls == 1U);
    assert(tx_message[1] == 0x55U && tx_message[4] == 1U);
    assert(tx_message[6] == 0xDAU && tx_message[16] == 0x44U);

    reset_host();
    assert(RingDataRelay_common_data_handler(1U, sample, 3U) == 0U);
    assert(decode_calls == 0U);
    decoded_message[0] = 2U;
    assert(RingDataRelay_common_data_handler(0U, sample, 0x10003U) == 0U);
    assert(decode_calls == 1U);
    (void)relay_rx_calls;
    return 0;
}
