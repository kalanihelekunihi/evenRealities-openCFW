#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t rx_message[10];
static uint8_t tx_message[10];
static uint8_t encode_buffer[0x100];
static uint8_t decoded_message[10];
static uint8_t notify_sequence;
static uint32_t decode_result = 1U;
static uint32_t encode_result = 1U;
static uint32_t decode_calls;
static uint32_t encode_calls;
static uint32_t send_calls;
static uint32_t notify_calls;
static uint32_t transport_route;
static uint32_t transport_service;
static uint32_t transport_length;
static uint32_t battery = 71U;
static uint32_t charging = 2U;
static uint32_t lid = 3U;
static uint32_t present = 1U;

#define OPEN_CFW_PB_CASE_MESSAGE_RX rx_message
#define OPEN_CFW_PB_CASE_MESSAGE_TX tx_message
#define OPEN_CFW_PB_CASE_ENCODE_BUFFER encode_buffer
#define OPEN_CFW_PB_CASE_DESCRIPTOR ((const void *)0x1234U)
#define OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE (&notify_sequence)
#include "../../components/apollo_main/core_overlay/pb_service_glasses_case.c"

open_cfw_pb_case_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length)
{
    open_cfw_pb_case_input input = {0};
    input.state = (void *)data;
    input.bytes_left = length;
    return input;
}

uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_case_input *input, const void *descriptor, void *message)
{
    ++decode_calls;
    assert(input->state != (void *)0);
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
    open_cfw_pb_case_output *output = (open_cfw_pb_case_output *)raw_output;
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

static int record_transport(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    transport_route = route;
    transport_service = service;
    transport_length = length;
    assert(data == encode_buffer);
    return -7;
}

int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++send_calls;
    return record_transport(route, service, data, length);
}

int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++notify_calls;
    return record_transport(route, service, data, length);
}

uint32_t open_cfw_glasses_case_battery_get(void) { return battery; }
uint32_t open_cfw_glasses_case_charging_get(void) { return charging; }
uint32_t open_cfw_glasses_case_lid_get(void) { return lid; }
uint32_t open_cfw_glasses_case_present_get(void) { return present; }

static void reset_host(void)
{
    memset(rx_message, 0xA5, sizeof(rx_message));
    memset(tx_message, 0xA5, sizeof(tx_message));
    memset(encode_buffer, 0, sizeof(encode_buffer));
    memset(decoded_message, 0, sizeof(decoded_message));
    decode_result = encode_result = 1U;
    decode_calls = encode_calls = send_calls = notify_calls = 0U;
    transport_route = transport_service = transport_length = 0U;
    battery = 71U;
    charging = 2U;
    lid = 3U;
    present = 1U;
}

int main(void)
{
    open_cfw_pb_case_info info = {11U, 12U, 13U, 14U};
    open_cfw_pb_case_output output;
    uint8_t scratch[4] = {0};
    static const uint8_t sample[3] = {1U, 2U, 3U};

    output.write = open_cfw_pb_service_glasses_case_buffer_write;
    output.context = scratch;
    output.capacity = sizeof(scratch);
    output.length = 1U;
    output.error = (const char *)0;
    assert(output.write(&output, sample, 3U) == 1U);
    assert(memcmp(scratch + 1, sample, 3U) == 0);
    output.length = 2U;
    assert(output.write(&output, sample, 3U) == 0U);

    assert(PB_RxGlassesCaseInfo(7U, (const void *)0) == 2U);
    assert(PB_RxGlassesCaseInfo(7U, &info) == 0U);
    assert(APP_PbTxEncodeGlassesCaseInfo(1U, (const void *)0) == 2U);
    reset_host();
    assert(APP_PbTxEncodeGlassesCaseInfo(0xA6U, &info) == 0U);
    assert(tx_message[0] == 1U && tx_message[1] == 0xA6U);
    assert(tx_message[2] == 3U && tx_message[3] == 0U);
    assert(tx_message[4] == 71U && tx_message[5] == 2U);
    assert(tx_message[6] == 3U && tx_message[7] == 1U);
    assert(tx_message[8] == 0U && tx_message[9] == 0U);
    assert(send_calls == 1U && notify_calls == 0U);
    assert(transport_route == 1U && transport_service == 0x81U);
    assert(transport_length == 3U);

    reset_host();
    present = 9U;
    assert(APP_PbTxEncodeGlassesCaseInfo(2U, &info) == 0U);
    assert(tx_message[7] == 0U);
    reset_host();
    encode_result = 0U;
    assert(APP_PbTxEncodeGlassesCaseInfo(2U, &info) == 0x2BU);
    assert(send_calls == 0U);

    reset_host();
    notify_sequence = 0xFEU;
    assert(APP_PbNotifyEncodeGlassesCaseInfo(99U, &info) == 0U);
    assert(tx_message[1] == 0xFEU && notify_sequence == 0xFFU);
    assert(memcmp(tx_message + 4, &info, sizeof(info)) == 0);
    assert(notify_calls == 1U && send_calls == 0U);
    reset_host();
    notify_sequence = 0xFFU;
    encode_result = 0U;
    assert(APP_PbNotifyEncodeGlassesCaseInfo(0U, &info) == 0x2BU);
    assert(notify_sequence == 0U && notify_calls == 0U);
    assert(APP_PbNotifyEncodeGlassesCaseInfo(0U, (const void *)0) == 2U);

    reset_host();
    assert(APP_PbRxGlassesCaseFrameDataProcess((const void *)0, 3U) == 2U);
    decode_result = 0U;
    assert(APP_PbRxGlassesCaseFrameDataProcess(sample, 3U) == 0x2BU);
    reset_host();
    decoded_message[0] = 2U;
    assert(APP_PbRxGlassesCaseFrameDataProcess(sample, 3U) == 1U);
    reset_host();
    decoded_message[0] = 1U;
    decoded_message[1] = 0x55U;
    decoded_message[4] = 9U;
    assert(APP_PbRxGlassesCaseFrameDataProcess(sample, 3U) == 0U);
    assert(decode_calls == 1U && encode_calls == 1U && send_calls == 1U);
    assert(tx_message[1] == 0x55U);
    return 0;
}
